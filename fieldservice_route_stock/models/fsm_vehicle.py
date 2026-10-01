# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class FSMVehicle(models.Model):
    _inherit = "fsm.vehicle"

    inventory_location_id = fields.Many2one(
        "stock.location",
        string="Inventory Location",
        help="Stock location where this vehicle's on-board inventory lives. "
        "Used by the route-stock module to derive how much of the route's "
        "max product is loaded on the vehicle.",
    )
    max_product_id = fields.Many2one(
        "product.product",
        string="Max Capacity Product",
        domain="[('type', '=', 'product')]",
        help="The product whose vehicle capacity is tracked (e.g. 'Water 19L "
        "bottle'). Leave empty if this vehicle has no product cap.",
    )
    max_product_qty = fields.Float(
        string="Max Product Quantity",
        digits="Product Unit of Measure",
        help="Maximum quantity of the capacity product that fits on this "
        "vehicle. The route-stock module uses this to flag day-routes that "
        "would exceed the vehicle's load capacity.",
    )
