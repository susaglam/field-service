# Copyright (C) 2019 - TODAY, Open Source Integrators, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.fields import Domain


class FSMStageStatus(models.Model):
    _name = "fsm.stage.status"
    _description = "Order Sub-Status"

    name = fields.Char(required=True)

    @api.model
    def _search(self, domain, *args, **kwargs):
        # The order form passes its stage as fsm_order_stage_id so the
        # sub-status dropdown only offers what that stage allows.
        stage_id = self.env.context.get("fsm_order_stage_id")
        if stage_id:
            # Read the stage WITHOUT that key: on saas-19.4 reading a many2many
            # searches its comodel, which is this method, and kept the key in
            # context, so the dropdown died with RecursionError.
            stage = (
                self.env["fsm.stage"]
                .with_context(fsm_order_stage_id=False)
                .browse(stage_id)
            )
            allowed = stage.sub_stage_id | stage.sub_stage_ids
            if allowed:
                # Narrow the caller's domain instead of replacing it, so the
                # text typed into the dropdown still filters.
                domain = Domain(domain) & Domain("id", "in", allowed.ids)
        return super()._search(domain, *args, **kwargs)
