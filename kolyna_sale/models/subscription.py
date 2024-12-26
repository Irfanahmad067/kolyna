# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


# class SaleSubscription(models.Model):
#     _inherit = "sale.subscription"

#     def _prepare_invoice_line(self, line, fiscal_position):
#         res = super(SaleSubscription, self)._prepare_invoice_line(line, fiscal_position)
#         if line.product_id.id == self.env.ref('kolyna_sale.product_abonnement_mensuel').id:
#             dog_id = self.env['sale.order.line'].search([('subscription_id', '=', line.analytic_account_id.id)], limit=1).dog_id
#             if dog_id.amount:
#                 res['price_unit'] = dog_id.amount
#         return res
