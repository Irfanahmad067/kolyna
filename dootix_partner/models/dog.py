# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging
import math
from datetime import date

_logger = logging.getLogger(__name__)


class Intolerance(models.Model):
    _name = 'res.dog.intolerance'
    _description = 'Intolerance'
    _order = 'name'

    name = fields.Char(string='Name', index=True, translate=True)
    coefficient = fields.Float(string='Coefficient')


class Dog(models.Model):
    _name = 'res.dog'
    _description = 'Dog'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "name"

    name = fields.Char(string='Name', index=True, required=True)
    already_barf = fields.Boolean(string='Already fed using Barf method', tracking=True)
    breed = fields.Char(string='Breed')
    birth_date = fields.Date('Birthdate')
    age = fields.Integer("Age", compute='_compute_age')
    weight = fields.Float('Weight', digits=(5, 1), default=15, tracking=True)
    desired_ration = fields.Selection(string='Desired ration', selection=[('XL', 'Very big ration'), 
        ('L', 'Big ration'), 
        ('M', 'Standard ration'), 
        ('S', 'Small ration'), 
        ('XS', 'Very small ration')], default='M')
    daily_ration_g = fields.Float(string='Daily ration in grams', digits=(12, 2), tracking=True, required="True")
    daily_ration_kg = fields.Float(string='Daily ration in kilograms (archived)', digits=(12, 2), invisible=True)
    monthly_ration_kg = fields.Float(string='Monthly ration in kilograms (archived)', digits=(12, 2), tracking=True, invisible=True)
    kg_per_delivery = fields.Float(string='Kg per delivery (archived)', digits=(12, 2), invisible=True)
    offer = fields.Selection(string='Offer', selection=[('sp', 'Swiss Premium'), 
        ('p', 'Premium'), 
        ('s', 'Standard')], default='s', required=True, tracking=True)
    amount = fields.Integer(string='Monthly amount (archived)', tracking=True, invisible=True)
    remark = fields.Text(string='Remark', tracking=True)
    owner = fields.Many2one("res.partner", string='Owner', ondelete='restrict', tracking=True, domain="[('is_prescriber', '=', False)]")
    intolerances_ids = fields.Many2many('res.dog.intolerance', 'res_dog_intolerance_link', string="Intolerances", tracking=True)
    intolerances_others = fields.Char(string='Intolerances others', tracking=True)
    intolerances_others_description = fields.Text(string='Intolerances Description', compute='_compute_intolerance', store=True, tracking=True)
    delivery_mode = fields.Selection(string='Delivery mode', selection=[('home', 'At home'), 
        ('pickup', 'To a Babarf partner'), 
        ('warehouse', 'Pickup at warehouse')], default='pickup', tracking=True, required=True)
    delivery_frequency = fields.Selection(string='Delivery frequency (archived)',
        selection=[('monthly', 'Monthly'), ('bi-monthy', 'Bi-monthly'), ('weekly', 'Weekly')], default='monthly', tracking=True, invisible=True)
    pickup_point = fields.Many2one("res.partner", string='Pickup point', ondelete='restrict',
        domain="['&',('is_pickup', '=', True),('status_pickup', '=', 'active')]", tracking=True)
    discount_multiple_dogs = fields.Integer(string='Discount for multiple dogs (archived)', compute='_compute_discount')
    preorder_receipt_date = fields.Date(string='Pre-order date', required="True", tracking=True)
    has_others = fields.Boolean(string='Has others')
    dog_group_id = fields.Many2one('dog.group', string='Special recipes', tracking=True)
    customer_status = fields.Many2one('customer.status', string="Customer status", tracking=True)
    dog_expedition_id = fields.Many2one('dog.expedition', string='Sector', tracking=True)
    delivery_cycle = fields.Char(string="Delivery cycle", tracking=True)
    state = fields.Selection([('waiting', 'Waiting'), ('confirmed', 'Confirmed'), ('in_progress', 'In Progress'),('cancel','Cancelled')], default='waiting')
    species = fields.Selection([('dog','Dog'),('cat','Cat')], default='dog')
    piece_size = fields.Many2one('dog.piecesize', string='Piece size', invisible=True)
    bag_size = fields.Many2one('dog.bagsize', string='bag_size', tracking=True)
    delivery_address_street = fields.Char(string='Delivery Address street', compute='_compute_delivery_address_phone', store=True, tracking=True)
    delivery_address_street2 = fields.Char(string='Delivery Address street2', compute='_compute_delivery_address_phone', store=True, tracking=True)
    delivery_address_zip = fields.Char(string='Delivery Address zip', compute='_compute_delivery_address_phone', store=True, tracking=True)
    delivery_address_city = fields.Char(string='Delivery Address city', compute='_compute_delivery_address_phone', store=True, tracking=True)
    delivery_address_country_id = fields.Char(string='Delivery Address country', compute='_compute_delivery_address_phone', store=True, tracking=True)
    delivery_phone = fields.Char(string='Delivery Phone', compute='_compute_delivery_address_phone', store=True)
    delivery_info = fields.Char(string='Delivery information', tracking=True)
    delivery_date = fields.Date(string='Last delivery date (archived)', invisible=True)
    first_delivery_date = fields.Date(string="First delivery date", tracking=True)
    ration_delivered = fields.Float(string='Rations Recently Delivered (archived)', invisible=True)
    customer_stock_last_delivery = fields.Float(string='Customer Stock At Last Delivery (archived)', tracking=True, invisible=True)
    last_delivery_date = fields.Date(string='Last Delivery Date (archived)', tracking=True, invisible=True)
    price_liste = fields.Selection(string="Current price",
        selection=[('old-rates', 'Old rates'), ('new-rates', 'New rates')], default='new-rates', tracking=True, required=True)
    easybarf_customer = fields.Boolean(string="Easy-Barf customer", default=False)
    dog_rank = fields.Selection(string="Dog rang",
        selection=[('dog','Dog'),('dog-bis','Dog bis')], default="dog", tracking=True)
    broadcast_list_EB = fields.Boolean(string="Broadcast list EB", default=False, tracking=True)
    newsletter_testing_month = fields.Date(string="Relaunch - testing month", tracking=True)
    newsletter_healthy_food = fields.Date(string="Relaunch - healthy food", tracking=True)
    newsletter_faq = fields.Date(string="Relaunch - FAQ", tracking=True)
    life_stage = fields.Selection(string="Life stage",
        selection=[('puppy', 'Puppy'), ('adult', 'Adult')], default="adult", tracking=True, required=True)
    specific_menu = fields.Char(string="Ingredient choice feature", tracking=True)
    quote_date = fields.Date(string="Quote opening date", tracking=True)
    order_confirmation_date = fields.Date(string="Order confirmation date", tracking=True)
    starter1 = fields.Integer(string="Week 1", tracking=True)
    starter2 = fields.Integer(string="Week 2", tracking=True)
    starter3 = fields.Integer(string="Week 3", tracking=True)
    starter4 = fields.Integer(string="Week 4", tracking=True)
    starter5 = fields.Integer(string="Week 5", tracking=True)
    starter6 = fields.Integer(string="Week 6", tracking=True)
    starter7 = fields.Integer(string="Week 7", tracking=True)
    starter8 = fields.Integer(string="Week 8", tracking=True)
    newsletter_no_relaunch = fields.Boolean(string="Don't relaunch", tracking=True)
    newsletter_puppy_price_drop = fields.Date(string="Newsletter - price drop", tracking=True)
    newsletter_puppy_birthday = fields.Date(string="Newsletter - growth completed", tracking=True)
    remark_puppy = fields.Text(string="Remark about growth", tracking=True)
    starting_percentage = fields.Float(string="Starting percentage", tracking=True, default=12)
    initial_puppy_weight = fields.Float(string="Initial puppy weight", tracking=True)
    last_weight_puppy = fields.Float(string="Last know weight", tracking=True)
    growth_average_ration = fields.Integer(string="Average ration during growth", tracking=True)
    date_update_puppy = fields.Date(string="Date update puppy", tracking=True)
    rations_1_month = fields.Integer(string="Rations 1 month", tracking=True)
    rations_2_month = fields.Integer(string="Rations 2 month", tracking=True)
    rations_3_month = fields.Integer(string="Rations 3 month", tracking=True)
    rations_4_month = fields.Integer(string="Rations 4 month", tracking=True)
    rations_5_month = fields.Integer(string="Rations 5 month", tracking=True)
    rations_6_month = fields.Integer(string="Rations 6 month", tracking=True)
    rations_7_month = fields.Integer(string="Rations 7 month", tracking=True)
    rations_8_month = fields.Integer(string="Rations 8 month", tracking=True)
    rations_9_month = fields.Integer(string="Rations 9 month", tracking=True)
    rations_10_month = fields.Integer(string="Rations 10 month", tracking=True)
    rations_11_month = fields.Integer(string="Rations 11 month", tracking=True)
    rations_12_month = fields.Integer(string="Rations 12 month", tracking=True)
    mensual_amount = fields.Integer(string="Mensual amount", help="Amount corresponding to consumption and deliveries for a period of one month", tracking=True, required=True)
    meals_per_month = fields.Integer(string="Meals per month", tracking=True, required=True, default=28)
    order_type = fields.Selection(string="Order type",
        selection=[('subscription', 'Subscription'),('occasional-orders', "Occasional orders")], tracking=True, required=True)
    bag_type = fields.Selection(string="Type of bag(s)",
        selection=[('daily-rations', 'Daily rations'),('1-sachet-for-2-days', '1 sachet for 2 days'),('2-sachets-per-day', '2 sachets per day')], tracking=True, required=True, default="daily-rations")
    frequency_of_deliveries = fields.Selection(string="Frequency of deliveries", selection=[('weekly', 'Weekly'),
        ('bimonthly', 'Bimonthly'),
        ('monthly', 'Monthly'),
        ('bimestrial', 'Bimestrial')], default="monthly", tracking=True, required=True)
    specific_ingredients = fields.Selection(string="Specific ingredients", selection=[('mix-without-oil', 'Mix without oil'),
        ('mix-with-oil', 'Mix with oil'),
        ('boneless', 'Boneless'),
        ('without-mix', 'Without mix'),
        ('without-bone-or-mix', 'Whitout bone or mix'),
        ('bulk-rations', 'Bulk rations'),
        ('uncrushed-necks', 'Uncrushed necks'),
        ('other-specificity', 'Other specificity')], tracking=True)
    specific_ingredients_other = fields.Char(string="Other specific ingredient", tracking=True)
    type_of_rations = fields.Selection(string="Type of rations to be produced",
        selection=[('starter-kit', 'Starter Kit'), ('full-menus', 'Full menus')], tracking=True, readonly=True)
    meat_size = fields.Selection(string="Piece size", selection=[('1-L','1 - L'),
        ('2-L-crushed-bones','2 - L - crushed bones'),
        ('3-XS-crushed-bones','3 - XS - crushed bones'),
        ('4-S-crushed-bones','4 - S - crushed bones'),
        ('5-S','5 - S')], tracking=True)
    puppy_calculation_basis = fields.Selection(string="Puppy calculation basis",
        selection=[('average', 'Average ration'),('maximum', 'Maximum ration')], tracking=True, default='average')
    discount_bidaily_bag = fields.Selection(string="Discount bi-daily bag", selection=[('without-reduction', 'Without reduction'), 
        ('20-chf-discount', '20 chf discount'), 
        ('division-by-2', 'Division by 2')], tracking=True, default='without-reduction')
    postal_delivery_fee = fields.Selection(string="Postal delivery fee",
        selection=[('invoiced','Invoiced'), ('not-billed', 'Not billed')], tracking=True, default='not-billed')
    delivery_frequency_invoiced = fields.Selection(string="Delivery frequency invoiced",
        selection=[('effective', 'Same as the effective frequency'), ('bi-monthly', 'Bi-monthly billed')], tracking=True, default='effective')
    billing_frequency = fields.Selection(string="Billing frequency",
        selection=[('monthly', 'Monthly'), ('bimestrial', 'Bimestrial'), ('other', 'Other')], tracking=True, default='monthly')
    remark_billing = fields.Text(string="Remark billing", tracking=True)
    rations_count = fields.Integer(compute='compute_ration_counts')

    @api.model
    def create(self, vals):
        res = super(Dog, self).create(vals)
        if res.owner:
            res.message_subscribe(res.owner.ids)
        return res

    def compute_ration_counts(self):
        for record in self:
            record.rations_count = self.env['mrp.production.plan.line'].search_count([('dog_id', '=', self.id)])

    @api.depends('intolerances_ids', 'intolerances_others')
    def _compute_intolerance(self):
        for record in self:
            intolerance_desc = ''
            if record.intolerances_ids:
                intolerance_desc += ', '.join(map(lambda x: x.name, record.intolerances_ids))
            if record.intolerances_others:
                intolerance_desc += ' ' + record.intolerances_others
            record.intolerances_others_description = intolerance_desc

    @api.depends('owner', 'delivery_mode', 'pickup_point')
    def _compute_delivery_address_phone(self):
        for record in self:
            if record.delivery_mode == 'home' and record.owner:
                partner = record.owner
                partner_ids = record.owner.child_ids.filtered(lambda l: l.type == 'delivery')
                if partner_ids:
                    partner = partner_ids and partner_ids[0]
                record.delivery_address_street = partner.street
                record.delivery_address_street2 = partner.street2
                record.delivery_address_zip = partner.zip
                record.delivery_address_city = partner.city
                record.delivery_address_country_id = partner.country_id and partner.country_id.name or ''
                record.delivery_phone = partner.phone
            elif record.delivery_mode == 'pickup' and record.pickup_point:
                    record.delivery_address_street = record.pickup_point.street
                    record.delivery_address_street2 = record.pickup_point.street2
                    record.delivery_address_zip = record.pickup_point.zip
                    record.delivery_address_city = record.pickup_point.city
                    record.delivery_address_country_id = record.pickup_point.country_id and record.pickup_point.country_id.name or ''
                    record.delivery_phone = record.pickup_point.phone
            elif record.delivery_mode == 'warehouse' and record.pickup_point:
                record.delivery_address_street = record.pickup_point.name
            else:
                record.delivery_address_street = None
                record.delivery_address_street2 = None
                record.delivery_address_zip = None
                record.delivery_address_city = None
                record.delivery_address_country_id = None
                record.delivery_phone = None

    def _compute_discount(self):
        self.discount_multiple_dogs = 0
        # if self.owner.dogs_count > 1:
        #     list_dogs = self.env['res.dog'].search(
        #         [('owner.id', '=', self.owner.id)], order='create_date ASC', limit=1)
        #     for dog in list_dogs:
        #         if dog.id != self.id:
        #             self.discount_multiple_dogs = 8

    def _compute_age(self):
        today = date.today()
        if self.birth_date:
            self.age = today.year - self.birth_date.year - \
                ((today.month, today.day) <
                 (self.birth_date.month, self.birth_date.day))
        else:
            self.age = ''

    @api.onchange('intolerances_ids')
    def onchange_intolerances(self):
        selected_ids = self.intolerances_ids
        self.has_others = False
        for record in self.intolerances_ids:
            if record.id == 7:
                self.has_others = True

    @api.onchange('weight', 'desired_ration')
    def onchange_ration(self):
        coefficient = 0
        if self.desired_ration == 'XL':
            coefficient = 4.25
        elif self.desired_ration == 'L':
            coefficient = 3.25
        elif self.desired_ration == 'M':
            coefficient = 2.75
        elif self.desired_ration == 'S':
            coefficient = 2.25
        else:
            coefficient = 1.25
        self.daily_ration_g = self.weight * coefficient * 10

    @api.onchange('daily_ration_g')
    def onchange_ration_g(self):
        self.daily_ration_kg = self.daily_ration_g / 1000
        self.monthly_ration_kg = self.daily_ration_kg * 30.4

    def get_correct_price(self):
        self.ensure_one()
        self.daily_ration_kg = self.daily_ration_g / 1000
        self.monthly_ration_kg = self.daily_ration_kg * 30.4
        price_per_offer = 0
        if self.offer == 'sp':
            price_per_offer = 9.17
        elif self.offer == 'p':
            price_per_offer = 4.47
        else:
            price_per_offer = 4.47

        if len(self.intolerances_ids) > 0:
            if self.offer == 'sp':
                price_per_offer = 10.37
            elif self.offer == 'p':
                price_per_offer = 5.67
            else:
                price_per_offer = 4.47

        price_per_dog = 70.56  # J

        delivery_cost = 0

        coefficient_delivery = 0.8 + price_per_offer

        if self.delivery_mode == 'home':
            base = 13.5
        else:
            base = 8.5

        base = base - self.discount_multiple_dogs

        if self.delivery_frequency == 'weekly':
            delivery_cost = base * 4
        elif self.delivery_frequency == 'monthly':
            delivery_cost = base
        else:
            delivery_cost = base * 2
        return math.ceil(coefficient_delivery*self.monthly_ration_kg + delivery_cost + price_per_dog)

    @api.onchange('owner', 'offer', 'monthly_ration_kg', 'daily_ration_g', 'intolerances_ids', 'delivery_mode', 'delivery_frequency')
    def onchange_amount(self):
        if self.delivery_frequency == 'monthly':
            coefficient = 1
        elif self.delivery_frequency == 'bi-monthy':
            coefficient = 2
        else:
            coefficient = 3
        self.kg_per_delivery = self.monthly_ration_kg / coefficient
        if self.offer == 's':
            self.intolerances_ids = []
        self._compute_discount()
        self.amount = self.get_correct_price()

    @api.model
    def consume_ration(self):
        # this method is call from schedule action
        # TODO : probably we can log note, so that user can able to tracke when it was last consume
        dogs = self.env['res.dog'].search([('customer_stock_last_delivery', '>', 0)])
        for record_dog in dogs:
            record_dog.customer_stock_last_delivery -= 1

    def action_view_rations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Rations',
            'view_mode': 'tree',
            'res_model': 'mrp.production.plan.line',
            'domain': [('dog_id', '=', self.id)],
            'context': "{'create': False}"
        }


class DogGroup(models.Model):
    _name = 'dog.group'
    _description = 'Dog Group'

    name = fields.Char()


class ExpeditionGroup(models.Model):
    _name = 'dog.expedition'
    _description = 'Dog Expedition Group'
    
    name = fields.Char()


class BagSize(models.Model):
    _name = 'dog.bagsize'
    _description = 'Dog Bag Size'
    
    name = fields.Char()


class PieceSize(models.Model):
    _name = 'dog.piecesize'
    _description = 'Dog Piece Size'
    
    name = fields.Char()


class CustomerStatus(models.Model):
    _name = 'customer.status'
    _description = 'Customer Status'
    
    name = fields.Char()
