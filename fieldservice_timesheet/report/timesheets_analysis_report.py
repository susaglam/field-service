# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import SQL


class TimesheetsAnalysisReport(models.Model):
    _inherit = "timesheets.analysis.report"

    fsm_order_id = fields.Many2one(
        "fsm.order", string="Field Service Order", readonly=True
    )

    @api.model
    def _select(self):
        # 20.0: the report's query parts are SQL objects (_table_sql), not strings
        return SQL(
            """%s,
            A.fsm_order_id AS fsm_order_id
            """,
            super()._select(),
        )
