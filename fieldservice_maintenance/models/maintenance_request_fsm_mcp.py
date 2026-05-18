# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""MCP / @ai_tool surface for maintenance.request ↔ FSM-order link."""

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


class MaintenanceRequestFsmMcp(models.Model):
    _inherit = "maintenance.request"

    @ai_tool(
        name="fsm_maintenance.get_fsm_order",
        description=(
            "Get the Field Service order linked to a maintenance request "
            "(if any)."
        ),
        input_schema={
            "type": "object",
            "properties": {"request_id": {"type": "integer"}},
            "required": ["request_id"],
        },
        risk="low",
    )
    def action_mcp_fsm_order(self, request_id):
        r = self.browse(request_id).exists()
        if not r:
            return {"error": f"Maintenance request {request_id} not found"}
        if not r.fsm_order_id:
            return {
                "request_id": r.id,
                "name": r.name,
                "fsm_order": None,
            }
        return {
            "request_id": r.id,
            "name": r.name,
            "fsm_order": {
                "id": r.fsm_order_id.id,
                "name": r.fsm_order_id.name,
                "stage": r.fsm_order_id.stage_id.name,
            },
        }


class FsmEquipmentMaintenanceMcp(models.Model):
    _inherit = "fsm.equipment"

    @ai_tool(
        name="fsm_maintenance.equipment_stats",
        description=(
            "Return predictive-maintenance stats for an FSM equipment: "
            "MTBF (mean time between failure), MTTR (mean repair time), "
            "next failure ETA, current open maintenance count."
        ),
        input_schema={
            "type": "object",
            "properties": {"equipment_id": {"type": "integer"}},
            "required": ["equipment_id"],
        },
        risk="low",
    )
    def action_mcp_maint_stats(self, equipment_id):
        eq = self.browse(equipment_id).exists()
        if not eq:
            return {"error": f"Equipment {equipment_id} not found"}
        return {
            "id": eq.id,
            "name": eq.display_name,
            "expected_mtbf": eq.expected_mtbf,
            "mtbf": eq.mtbf,
            "mttr": eq.mttr,
            "latest_failure_date": eq.latest_failure_date.isoformat()
            if eq.latest_failure_date
            else None,
            "estimated_days_until_failure": eq.estimated_next_failure,
            "maintenance_count": eq.maintenance_count,
            "maintenance_open_count": eq.maintenance_open_count,
        }
