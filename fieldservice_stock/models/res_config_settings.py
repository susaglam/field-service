# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    fsm_auto_validate_pickings = fields.Boolean(
        related="company_id.fsm_auto_validate_pickings",
        readonly=False,
    )
