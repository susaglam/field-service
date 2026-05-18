# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMRoutePayment(models.Model):
    _name = "fsm.route.dayroute.payment"
    _rec_name = "journal_id"
    _description = "Field Service Dayroute Payment"

    journal_id = fields.Many2one(
        "account.journal",
        string="Journal",
        required=True,
        help="Accounting journal that received the payments for this "
        "day-route (Cash, Bank, etc.). One row per journal — each row "
        "aggregates the collected vs. counted amounts for that journal.",
    )
    amount_collected = fields.Float(
        string="Collected Amount",
        readonly=True,
        compute="_compute_amount_collected",
        help="Sum of payments that were posted against this day-route's "
        "FSM orders on the selected journal. Auto-computed from "
        "account.payment records.",
    )
    amount_counted = fields.Float(
        string="Counted Amount",
        default=0.0,
        help="Cash / amount physically counted by the worker at the end "
        "of the day-route. The difference between this and the "
        "Collected Amount becomes the day-route's reconciliation "
        "discrepancy.",
    )
    difference = fields.Float(
        string="Difference",
        compute="_compute_amount_difference",
        help="Collected Amount minus Counted Amount. Positive values "
        "indicate uncounted cash (worker owes the company); negative "
        "values indicate over-counting (company owes the worker).",
    )
    move_id = fields.Many2one(
        "account.move",
        string="Journal Entry",
        readonly=True,
        help="Auto-generated account move that reconciles a positive "
        "difference into the worker's receivable account when the "
        "day-route stage closes.",
    )
    dayroute_id = fields.Many2one(
        "fsm.route.dayroute",
        string="Day Route",
        ondelete="cascade",
        help="The day-route whose order payments this row aggregates.",
    )

    def _compute_amount_collected(self):
        """Returns total amount collected by worker"""
        account_payment_obj = self.env["account.payment"]
        for dayroute_payment in self:
            amount = 0
            for fsm_order in dayroute_payment.dayroute_id.order_ids:
                payment_ids = account_payment_obj.search(
                    [
                        ("journal_id", "=", dayroute_payment.journal_id.id),
                        ("fsm_order_ids", "in", [fsm_order.id]),
                    ]
                )
                for payment in payment_ids:
                    amount += payment.amount
            dayroute_payment.amount_collected = amount

    @api.depends("amount_collected", "amount_counted")
    def _compute_amount_difference(self):
        """Returns difference between amount collected and amount counted"""
        for rec in self:
            rec.difference = rec.amount_collected - rec.amount_counted
