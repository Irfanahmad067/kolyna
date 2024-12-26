# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class DeliveryBox(models.Model):
    _name = 'delivery.box'
    _description = 'Delivery Box'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    expected_delivery_date = fields.Date(string='Expected Delivery Date')
    packaging_date = fields.Datetime(string='Packaging Date')
    delivery_date = fields.Datetime(string='Delivery Date')
    state = fields.Selection([('new', 'New'), ('packaged', 'Packaged'), ('delivered', 'Delivered')], default='new', track_visibility='onchange')
    ration_ids = fields.Many2many('mrp.production.plan.line', string='Rations')
    number_of_rations = fields.Integer(string='Number Of Rations')
    barcode = fields.Char(string='Barcode')
    dog_id = fields.Many2one('res.dog', string='Dog')
    delivery_address_id = fields.Many2one('res.partner', string='Delivery Address')

    def action_packaged(self):
        self.ensure_one()
        self.write({'state': 'packaged', 'packaging_date': fields.Datetime.now()})
        self.ration_ids.write({'packaging_date': fields.Datetime.now()})
        return True

    def action_delivered(self):
        self.ensure_one()
        self.write({'state': 'delivered', 'delivery_date': fields.Datetime.now()})
        self.ration_ids.write({'delivery_date': fields.Datetime.now()})
        self.dog_id.write({
            'ration_delivered': len(self.ration_ids),
            'customer_stock_last_delivery': self.dog_id.customer_stock_last_delivery + len(self.ration_ids),
            'last_delivery_date': fields.Date.today()
        })
        return True

    def action_new(self):
        self.ensure_one()
        self.write({'state': 'new', 'delivery_date': False, 'packaging_date': False})
        self.ration_ids.write({'delivery_date': False, 'packaging_date': False})
        return True

    def write(self, vals):
        if vals.get('state') in ['new', 'packaged']:
            for box in self.filtered(lambda s: s.state == 'delivered'):
                box.dog_id.write({
                    'ration_delivered': box.dog_id.ration_delivered - len(box.ration_ids),
                    'customer_stock_last_delivery': box.dog_id.customer_stock_last_delivery - len(box.ration_ids),
                    'last_delivery_date': fields.Date.today()})
        return super(DeliveryBox, self).write(vals)
