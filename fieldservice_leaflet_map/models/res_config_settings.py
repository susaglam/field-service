# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    fsm_map_default_zoom = fields.Integer(
        related="company_id.fsm_map_default_zoom", readonly=False,
    )
    fsm_map_default_latitude = fields.Float(
        related="company_id.fsm_map_default_latitude", readonly=False,
    )
    fsm_map_default_longitude = fields.Float(
        related="company_id.fsm_map_default_longitude", readonly=False,
    )
    fsm_map_fit_bounds = fields.Boolean(
        related="company_id.fsm_map_fit_bounds", readonly=False,
    )
    fsm_map_auto_geocode = fields.Boolean(
        related="company_id.fsm_map_auto_geocode", readonly=False,
    )

    def action_fsm_geocode_all_locations(self):
        partners = self.env["res.partner"].search(
            [
                ("fsm_location", "=", True),
                "|",
                ("partner_latitude", "=", 0),
                ("partner_latitude", "=", False),
            ]
        )
        if not partners:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Field Service Map",
                    "message": "All Field Service locations are already geocoded.",
                    "type": "info",
                },
            }
        partners.geo_localize()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Field Service Map",
                "message": f"Geocoded {len(partners)} location(s).",
                "type": "success",
                "next": {"type": "ir.actions.client", "tag": "soft_reload"},
            },
        }
