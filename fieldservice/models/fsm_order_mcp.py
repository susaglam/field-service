# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""MCP / @ai_tool surface for fsm.order.

These methods expose the FSM order workflow to AI / MCP clients via the
cs_mcp_bridge. They are thin JSON wrappers around the existing
action_complete / action_cancel methods plus a few search/inspect helpers
that an AI agent typically needs.
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


class FsmOrderMcp(models.Model):
    _inherit = "fsm.order"

    @ai_tool(
        name="fieldservice.order_search",
        description=(
            "Search Field Service orders by name, location, stage, or "
            "assignee. Returns a list of {id, name, stage, location, "
            "person, scheduled_date_start} dicts."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "name_contains": {"type": "string"},
                "location_id": {"type": "integer"},
                "stage_name": {"type": "string"},
                "person_id": {"type": "integer"},
                "limit": {"type": "integer", "default": 20},
            },
        },
        risk="low",
    )
    def action_mcp_search(
        self,
        name_contains=None,
        location_id=None,
        stage_name=None,
        person_id=None,
        limit=20,
    ):
        domain = []
        if name_contains:
            domain.append(("name", "ilike", name_contains))
        if location_id:
            domain.append(("location_id", "=", location_id))
        if stage_name:
            domain.append(("stage_id.name", "ilike", stage_name))
        if person_id:
            domain.append(("person_id", "=", person_id))
        orders = self.search(domain, limit=limit)
        return {
            "count": len(orders),
            "orders": [
                {
                    "id": o.id,
                    "name": o.name,
                    "stage": o.stage_id.name,
                    "location": o.location_id.display_name,
                    "person": o.person_id.name if o.person_id else None,
                    "scheduled_date_start": (
                        o.scheduled_date_start.isoformat()
                        if o.scheduled_date_start
                        else None
                    ),
                }
                for o in orders
            ],
        }

    @ai_tool(
        name="fieldservice.order_read",
        description=(
            "Read full details of an FSM order — stage, location, person, "
            "description, scheduled timing, priority, tags."
        ),
        input_schema={
            "type": "object",
            "properties": {"order_id": {"type": "integer"}},
            "required": ["order_id"],
        },
        risk="low",
    )
    def action_mcp_read(self, order_id):
        order = self.browse(order_id).exists()
        if not order:
            return {"error": f"Order {order_id} not found"}
        return {
            "id": order.id,
            "name": order.name,
            "stage": order.stage_id.name,
            "is_closed": order.stage_id.is_closed,
            "location": order.location_id.display_name,
            "person": order.person_id.name if order.person_id else None,
            "team": order.team_id.name if order.team_id else None,
            "description": order.description or "",
            "scheduled_date_start": (
                order.scheduled_date_start.isoformat()
                if order.scheduled_date_start
                else None
            ),
            "scheduled_duration": order.scheduled_duration,
            "priority": order.priority,
            "tags": [t.name for t in order.tag_ids],
        }

    @ai_tool(
        name="fieldservice.order_complete",
        description=(
            "Mark an FSM order as completed. Sets its stage to the "
            "'Completed' stage and bypasses any open-required-fields "
            "validation. Returns the new stage of the order."
        ),
        input_schema={
            "type": "object",
            "properties": {"order_id": {"type": "integer"}},
            "required": ["order_id"],
        },
        risk="medium",
        examples=[
            {
                "goal": "Close a finished service call",
                "steps": [
                    {
                        "tool": "fieldservice.order_read",
                        "args": {"order_id": 42},
                    },
                    {
                        "tool": "fieldservice.order_complete",
                        "args": {"order_id": 42},
                    },
                ],
            }
        ],
    )
    def action_mcp_complete(self, order_id):
        order = self.browse(order_id).exists()
        if not order:
            return {"error": f"Order {order_id} not found"}
        order.action_complete()
        return {
            "id": order.id,
            "name": order.name,
            "stage": order.stage_id.name,
            "is_closed": order.stage_id.is_closed,
        }

    @ai_tool(
        name="fieldservice.order_cancel",
        description=(
            "Cancel an FSM order. Sets its stage to 'Cancelled'. "
            "Returns the new stage."
        ),
        input_schema={
            "type": "object",
            "properties": {"order_id": {"type": "integer"}},
            "required": ["order_id"],
        },
        risk="high",
        examples=[
            {
                "goal": "Cancel an order that cannot be fulfilled",
                "steps": [
                    {
                        "tool": "fieldservice.order_cancel",
                        "args": {"order_id": 42},
                    }
                ],
            }
        ],
    )
    def action_mcp_cancel(self, order_id):
        order = self.browse(order_id).exists()
        if not order:
            return {"error": f"Order {order_id} not found"}
        order.action_cancel()
        return {
            "id": order.id,
            "name": order.name,
            "stage": order.stage_id.name,
        }

    @ai_tool(
        name="fieldservice.order_assign",
        description=(
            "Assign an FSM order to a worker (fsm.person). The worker "
            "must already exist; create one via fieldservice.worker_create "
            "if needed."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "order_id": {"type": "integer"},
                "person_id": {"type": "integer"},
            },
            "required": ["order_id", "person_id"],
        },
        risk="medium",
    )
    def action_mcp_assign(self, order_id, person_id):
        order = self.browse(order_id).exists()
        if not order:
            return {"error": f"Order {order_id} not found"}
        order.write({"person_id": person_id})
        return {
            "id": order.id,
            "name": order.name,
            "person": order.person_id.name if order.person_id else None,
        }

    @ai_tool(
        name="fieldservice.order_schedule",
        description=(
            "Schedule an FSM order — set its scheduled start datetime "
            "and optional duration in hours. The end date is computed "
            "automatically."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "order_id": {"type": "integer"},
                "start_iso": {
                    "type": "string",
                    "description": "ISO 8601 datetime, e.g. 2026-05-20T09:00:00",
                },
                "duration_hours": {"type": "number"},
            },
            "required": ["order_id", "start_iso"],
        },
        risk="medium",
    )
    def action_mcp_schedule(self, order_id, start_iso, duration_hours=None):
        order = self.browse(order_id).exists()
        if not order:
            return {"error": f"Order {order_id} not found"}
        vals = {"scheduled_date_start": start_iso}
        if duration_hours is not None:
            vals["scheduled_duration"] = duration_hours
        order.write(vals)
        return {
            "id": order.id,
            "name": order.name,
            "scheduled_date_start": (
                order.scheduled_date_start.isoformat()
                if order.scheduled_date_start
                else None
            ),
            "scheduled_date_end": (
                order.scheduled_date_end.isoformat()
                if order.scheduled_date_end
                else None
            ),
            "scheduled_duration": order.scheduled_duration,
        }
