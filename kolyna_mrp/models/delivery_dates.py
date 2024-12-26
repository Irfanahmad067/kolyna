# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class DeliveryDates(models.Model):
    _name = 'delivery.dates'
    _description = 'Delivery Dates'

    date = fields.Date(string='Date')
    dog_expedition_id = fields.Many2one('dog.expedition', string='Sector')
    delivery_frequency = fields.Selection(
        string='Delivery frequency',
        selection=[('monthly', 'Monthly'), ('bi-monthy', 'Bi-monthly'), ('weekly', 'Weekly')], default='monthly')
