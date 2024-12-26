# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, date, timedelta

import json
import copy

from odoo import http, _, fields
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class MRPProductionScheduler(http.Controller):

    def _set_matrix_data(self, matrix):
        request.env['ir.config_parameter'].sudo().set_param(
            'mrp.schedule.production.grid', matrix)

    def _get_matrix_data(self):
        return json.loads(request.env['ir.config_parameter'].sudo().get_param(
            'mrp.schedule.production.grid'))

    def _get_product_vals(self, matrix):
        res = {}
        for dog_id, values in list(matrix.items()):
            for product_id, qty in values.items():
                if qty < 1:
                    continue
                if product_id not in res:
                    res[product_id] = [(dog_id, qty)]
                else:
                    res[product_id].append((dog_id, qty))
        return res

    def _calculate_line_weight(self, bom_id, dog_id):
        weights = [False for _ in range(8)]
        dog_ration = request.env['res.dog'].browse(int(dog_id)).daily_ration_g
        Bom = request.env['mrp.bom'].browse(int(bom_id))
        # TODO : check conversion
        gram_uom = request.env['uom.uom'].search([
            ('name', '=', 'g')
        ])
        bom_weight = Bom.product_uom_id._compute_quantity(
            Bom.product_qty, gram_uom)
        for index, line in enumerate(bom_id.bom_line_ids):
            line_weight = line.product_uom_id._compute_quantity(
                line.product_qty, gram_uom)
            final_weight = round((dog_ration / bom_weight) * line_weight, 2)
            weights[index] = final_weight
        return weights

    @http.route('/mrp/production/schedule/data', type='json', auth='user')
    def get_production_schedule_grid_data(self, selected_group='all', selected_bag_size=None, selected_piece_size=None):
        res = {'dogs': [], 'products': [], 'selected_group': selected_group, 'selected_bag_size': selected_bag_size, 'selected_piece_size': selected_piece_size}
        res['dog_group'] = request.env['dog.group'].search_read([])
        res['bag_sizes'] = request.env['dog.bagsize'].search_read([])
        res['piece_sizes'] = request.env['dog.piecesize'].search_read([])

        matrix_data = self._get_matrix_data()
        matrix_data = {int(key): value for key, value in matrix_data.items()}
        dog_domain = [('state', 'not in', ['waiting', 'cancel'])]
        if selected_group != 'all':
            dog_domain += [('dog_group_id', 'in', selected_group)]

        if selected_bag_size:
            dog_domain += [('bag_size', '=', int(selected_bag_size))]

        if selected_piece_size:
            dog_domain += [('piece_size', '=', int(selected_piece_size))]

        dogs = request.env['res.dog'].search(dog_domain)
        offer_selection = dogs._fields['offer']._description_selection(request.env)
        category_id = request.env['product.category'].search([('name', '=', 'Menu')], limit=1).id
        products = request.env['product.product'].search(
            [('categ_id', '=', category_id)], order='name')
        for product in products:
            res['products'].append([product.id, product.display_name])

        for dog in dogs:
            offer = list(filter(lambda x: x[0] == dog.offer, offer_selection))
            offer = offer and offer[0] and offer[0][1] or ''
            owner = request.env['res.partner'].browse(dog.owner.id).display_name
            intolerances = ", ".join(intolerance.name for intolerance in dog.intolerances_ids)
            res['dogs'].append([dog.id, dog.name, offer, owner, intolerances, dog.daily_ration_g])
            if matrix_data.get(dog.id):
                # TODO  do it outside
                for product in products:
                    if not matrix_data[dog.id].get(str(product.id)):
                        matrix_data[dog.id][product.id] = 0

            if not matrix_data.get(dog.id):
                matrix_data[dog.id] = {}
                for product in products:
                    matrix_data[dog.id][product.id] = 0

        # clean up data on removal of dog or products
        matrix_copy = copy.deepcopy(matrix_data)
        for dog, value in matrix_data.items():
            if dog not in dogs.ids:
                matrix_copy.pop(dog)
                continue
            for product, val in value.items():
                if int(product) not in products.ids:
                    del matrix_copy[dog][product]

        matrix_copy_str = json.dumps(matrix_copy)
        self._set_matrix_data(matrix_copy_str)
        res['matrix'] = matrix_copy
        return res

    @http.route('/mrp/production/schedule/save/data', type='json', auth='user')
    def save_production_schedule_grid_datas(self, matrix, createmo=False):
        msg = ''
        try:
            if matrix:
                self._set_matrix_data(matrix)
                msg = _('Successfully Saved!')
            if createmo:
                matrix = self._get_matrix_data()
                vals = self._prepare_plan_line_vals(matrix)
                request.env['mrp.production.plan'].sudo().create(vals)
                mo_vals = self._prepare_manufacturing_order_vals(matrix)
                production_ids = request.env['mrp.production'].sudo().create(mo_vals)
                for production in production_ids:
                    production._onchange_move_raw()
                    production._create_update_move_finished()
                # Emptying matrix after creating a mo
                self._set_matrix_data({})
                msg = _("Production Plan and Manufacturing Order were \
                    created successfully!")
        except Exception:
            raise
        return msg

    def _prepare_plan_line_vals(self, matrix):
        vals = []
        ingredients = [False for _ in range(8)]
        weights = [False for _ in range(8)]
        ingredient_names = [False for _ in range(8)]
        line_number = 1
        for dog_id, values in list(matrix.items()):
            for product_id, qty in filter(
                    lambda res: res[1] > 0, list(values.items())):
                product = request.env[
                    'product.product'].browse(int(product_id))
                bom_id = request.env['mrp.bom'].search([
                    ('product_id', '=', product.id)
                ], limit=1)
                if not bom_id:
                    raise UserError(_(
                        "Can not find BoM for '%s' product!") % (product.name))

                components = bom_id.bom_line_ids.mapped('product_id')
                COMPONENT_IDS = components.ids
                display_names = components.mapped('display_name')
                weights = self._calculate_line_weight(bom_id, dog_id)

                for index, comp in enumerate(COMPONENT_IDS):
                    ingredients[index] = comp

                for index, name in enumerate(display_names):
                    ingredient_names[index] = name

                for index in range(qty):
                    vals.append((0, 0, {
                        'dog_id': int(dog_id),
                        'dog_name':request.env['res.dog'].browse(int(dog_id)).name,
                        'product_id': product_id,
                        'product_name':request.env['product.product'].browse(int(product_id)).display_name,
                        'ingredient_1': ingredients[0],
                        'ingredient_2': ingredients[1],
                        'ingredient_3': ingredients[2],
                        'ingredient_4': ingredients[3],
                        'ingredient_5': ingredients[4],
                        'ingredient_6': ingredients[5],
                        'ingredient_7': ingredients[6],
                        'ingredient_8': ingredients[7],
                        'ingredient_name_1': ingredient_names[0],
                        'ingredient_name_2': ingredient_names[1],
                        'ingredient_name_3': ingredient_names[2],
                        'ingredient_name_4': ingredient_names[3],
                        'ingredient_name_5': ingredient_names[4],
                        'ingredient_name_6': ingredient_names[5],
                        'ingredient_name_7': ingredient_names[6],
                        'ingredient_name_8': ingredient_names[7],
                        'ingredient_weight_1': weights[0],
                        'ingredient_weight_2': weights[1],
                        'ingredient_weight_3': weights[2],
                        'ingredient_weight_4': weights[3],
                        'ingredient_weight_5': weights[4],
                        'ingredient_weight_6': weights[5],
                        'ingredient_weight_7': weights[6],
                        'ingredient_weight_8': weights[7],
                    }))
                    line_number = line_number + 1

        return {
            'date': datetime.now(),
            'user_id': request.env.user.id,
            'plan_line_ids': vals
        }

    def _prepare_manufacturing_order_vals(self, matrix):
        vals = []
        res = self._get_product_vals(matrix)
        Production = request.env['mrp.production']
        picking_type_id = Production._get_default_picking_type()
        src_location = Production._get_default_location_src_id()
        dest_location = Production._get_default_location_dest_id()

        for product_id, dogs_data in list(res.items()):
            product = request.env['product.product'].browse(int(product_id))
            bom_id = request.env['mrp.bom'].search([
                ('product_id', '=', product.id)
            ], limit=1)
            if not bom_id:
                raise UserError(_(
                    "Can not find BoM for '%s' product!") % (product.name))
            total_weight = 0
            for (dog_id, qty) in dogs_data:
                total_weight = total_weight + (request.env['res.dog'].browse(int(dog_id)).daily_ration_g * qty)/1000

            #weight = request.env['res.dog'].browse(int(dog_id)).daily_ration_g

            vals.append({
                'product_id': product.id,
                'product_qty': total_weight,
                'product_uom_id': request.env.ref('uom.product_uom_kgm').id,
                'picking_type_id': picking_type_id,
                'location_src_id': src_location,
                'location_dest_id': dest_location,
                'bom_id': bom_id.id,
                'date_planned_start': datetime.now()
            })

        return vals

    @http.route('/mrp/production/rations/data', type='json', auth='user')
    def get_rations_data(self):
        dogs = request.env['res.dog'].search([('state', '!=', 'waiting')])
        DBox = request.env['delivery.box']
        start_date = date.today()
        end_date = start_date + timedelta(days=30)
        delta = end_date - start_date
        dogs_data = []
        days = []
        matrix_data = dict()

        for i in range(delta.days + 1):
            day = start_date + timedelta(days=i)
            days.append(day.strftime(DEFAULT_SERVER_DATE_FORMAT))

        for dog in dogs:
            dogs_data.append((dog.id, dog.name, dog.owner.display_name))
            matrix_data[dog.id] = {}
            qty = dog.customer_stock_last_delivery
            # locale en_GB is used to be able to obtain the datetime from the string returned by read_group
            # /!\ do not use en_US as it's not ISO-standard and does not match datetime's library
            box_data = DBox.with_context(lang='en_GB').read_group([
                ('state', 'in', ('new', 'packaged')),
                ('dog_id', '=', dog.id),
                ('expected_delivery_date', '>', start_date.strftime(DEFAULT_SERVER_DATE_FORMAT))
                ], ['number_of_rations', 'expected_delivery_date'], ['expected_delivery_date:day'])
            boxes = dict((datetime.strptime(data['expected_delivery_date:day'], "%d %b %Y").strftime(DEFAULT_SERVER_DATE_FORMAT), data['number_of_rations']) for data in box_data)
            for day in days:
                if qty < 0:
                    qty = 0
                if boxes.get(day):
                    qty = qty + boxes.get(day, 0)
                if qty > 0:
                    qty = qty - 1
                matrix_data[dog.id][day] = qty if qty > 0 else 0
        return {'dogs': dogs_data, 'days': days, 'matrix': matrix_data}

    @http.route('/mrp/production/rations/summary/data', type='json', auth='user')
    def get_rations_summary_data(self, selected_filter):
        dogs = request.env['res.dog'].search([('state', '!=', 'waiting')])
        deliveryDates = request.env['delivery.dates']
        ration = request.env['mrp.production.plan.line']
        dogs_data = []

        today = date.today()

        for dog in dogs:
            remaining_days = 0
            stockAtNextDD = 0
            stockAtNextDDBefore = 0
            freq_days = 0

            if dog.delivery_frequency == 'bi-monthy':
                freq_days = 14
            elif dog.delivery_frequency == 'monthly':
                freq_days = 28
            elif dog.delivery_frequency == 'weekly':
                freq_days = 7

            stockAtClient = dog.customer_stock_last_delivery
            nextDeliveryDate = deliveryDates.search([('dog_expedition_id', '=', dog.dog_expedition_id.id), ('delivery_frequency', '=', dog.delivery_frequency)], limit=1).date
            stockAtKolyna = ration.search_count([('dog_id', '=', dog.id), ('delivery_date', '=', False), '|', ('packaging_date', '!=', False), ('date', '!=', False)])
            if nextDeliveryDate:
                remaining_days = (nextDeliveryDate - today).days
                stockAtNextDDBefore = stockAtClient - remaining_days
                stockAtNextDD = max(0, stockAtNextDDBefore) + freq_days
            remainingRations = max(0, freq_days - stockAtKolyna)
            remainingDays = remaining_days if remainingRations > 0 else 0

            # apply Filters
            if ('ration_negative' in selected_filter and stockAtNextDDBefore > 0) or ('less_days_to_produce' in selected_filter and (remainingRations <= 0 or remainingDays >= 14)):
                continue

            column = dict(
                dogID=dog.id,
                dogName=dog.name,
                ownerName=dog.owner.name or 'N/A',
                firstDelivery='',
                expeditionGroup=dog.dog_expedition_id.name or 'N/A',
                deliveryFrequency=dog.delivery_frequency or 'N/A',
                stockAtKolyna=stockAtKolyna,
                stockAtClient=stockAtClient,
                nextDeliveryDate=nextDeliveryDate,
                stockAtNextDD=stockAtNextDD,
                remainingRations=remainingRations,
                remainingDays=remainingDays,
                stockAtNextDDBefore=stockAtNextDDBefore,
            )
            dogs_data.append(column)
        return {'dogs': dogs_data, 'selected_filter': selected_filter}
