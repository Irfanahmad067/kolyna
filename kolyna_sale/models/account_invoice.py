# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    dog_id = fields.Many2one('res.dog', string='Dog')
