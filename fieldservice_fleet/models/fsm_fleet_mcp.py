# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""Minimal MCP / @ai_tool surface for fieldservice_fleet.

Exposes the fields this module adds to fsm.vehicle as one small read tool
so AI clients can fetch them without scraping the order_read payload.
"""

from odoo import models
try:
    from odoo.addons.cs_mcp_bridge.tools import ai_tool
except ImportError:
    # No-op fallback when cs_mcp_bridge is not installed.
    # AI/MCP surface unavailable; methods stay normal callable Python.
    def ai_tool(**_kwargs):
        def _decorator(fn):
            return fn
        return _decorator


class FieldserviceFleetMcp(models.Model):
    _inherit = "fsm.vehicle"

    @ai_tool(
        name="fsm_fleet.get_vehicle_details",
        description="Return fleet details (plate, fuel, odometer) for an FSM vehicle.",
        input_schema={
            "type": "object",
            "properties": {"vehicle_id": {"type": "integer"}},
            "required": ["vehicle_id"],
        },
        risk="low",
    )
    def action_mcp_read(self, vehicle_id):
        rec = self.browse(vehicle_id).exists()
        if not rec:
            return {"error": f"Record {vehicle_id} not found"}
        return {
            "id": rec.id,
            "name": rec.display_name,
            "fleet_vehicle_id": rec.fleet_vehicle_id.display_name if rec.fleet_vehicle_id else None,
            "license_plate": rec.license_plate,
            "fuel_type": rec.fuel_type,
            "odometer": rec.odometer,
            "is_fsm_vehicle": rec.is_fsm_vehicle,
        }
