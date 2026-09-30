# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    # Per company, like the other Field Service automation toggles on
    # res.company: one company may run its van stock through Odoo while a
    # sister company keeps validating transfers by hand.
    fsm_auto_validate_pickings = fields.Boolean(
        string="Validate Transfers on Order Completion",
        help="When a field service order is completed, validate its open "
        "delivery and return transfers in the same step, so stock reflects "
        "what the technician used. Completion is blocked with an explanation "
        "if a transfer lacks stock or needs a confirmation step. Example: the "
        "technician finishes a bathroom installation, the order is marked "
        "Completed and the 2 mixer taps on its delivery are booked out of the "
        "warehouse at the same moment.",
    )
