# Copyright (C) 2018 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # Was: related="group_id.fsm_order_id" — procurement.group removed in saas-19.3.
    # Now standalone; populated directly by callers (e.g. fieldservice_sale_stock).
    fsm_order_id = fields.Many2one(
        "fsm.order", string="Field Service Order", index=True, copy=False,
        help="Field service order this transfer supplies. Its lines are then "
        "listed on that order's Operations tab.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        pickings = super().create(vals_list)
        pickings.move_ids._fsm_link_to_picking_order()
        return pickings

    def write(self, vals):
        res = super().write(vals)
        if vals.get("fsm_order_id"):
            # Linking a transfer to an order brings its existing lines along
            self.move_ids._fsm_link_to_picking_order()
        return res
