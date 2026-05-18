# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class FSMActivity(models.Model):
    _name = "fsm.activity"
    _description = "Field Service Activity"

    name = fields.Char(
        required=True,
        readonly=True,
    )
    required = fields.Boolean(
        default=False,
        readonly=True,
        help="Required.",
    )
    sequence = fields.Integer()
    completed = fields.Boolean(default=False, help="Completed.")
    completed_on = fields.Datetime(readonly=True, help="Completed On.")
    completed_by = fields.Many2one("res.users", readonly=True, help="Completed By.")
    ref = fields.Char("Reference", readonly=True, help="Ref.")
    fsm_order_id = fields.Many2one("fsm.order", "FSM Order", help="Fsm Order Id. Linked record reference.")
    fsm_template_id = fields.Many2one("fsm.template", "FSM Template", help="Fsm Template Id. Linked record reference.")
    state = fields.Selection(
        [("todo", "To Do"), ("done", "Completed"), ("cancel", "Cancelled")],
        readonly=True,
        default="todo",
        help="State. Current state of the record.",
    )

    def action_done(self):
        self.write(
            {
                "completed": True,
                "completed_on": fields.Datetime.now(),
                "completed_by": self.env.user.id,
                "state": "done",
            }
        )

    def action_cancel(self):
        self.state = "cancel"
