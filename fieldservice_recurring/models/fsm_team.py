# Copyright (C) 2022 Raphaël Reverdy (Akretion)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMTeam(models.Model):
    _inherit = "fsm.team"

    def _compute_recurring_draft_count(self):
        order_data = self.env["fsm.recurring"]._read_group(
            [
                ("team_id", "in", self.ids),
                ("state", "=", "draft"),
            ],
            groupby=["team_id"],
            aggregates=["__count"],
        )
        result = {team.id: count for team, count in order_data}
        for team in self:
            team.recurring_draft_count = result.get(team.id, 0)

    recurring_draft_count = fields.Integer(
        compute="_compute_recurring_draft_count", string="Recurring in draft"
    )
