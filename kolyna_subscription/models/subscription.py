# -- coding: utf-8 --

from odoo import fields, models,_
from dateutil.relativedelta import relativedelta
from odoo.tools import format_date

class SaleSubscription(models.Model):
    _inherit = "sale.subscription"
    
    # payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms')
    dog_ids = fields.Many2many('res.dog', string='Chien(s)')

    def _prepare_invoice_data(self):
        vals = super()._prepare_invoice_data()
        # vals['payment_term_id'] = self.payment_term_id.id
        next_date = fields.Date.from_string(self.recurring_next_date)
        periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
        end_date = next_date + relativedelta(**{periods[self.recurring_rule_type]: self.recurring_interval})
        narration = _("This invoice covers the following period: %s - %s") % (format_date(self.env, next_date + relativedelta(months=1)), format_date(self.env, end_date + relativedelta(months=1) - relativedelta(days=1)))
        vals['narration'] = narration
        if self.dog_ids:
            vals['dog_ids'] = self.dog_ids
        return vals
