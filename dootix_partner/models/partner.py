# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    facebook_page = fields.Char("Facebook page")
    instagram_page = fields.Char("Instagram page")
    status_pickup = fields.Selection(string='Status pickup',
        selection=[('active', 'Active'), ('inactive', 'Inactive')], default='inactive')
    is_pickup = fields.Boolean(string='Is a pickup point', default=False, help="Check this box if this contact is a pickup point")
    is_prescriber = fields.Boolean(string='Is a prescriber', default=False, help="Check this box if this contact is a prescriber")
    freezer = fields.Integer("Freezer size")
    freezer_id = fields.Char("Freezer identification", help="If the freezer is provided by Kolyna")
    newsletter = fields.Boolean('Newsletter', default=True)
    prescriber = fields.Many2one("res.partner", string='Prescriber', ondelete='restrict', domain="[('is_prescriber', '=', True)]")
    dogs_count = fields.Integer(string='Dogs', compute='_dogs_count')
    dogs_prescribed = fields.Integer(string='Prescbribed dogs', compute='_dogs_prescribed')
    dogs_pickup = fields.Integer(string='Pickup dogs', compute='_dogs_pickup')

    def _dogs_count(self):
        dogs_data = self.env['res.dog'].read_group(domain=[('owner', 'in', self.ids)], fields=['owner'], groupby=['owner'])
        mapped_data = dict([(m['owner'][0], m['owner_count']) for m in dogs_data])
        for partner in self:
            partner.dogs_count = mapped_data.get(partner.id, 0)

    def _dogs_prescribed(self):
        for partner in self:
            total = 0
            prescribeds = self.env['res.partner'].search([('prescriber.id', '=', self.id)])
            for prescribed in prescribeds:
                total = total + prescribed.dogs_count
            self.dogs_prescribed = total

    def _dogs_pickup(self):
        for partner in self:
            pickups = self.env['res.dog'].search([('pickup_point.id', '=', self.id)])
            self.dogs_pickup = len(pickups)

    @api.onchange('is_prescriber', 'is_pickup')
    def onchange_is_prescriber(self):
        if self.is_prescriber == False:
            self.is_pickup = False
        if self.is_pickup == False:
            self.status_pickup = 'inactive'
