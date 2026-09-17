# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockReference(models.Model):
    _inherit = "stock.reference"

    fsm_order_ids = fields.Many2many(
        "fsm.order",
        "stock_reference_fsm_order_rel",
        "reference_id",
        "fsm_order_id",
        string="Field Service Orders",
        help="Field service orders that belong to this reference, e.g. the "
        "installation order created by the sale this reference groups.",
    )
