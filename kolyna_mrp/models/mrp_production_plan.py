# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class MrpProductionPlan(models.Model):
    _name = "mrp.production.plan"
    _description = "Production Plan"
    _rec_name = "user_id"
    _order = "date desc"

    date = fields.Datetime(string="Date", default=fields.Datetime.now())
    user_id = fields.Many2one("res.users", string="Created By")
    plan_line_ids = fields.One2many(
        "mrp.production.plan.line", "plan_id", string="Lines")


class MrpProductionPlanLine(models.Model):
    _name = "mrp.production.plan.line"
    _inherit = ['mail.thread']
    _description = "Production Plan Lines"
    _rec_name = "product_id"
    _order = "create_date desc"

    plan_id = fields.Many2one("mrp.production.plan", string="Plan")
    dog_id = fields.Many2one("res.dog", string="Dog", track_visibility='onchange')
    dog_name = fields.Char(string="Name")
    total_weight = fields.Float(
        related="dog_id.daily_ration_g", string="Total Weight", store=True)
    product_id = fields.Many2one("product.product", string="Product", track_visibility='onchange')
    product_name = fields.Char(string="Product name")
    ingredient_1 = fields.Many2one("product.product", string="Ingredient 1")
    ingredient_2 = fields.Many2one("product.product", string="Ingredient 2")
    ingredient_3 = fields.Many2one("product.product", string="Ingredient 3")
    ingredient_4 = fields.Many2one("product.product", string="Ingredient 4")
    ingredient_5 = fields.Many2one("product.product", string="Ingredient 5")
    ingredient_6 = fields.Many2one("product.product", string="Ingredient 6")
    ingredient_7 = fields.Many2one("product.product", string="Ingredient 7")
    ingredient_8 = fields.Many2one("product.product", string="Ingredient 8")
    ingredient_name_1 = fields.Char(string="Ingredient Name 1")
    ingredient_name_2 = fields.Char(string="Ingredient Name 2")
    ingredient_name_3 = fields.Char(string="Ingredient Name 3")
    ingredient_name_4 = fields.Char(string="Ingredient Name 4")
    ingredient_name_5 = fields.Char(string="Ingredient Name 5")
    ingredient_name_6 = fields.Char(string="Ingredient Name 6")
    ingredient_name_7 = fields.Char(string="Ingredient Name 7")
    ingredient_name_8 = fields.Char(string="Ingredient Name 8")
    ingredient_weight_1 = fields.Float(string="Weight 1")
    ingredient_weight_2 = fields.Float(string="Weight 2")
    ingredient_weight_3 = fields.Float(string="Weight 3")
    ingredient_weight_4 = fields.Float(string="Weight 4")
    ingredient_weight_5 = fields.Float(string="Weight 5")
    ingredient_weight_6 = fields.Float(string="Weight 6")
    ingredient_weight_7 = fields.Float(string="Weight 7")
    ingredient_weight_8 = fields.Float(string="Weight 8")
    real_weight_1 = fields.Float(string="Real Weight 1")
    real_weight_2 = fields.Float(string="Real Weight 2")
    real_weight_3 = fields.Float(string="Real Weight 3")
    real_weight_4 = fields.Float(string="Real Weight 4")
    real_weight_5 = fields.Float(string="Real Weight 5")
    real_weight_6 = fields.Float(string="Real Weight 6")
    real_weight_7 = fields.Float(string="Real Weight 7")
    real_weight_8 = fields.Float(string="Real Weight 8")
    real_total_weight = fields.Float(string="Real Total Weight")
    note_1 = fields.Text(string="Note 1")
    note_2 = fields.Text(string="Note 2")
    note_3 = fields.Text(string="Note 3")
    note_4 = fields.Text(string="Note 4")
    note_5 = fields.Text(string="Note 5")
    note_6 = fields.Text(string="Note 6")
    note_7 = fields.Text(string="Note 7")
    note_8 = fields.Text(string="Note 8")

    lot_id = fields.Char(string="Lot")
    date = fields.Date(string="Production Date")

    lot_1 = fields.Many2one("stock.production.lot", string="LOT 1")
    lot_2 = fields.Many2one("stock.production.lot", string="LOT 2")
    lot_3 = fields.Many2one("stock.production.lot", string="LOT 3")
    lot_4 = fields.Many2one("stock.production.lot", string="LOT 4")
    lot_5 = fields.Many2one("stock.production.lot", string="LOT 5")
    lot_6 = fields.Many2one("stock.production.lot", string="LOT 6")
    lot_7 = fields.Many2one("stock.production.lot", string="LOT 7")
    lot_8 = fields.Many2one("stock.production.lot", string="LOT 8")

    packaging_date = fields.Datetime(string='Packaging Date')
    delivery_date = fields.Datetime(string='Delivery Date')
