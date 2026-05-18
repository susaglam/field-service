# Copyright (c) 2020 Pavlov Media <https://www.pavlovmedia.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ChangeLog(models.Model):
    _name = "change.log"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "implemented_on desc"
    _description = "Change Log"

    active = fields.Boolean(default=True)
    name = fields.Char(string="Title", required=True)
    location_id = fields.Many2one("fsm.location", string="FSM Location", help="Location Id. Linked record reference.")
    implemented_on = fields.Datetime(required=True, default=fields.Datetime.now, help="Implemented On.")
    description = fields.Text(required=True, help="Description.")
    user_id = fields.Many2one(
        "res.users",
        string="Changed By",
        default=lambda self: self.env.user,
        tracking=True,
        required=True,
        help="User Id. Linked record reference.",
    )
    tag_ids = fields.Many2many("change.log.tag", string="Tags", help="Tag Ids. Many-to-many / one-to-many relation collection.")
    type_id = fields.Many2one("change.log.type", string="Type", required=True, help="Type Id. Linked record reference.")
    impact_id = fields.Many2one("change.log.impact", string="Impact", required=True, help="Impact Id. Linked record reference.")
    stage_id = fields.Many2one(
        "change.log.stage",
        string="Stage",
        group_expand="_read_group_stage_ids",
        default=lambda self: self.env.ref(
            "fieldservice_change_management.change_log_stage_active"
        )
        or 0,
        help="Select the current stage of the Bandwidth Change.",
    )
