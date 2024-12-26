# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class DeleteProductionOrder(models.TransientModel):
    _name = 'delete.production.order'
    _description = 'Delete Production Order'

    @api.model
    def default_get(self, fields):
        res = super(DeleteProductionOrder, self).default_get(fields)
        active_ids = self.env.context.get('active_ids')
        if self.env.context.get('active_model') == 'mrp.production' and active_ids:
            production_ids = self.env['mrp.production'].browse(active_ids)
            res['production_order_ids'] = production_ids
        return res

    production_order_ids = fields.Many2many('mrp.production', string='Production Orders', required=True)

    def action_delete(self):
        self.ensure_one()
        # delete orders
        if any(o.state not in ['confirmed', 'planned', 'cancel', 'draft'] for o in self.production_order_ids):
            raise UserError(_('You can not delete order which are in state Done/Inprogress'))
        self.production_order_ids.action_cancel()
        self.production_order_ids.unlink()
