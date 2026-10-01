# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.api import SUPERUSER_ID


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    sub_stage_id = fields.Many2one(
        "fsm.stage.status",
        string="Sub-Status",
        required=True,
        tracking=True,
        default=lambda self: self._default_stage_id().sub_stage_id,
        init_storage="_init_sub_stage_id",
        help="Sub Stage Id. Linked record reference.",
    )

    def _init_sub_stage_id(self):
        """Give the orders that already exist a sub-status when the module is
        installed (the field's ``init_storage``).

        sub_stage_id is required, but its default reads the stage's sub-status
        and the "Default" status, which both come from data files that load
        AFTER the schema. Existing orders therefore stayed NULL, PostgreSQL
        refused the constraint ("Constraint not added: column sub_stage_id ...
        contains null values") and those orders had no sub-status at all.

        The "Default" status is created here under its XML id; the data file
        then updates this same record instead of creating a second one.
        """
        cr = self.env.cr
        cr.execute(
            """SELECT res_id FROM ir_model_data
                WHERE module = 'fieldservice_substatus'
                  AND name = 'fsm_stage_status_default'"""
        )
        row = cr.fetchone()
        if row:
            status_id = row[0]
        else:
            cr.execute(
                """INSERT INTO fsm_stage_status
                          (name, create_uid, create_date, write_uid, write_date)
                   VALUES ('Default', %(uid)s, now() AT TIME ZONE 'UTC',
                           %(uid)s, now() AT TIME ZONE 'UTC')
                RETURNING id""",
                {"uid": SUPERUSER_ID},
            )
            status_id = cr.fetchone()[0]
            cr.execute(
                """INSERT INTO ir_model_data
                          (module, name, model, res_id, noupdate,
                           create_uid, create_date, write_uid, write_date)
                   VALUES ('fieldservice_substatus', 'fsm_stage_status_default',
                           'fsm.stage.status', %(res_id)s, FALSE,
                           %(uid)s, now() AT TIME ZONE 'UTC',
                           %(uid)s, now() AT TIME ZONE 'UTC')""",
                {"res_id": status_id, "uid": SUPERUSER_ID},
            )
        cr.execute(
            "UPDATE fsm_order SET sub_stage_id = %s WHERE sub_stage_id IS NULL",
            (status_id,),
        )

    def write(self, vals):
        if "stage_id" in vals:
            sub_stage_id = (
                self.env["fsm.stage"].browse(vals.get("stage_id")).sub_stage_id
            )
            if sub_stage_id:
                vals.update({"sub_stage_id": sub_stage_id.id})
        return super().write(vals)

    def _track_log_get_default_subtype(self, track_init_values):
        # saas-19.4 name of mail.thread._track_subtype (see fieldservice)
        self.ensure_one()
        if "sub_stage_id" in track_init_values:
            return self.env.ref("fieldservice_substatus.fso_substatus_changed")
        return super()._track_log_get_default_subtype(track_init_values)
