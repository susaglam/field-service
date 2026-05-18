# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""MCP / @ai_tool surface for the leaflet map / geocoding actions."""

from odoo import models
from odoo.addons.cs_mcp_bridge.tools import ai_tool


class FsmLocationMcp(models.Model):
    _inherit = "fsm.location"

    @ai_tool(
        name="fsm_map.geocode_location",
        description=(
            "Run OpenStreetMap (Nominatim) geocoding on a single FSM "
            "location, filling partner_latitude / partner_longitude. "
            "Idempotent — re-running on an already-geocoded location "
            "is a no-op."
        ),
        input_schema={
            "type": "object",
            "properties": {"location_id": {"type": "integer"}},
            "required": ["location_id"],
        },
        risk="low",
    )
    def action_mcp_geocode(self, location_id):
        loc = self.browse(location_id).exists()
        if not loc:
            return {"error": f"Location {location_id} not found"}
        partner = loc.partner_id
        if not partner:
            return {"error": "Location has no linked partner"}
        if partner.partner_latitude and partner.partner_longitude:
            return {
                "id": loc.id,
                "name": loc.display_name,
                "lat": partner.partner_latitude,
                "lng": partner.partner_longitude,
                "status": "already_geocoded",
            }
        try:
            partner.geo_localize()
        except Exception as e:
            return {"error": f"Geocoding failed: {e}"}
        return {
            "id": loc.id,
            "name": loc.display_name,
            "lat": partner.partner_latitude,
            "lng": partner.partner_longitude,
            "status": "geocoded",
        }

    @ai_tool(
        name="fsm_map.geocode_all",
        description=(
            "Run Nominatim geocoding on every FSM location lacking "
            "lat/lng. Bulk operation — returns count of locations "
            "processed and skipped. Slow on large datasets (1 req/sec "
            "Nominatim rate limit)."
        ),
        input_schema={"type": "object", "properties": {}},
        risk="high",
    )
    def action_mcp_geocode_all(self):
        partners = self.env["res.partner"].search(
            [
                ("fsm_location", "=", True),
                "|",
                ("partner_latitude", "=", 0),
                ("partner_latitude", "=", False),
            ]
        )
        if not partners:
            return {"processed": 0, "message": "All locations already geocoded."}
        partners.geo_localize()
        return {
            "processed": len(partners),
            "message": f"Geocoded {len(partners)} location(s).",
        }
