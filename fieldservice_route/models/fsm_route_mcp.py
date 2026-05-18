# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""MCP / @ai_tool surface for fsm.route + fsm.route.dayroute."""

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


class FsmRouteMcp(models.Model):
    _inherit = "fsm.route"

    @ai_tool(
        name="fsm_route.search",
        description=(
            "Search Field Service routes by name or assigned person. "
            "Returns route id, name, person, day of week, max orders."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "name_contains": {"type": "string"},
                "person_id": {"type": "integer"},
                "limit": {"type": "integer", "default": 20},
            },
        },
        risk="low",
    )
    def action_mcp_search(self, name_contains=None, person_id=None, limit=20):
        domain = []
        if name_contains:
            domain.append(("name", "ilike", name_contains))
        if person_id:
            domain.append(("fsm_person_id", "=", person_id))
        routes = self.search(domain, limit=limit)
        return {
            "count": len(routes),
            "routes": [
                {
                    "id": r.id,
                    "name": r.name,
                    "person": r.fsm_person_id.name if r.fsm_person_id else None,
                    "days": [d.name for d in r.day_ids],
                    "max_orders": r.max_order,
                }
                for r in routes
            ],
        }


class FsmRouteDayrouteMcp(models.Model):
    _inherit = "fsm.route.dayroute"

    @ai_tool(
        name="fsm_route.dayroute_search",
        description=(
            "Search FSM day-routes by date, person, route, or stage. "
            "Returns id, name, date, route, person, stage, order count."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "date_from": {"type": "string"},
                "date_to": {"type": "string"},
                "person_id": {"type": "integer"},
                "route_id": {"type": "integer"},
                "stage_name": {"type": "string"},
                "limit": {"type": "integer", "default": 30},
            },
        },
        risk="low",
    )
    def action_mcp_dayroute_search(
        self,
        date_from=None,
        date_to=None,
        person_id=None,
        route_id=None,
        stage_name=None,
        limit=30,
    ):
        domain = []
        if date_from:
            domain.append(("date", ">=", date_from))
        if date_to:
            domain.append(("date", "<=", date_to))
        if person_id:
            domain.append(("person_id", "=", person_id))
        if route_id:
            domain.append(("route_id", "=", route_id))
        if stage_name:
            domain.append(("stage_id.name", "ilike", stage_name))
        records = self.search(domain, limit=limit, order="date desc")
        return {
            "count": len(records),
            "dayroutes": [
                {
                    "id": r.id,
                    "name": r.name,
                    "date": r.date.isoformat() if r.date else None,
                    "route": r.route_id.name if r.route_id else None,
                    "person": r.person_id.name if r.person_id else None,
                    "stage": r.stage_id.name,
                    "order_count": r.order_count,
                    "order_remaining": r.order_remaining,
                }
                for r in records
            ],
        }

    @ai_tool(
        name="fsm_route.dayroute_read",
        description="Read full detail of one day-route including its orders.",
        input_schema={
            "type": "object",
            "properties": {"dayroute_id": {"type": "integer"}},
            "required": ["dayroute_id"],
        },
        risk="low",
    )
    def action_mcp_dayroute_read(self, dayroute_id):
        dr = self.browse(dayroute_id).exists()
        if not dr:
            return {"error": f"Day route {dayroute_id} not found"}
        return {
            "id": dr.id,
            "name": dr.name,
            "date": dr.date.isoformat() if dr.date else None,
            "route": dr.route_id.name if dr.route_id else None,
            "person": dr.person_id.name if dr.person_id else None,
            "stage": dr.stage_id.name,
            "max_order": dr.max_order,
            "order_count": dr.order_count,
            "orders": [
                {"id": o.id, "name": o.name, "stage": o.stage_id.name}
                for o in dr.order_ids
            ],
        }
