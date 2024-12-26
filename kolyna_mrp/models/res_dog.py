# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import date

from odoo import api, fields, models


class ResDog(models.Model):
    _inherit = 'res.dog'

    first_date = fields.Datetime(string='First Date', compute='_compute_first_date', store=True)
    kolyna_stock = fields.Integer(string='Kolyna Stock', compute='_compute_next_delivery_info', store=True)
    next_delivery_date = fields.Date(string='Next Delivery Date', compute='_compute_next_delivery_info', store=True)
    next_delivery_stock = fields.Integer(string='Next Delivery Stock', compute='_compute_next_delivery_info', store=True)
    stock_before_next_delivery = fields.Integer(string='Stock Before Next Delivery', compute='_compute_next_delivery_info', store=True)
    days_left = fields.Integer(string='Days Left', compute='_compute_next_delivery_info', store=True)
    box_ids = fields.One2many('delivery.box', 'dog_id')
    ration_ids = fields.One2many('mrp.production.plan.line', 'dog_id')

    @api.depends('box_ids.state', 'box_ids.delivery_date', 'box_ids.dog_id')
    def _compute_first_date(self):
        Box = self.env['delivery.box']
        for dog in self:
            dog.first_date = Box.search([('dog_id', '=', dog.id), ('state', '=', 'delivered')], order='delivery_date desc', limit=1).delivery_date

    @api.depends(
        'ration_ids.dog_id', 'ration_ids.delivery_date', 'ration_ids.packaging_date', 'ration_ids.date',
        'customer_stock_last_delivery', 'box_ids.state', 'box_ids.delivery_date', 'box_ids.expected_delivery_date',
        'box_ids.number_of_rations', 'box_ids.dog_id')
    def _compute_next_delivery_info(self):
        ration = self.env['mrp.production.plan.line']
        deliveryBox = self.env['delivery.box']
        today = date.today()
        for dog in self:
            stockAtNextDD = 0
            remaining_days = 0
            stockAtNextDDBefore = 0
            stockAtKolyna = ration.search_count([('dog_id', '=', dog.id), ('delivery_date', '=', False), '|', ('packaging_date', '!=', False), ('date', '!=', False)])
            box = deliveryBox.search([('dog_id', '=', dog.id), ('state', '!=', 'delivered')], limit=1, order='expected_delivery_date desc')
            nextDeliveryDate = box.expected_delivery_date
            freq_days = 0

            if dog.delivery_frequency == 'bi-monthy':
                freq_days = 14
            elif dog.delivery_frequency == 'monthly':
                freq_days = 28
            elif dog.delivery_frequency == 'weekly':
                freq_days = 7

            if nextDeliveryDate:
                remaining_days = (nextDeliveryDate - today).days
                stockAtNextDDBefore = (dog.customer_stock_last_delivery + box.number_of_rations) - remaining_days
                stockAtNextDD = (stockAtKolyna + box.number_of_rations) - remaining_days

            remainingRations = max(0, freq_days - stockAtKolyna)
            remainingDays = remaining_days if remainingRations > 0 else 0
            dog.next_delivery_date = nextDeliveryDate
            dog.next_delivery_stock = stockAtNextDD
            dog.stock_before_next_delivery = stockAtNextDDBefore
            dog.days_left = remainingDays
            dog.kolyna_stock = stockAtKolyna
