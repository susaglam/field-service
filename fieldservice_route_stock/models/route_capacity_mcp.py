# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""MCP / @ai_tool surface for route-stock capacity checks."""

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


class FsmRouteDayrouteCapacityMcp(models.Model):
    _inherit = "fsm.route.dayroute"

    @ai_tool(
        name="route_stock.capacity_check",
        description=(
            "Inspect a day-route's vehicle capacity utilization for the "
            "route's max product. Returns used qty, remaining qty, "
            "vehicle max, and whether the day-route is over-capacity."
        ),
        input_schema={
            "type": "object",
            "properties": {"dayroute_id": {"type": "integer"}},
            "required": ["dayroute_id"],
        },
        risk="low",
    )
    def action_mcp_capacity(self, dayroute_id):
        dr = self.browse(dayroute_id).exists()
        if not dr:
            return {"error": f"Day route {dayroute_id} not found"}
        return {
            "id": dr.id,
            "name": dr.name,
            "vehicle": dr.fsm_vehicle_id.name if dr.fsm_vehicle_id else None,
            "max_product": dr.max_product_id.display_name
            if dr.max_product_id
            else None,
            "is_limited": dr.is_limited,
            "vehicle_max_qty": dr.max_product_qty,
            "used_qty": dr.product_qty,
            "remaining_qty": dr.product_qty_remaining,
            "over_capacity": dr.is_limited and dr.product_qty_remaining < 0,
        }
