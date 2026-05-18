# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMRouteDayRoute(models.Model):
    _inherit = "fsm.route.dayroute"

    dayroute_payment_ids = fields.One2many(
        "fsm.route.dayroute.payment",
        "dayroute_id",
        string="Payment Summary",
        help="Per-journal cash count for this day-route. Each row aggregates "
        "the payments collected from this day-route's FSM orders.",
    )
    invoice_count = fields.Integer(
        string="Invoice Count",
        compute="_compute_invoice_count",
        readonly=True,
        help="Total number of customer invoices generated from the FSM orders "
        "on this day-route.",
    )

    def write(self, values):
        result = super().write(values)
        if not values.get("stage_id"):
            return result
        for rec in self:
            if not (
                rec.stage_id.stage_type == "route" and rec.stage_id.is_closed
            ):
                continue
            for route_payment in rec.dayroute_payment_ids:
                if route_payment.difference <= 0:
                    continue
                partner = rec.person_id.partner_id.commercial_partner_id
                account = partner.property_account_receivable_id
                amount = route_payment.difference
                lines = [
                    (0, 0, {
                        "name": rec.name,
                        "account_id": account.id,
                        "partner_id": partner.id,
                        "debit": amount,
                    }),
                    (0, 0, {
                        "name": rec.name,
                        "account_id":
                            route_payment.journal_id.default_account_id.id,
                        "credit": amount,
                    }),
                ]
                move = self.env["account.move"].create({
                    "journal_id": route_payment.journal_id.id,
                    "ref": rec.name,
                    "line_ids": lines,
                })
                route_payment.move_id = move
                move.action_post()
        return result

    @api.depends("order_ids.invoice_count")
    def _compute_invoice_count(self):
        for dayroute in self:
            dayroute.invoice_count = sum(
                order.invoice_count for order in dayroute.order_ids
            )

    def action_view_invoices(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account.action_move_out_invoice_type"
        )
        invoice_ids = self.order_ids.invoice_ids.ids
        if self.invoice_count > 1:
            action["domain"] = [("id", "in", invoice_ids)]
        elif self.invoice_count == 1:
            form = self.env.ref("account.view_move_form")
            action["views"] = [(form.id, "form")]
            action["res_id"] = invoice_ids[0]
        return action
