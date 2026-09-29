# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, tagged
from odoo.tests.common import JsonRpcException
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestFieldserviceUi(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.completed = cls.env.ref("fieldservice.fsm_stage_completed")
        cls.team = cls.env["fsm.team"].create({"name": "FSM Tour Team"})
        owner = cls.env["res.partner"].create({"name": "FSM Tour Owner"})
        location = cls.env["fsm.location"].create(
            {"name": "FSM Tour Location", "owner_id": owner.id}
        )
        cls.order = cls.env["fsm.order"].create(
            {
                "name": "FSM Tour Order",
                "location_id": location.id,
                "team_id": cls.team.id,
            }
        )

    def _call(self, method, args, context=None):
        return self.make_jsonrpc_request(
            f"/web/dataset/call_kw/fsm.order/{method}",
            {
                "model": "fsm.order",
                "method": method,
                "args": args,
                "kwargs": {"context": context or {}},
            },
        )

    def test_a_client_cannot_skip_the_complete_button(self):
        """action_complete() is where modules check an order before it is done
        (required activities, stock transfers). The context key it used to set
        for itself came over JSON-RPC as easily, so any user could skip them."""
        self.authenticate("admin", "admin")
        with mute_logger("odoo.http"), self.assertRaises(JsonRpcException):
            self._call(
                "write",
                [[self.order.id], {"stage_id": self.completed.id}],
                {"bypass_order_completed_stage": True},
            )
        self.assertNotEqual(self.order.stage_id, self.completed)
        self._call("action_complete", [[self.order.id]])
        self.order.invalidate_recordset(["stage_id"])
        self.assertEqual(self.order.stage_id, self.completed)

    def test_kanban_views_tour(self):
        self.start_tour(
            "/odoo/action-fieldservice.action_team_dashboard",
            "fieldservice.kanban_views_tour",
            login="admin",
        )
