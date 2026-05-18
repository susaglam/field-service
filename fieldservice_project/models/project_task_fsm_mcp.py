# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""MCP / @ai_tool surface for project.task ↔ FSM-order link."""

from odoo import models
from odoo.addons.cs_mcp_bridge.tools import ai_tool


class ProjectTaskFsmMcp(models.Model):
    _inherit = "project.task"

    @ai_tool(
        name="fsm_project.list_fsm_orders",
        description=(
            "List Field Service orders linked to a project task. Returns "
            "id, name, stage."
        ),
        input_schema={
            "type": "object",
            "properties": {"task_id": {"type": "integer"}},
            "required": ["task_id"],
        },
        risk="low",
    )
    def action_mcp_list_fsm(self, task_id):
        t = self.browse(task_id).exists()
        if not t:
            return {"error": f"Task {task_id} not found"}
        return {
            "task_id": t.id,
            "task_name": t.name,
            "fsm_orders": [
                {"id": o.id, "name": o.name, "stage": o.stage_id.name}
                for o in t.fsm_order_ids
            ],
        }
