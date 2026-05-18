# Copyright (C) 2020 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class FSMPersonCalendarFilter(models.Model):
    """Assigned Worker Calendar Filter"""

    _name = "fsm.person.calendar.filter"
    _description = "FSM Person Calendar Filter"

    user_id = fields.Many2one(
        "res.users",
        "Me",
        required=True,
        default=lambda self: self.env.user,
        ondelete="cascade",
        help="User Id. Linked record reference.",
    )
    person_id = fields.Many2one("fsm.person", "FSM Worker", required=True, help="Person Id. Linked record reference.")
    active = fields.Boolean(default=True)
    person_checked = fields.Boolean(default=True, help="Person Checked.")

    _user_id_fsm_person_id_unique = models.Constraint(
        'UNIQUE(user_id,person_id)',
        'You cannot have the same worker twice.',
    )
