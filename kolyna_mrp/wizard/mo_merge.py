# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime
import logging

from odoo import models, api, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger('base.partner.merge')


class MergeProductionOrder(models.TransientModel):
    _name = 'merge.production.order'
    _description = 'Merge Production Order'

    @api.model
    def default_get(self, fields):
        res = super(MergeProductionOrder, self).default_get(fields)
        active_ids = self.env.context.get('active_ids')
        if self.env.context.get('active_model') == 'mrp.production' and active_ids:
            production_ids = self.env['mrp.production'].browse(active_ids)
            res['production_order_ids'] = production_ids
            res['dst_production_order_id'] = self._get_ordered_mo(active_ids)[-1].id
        return res

    dst_production_order_id = fields.Many2one('mrp.production', string='Destination Production Order', required=True)
    production_order_ids = fields.Many2many('mrp.production', string='Production Orders', required=True)

    @api.model
    def _get_ordered_mo(self, order_ids):
        """ Helper : returns a `mrp.production` recordset ordered by id/create_date fields
            :param order_ids : list of mo ids to sort
        """
        return self.env['mrp.production'].browse(order_ids).sorted(
            key=lambda m: ((m.create_date or datetime.datetime(1970, 1, 1), m.id)),
            reverse=True,
        )

    def action_merge(self):
        """
            for this customer we, only merge the quantity, no other field will change of destination manufacturing order
        """
        self.ensure_one()
        src_order_ids = self.production_order_ids.filtered(lambda o: o.id != self.dst_production_order_id.id)
        # Validation before merge
        self._merge_order_validation()
        self._merge_order()
        self._log_merge_operation(src_order_ids, self.dst_production_order_id)

        # delete merged orders
        src_order_ids.action_cancel()
        src_order_ids.unlink()

    def _merge_order_validation(self):
        if len(self.production_order_ids) < 2:
            raise UserError(_('You must have atleast two manufacturing order selected in order to merge'))

        if any(o.product_id != self.dst_production_order_id.product_id for o in self.production_order_ids):
            raise UserError(_('All selected manufacturing order must have same product!'))

        if any(o.product_uom_id != self.dst_production_order_id.product_uom_id for o in self.production_order_ids):
            raise UserError(_('All selected manufacturing order must have same product unit of measure!'))

        if any(o.state != 'confirmed' for o in self.production_order_ids):
            raise UserError(_('All selected manufacturing order must be on confirmed state'))

        if any(o.bom_id != self.dst_production_order_id.bom_id for o in self.production_order_ids):
            raise UserError(_('All selected manufacturing order must have same bill of material!'))

    def _merge_order(self):
        qty = self.dst_production_order_id.product_qty
        for mo in self.production_order_ids.filtered(lambda o: o.id != self.dst_production_order_id.id):
            qty += mo.product_qty

        wizard = self.env['change.production.qty'].create({'mo_id': self.dst_production_order_id.id, 'product_qty': qty})
        wizard.change_prod_qty()

    def _log_merge_operation(self, src_orders, dst_order):
        _logger.info('(uid = %s) merged the manufacturing orders %r with %s', self._uid, src_orders.ids, dst_order.id)
        dst_order.message_post(body='%s %s' % (_("Merged with the following manufacturing order:"), ", ".join('%s <%s> (ID %s)' % (o.name, o.product_qty or 'n/a', o.id) for o in src_orders)))
