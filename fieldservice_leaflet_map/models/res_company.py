# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    fsm_map_default_zoom = fields.Integer(
        string="Default Map Zoom",
        default=7,
        help="Initial zoom level when the Field Service map opens (1=world, 18=street).",
    )
    fsm_map_default_latitude = fields.Float(
        string="Default Map Latitude",
        default=52.1,
        digits=(10, 7),
        help="Map center latitude when no location is in view (NL default ~52.1).",
    )
    fsm_map_default_longitude = fields.Float(
        string="Default Map Longitude",
        default=5.3,
        digits=(10, 7),
        help="Map center longitude when no location is in view (NL default ~5.3).",
    )
    fsm_map_fit_bounds = fields.Boolean(
        string="Auto-fit Map to Locations",
        default=True,
        help="When on, the map auto-zooms to encompass all visible locations.",
    )
    fsm_map_auto_geocode = fields.Boolean(
        string="Auto-Geocode New Locations",
        default=True,
        help="Automatically run OpenStreetMap geocoding (Nominatim) on every "
        "Field Service location after create/write so the partner_latitude / "
        "partner_longitude fields get filled and the marker appears on the map.",
    )
