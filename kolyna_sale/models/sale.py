# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    dog_id = fields.Many2one('res.dog', string='Dog')

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        res['dog_id'] = self.dog_id.id
        return res

    @api.onchange('dog_id')
    def onchange_dog_id(self):
        if self.dog_id:
            abonnement_product = self.env.ref('kolyna_sale.product_abonnement_mensuel')
            if self.product_id.id == abonnement_product.id:
                self.price_unit = self.dog_id.amount

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_price_unit(self):
        if self.dog_id and self.product_id.id == self.env.ref('kolyna_sale.product_abonnement_mensuel').id:
            self.price_unit = self.dog_id.amount
            self.technical_price_unit = self.dog_id.amount
        else:
            return super(SaleOrderLine, self)._compute_price_unit()

