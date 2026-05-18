# Copyright (C) 2018 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # Was: related="group_id.fsm_order_id" — procurement.group removed in saas-19.3.
    # Now standalone; populated directly by callers (e.g. fieldservice_sale_stock).
    fsm_order_id = fields.Many2one(
        "fsm.order", string="Field Service Order", index=True, copy=False,
        help="Fsm Order Id. Linked record reference.",
    )
