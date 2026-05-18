# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""MCP / @ai_tool surface for fsm.vehicle."""

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


class FsmVehicleMcp(models.Model):
    _inherit = "fsm.vehicle"

    @ai_tool(
        name="fsm_vehicle.search",
        description=(
            "Search Field Service vehicles by name or assigned driver. "
            "Returns id, name, assigned_driver."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "name_contains": {"type": "string"},
                "driver_id": {"type": "integer"},
                "limit": {"type": "integer", "default": 30},
            },
        },
        risk="low",
    )
    def action_mcp_search(self, name_contains=None, driver_id=None, limit=30):
        domain = []
        if name_contains:
            domain.append(("name", "ilike", name_contains))
        if driver_id:
            domain.append(("person_id", "=", driver_id))
        records = self.search(domain, limit=limit)
        return {
            "count": len(records),
            "vehicles": [
                {
                    "id": v.id,
                    "name": v.name,
                    "driver": v.person_id.name if v.person_id else None,
                }
                for v in records
            ],
        }

    @ai_tool(
        name="fsm_vehicle.create",
        description="Create a new FSM vehicle.",
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "person_id": {"type": "integer", "description": "Driver fsm.person id"},
            },
            "required": ["name"],
        },
        risk="medium",
    )
    def action_mcp_create(self, name, person_id=None):
        vals = {"name": name}
        if person_id:
            vals["person_id"] = person_id
        v = self.create(vals)
        return {"id": v.id, "name": v.name}
