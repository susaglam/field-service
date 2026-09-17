# Copyright (C) 2018 - TODAY, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMLocation(models.Model):
    _inherit = "fsm.location"

    inventory_location_id = fields.Many2one(
        "stock.location",
        string="Inventory Location",
        compute="_compute_inventory_location_id",
        store=True,
        readonly=False,
        required=True,
        recursive=True,
        default=lambda self: self.env.ref("stock.stock_location_customers"),
    )
    shipping_address_id = fields.Many2one(
        "res.partner",
        string="Shipping Location",
        help="Address that receives deliveries for this location when it is not "
        "the location itself, e.g. the site office that accepts parts for a "
        "building. For reference only: transfers do not use it automatically.",
    )

    @api.depends("parent_id", "parent_id.inventory_location_id")
    def _compute_inventory_location_id(self):
        for rec in self:
            if rec.parent_id:
                rec.inventory_location_id = rec.parent_id.inventory_location_id
