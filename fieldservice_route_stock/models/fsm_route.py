# Copyright (C) 2019 Open Source Integrators
# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class FsmRoute(models.Model):
    _inherit = "fsm.route"

    max_product_id = fields.Many2one(
        "product.product",
        string="Max Capacity Product",
        domain="[('type', '=', 'product')]",
        help="The product whose quantity caps this route's day capacity. "
        "Typically matches the vehicle's capacity product (e.g. 'Water 19L "
        "bottle'). Day-routes will sum order quantities of this product and "
        "warn when the total exceeds the vehicle's max_product_qty.",
    )
    max_product_uom_id = fields.Many2one(
        "uom.uom",
        related="max_product_id.uom_id",
        string="UoM",
        store=True,
    )
    max_product_qty = fields.Float(
        string="Max Product Quantity",
        digits="Product Unit of Measure",
        help="Theoretical max capacity of the route across all assigned "
        "vehicles. Day-routes still validate per-vehicle capacity at the "
        "vehicle level.",
    )
