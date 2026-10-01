# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""A day-route's cash count: collected vs counted, and the entry for the gap.

Rewritten for 20.0. The previous version dated from Odoo 12 (account.invoice,
user_type_id, action_validate_invoice_payment) and could not run.
"""

from odoo import Command, fields
from odoo.tests import tagged

from odoo.addons.fieldservice_account.tests.test_fsm_account import FSMAccountCase


@tagged("-at_install", "post_install")
class TestDayrouteAccount(FSMAccountCase):
    def setUp(self):
        super().setUp()
        company = self.env.company
        self.bank_journal = (
            self.env["account.journal"]
            .search([("company_id", "=", company.id), ("type", "=", "bank")], limit=1)
            .ensure_one()
        )
        self.worker = self.env["fsm.person"].create({"name": "Route Worker"})
        self.route = self.env["fsm.route"].create(
            {
                "name": "Cash Route",
                "max_order": 10,
                "fsm_person_id": self.worker.id,
                "day_ids": [Command.set(self.env["fsm.route.day"].search([]).ids)],
            }
        )
        self.test_location.fsm_route_id = self.route
        # Assigning a worker and a date puts the order on that day's route
        self.test_order.write(
            {
                "person_id": self.worker.id,
                "scheduled_date_start": fields.Datetime.now(),
            }
        )
        self.dayroute = self.test_order.dayroute_id
        self.closed_stage = self.env.ref("fieldservice_route.fsm_stage_route_close")

    def _collect(self, amount):
        """The worker takes a payment for the order on the bank journal."""
        payment = self.env["account.payment"].create(
            {
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": self.test_partner.id,
                "amount": amount,
                "journal_id": self.bank_journal.id,
            }
        )
        payment.fsm_order_ids = [Command.set(self.test_order.ids)]
        payment.action_post()
        return payment

    def test_order_is_on_a_dayroute(self):
        self.assertTrue(self.dayroute)
        self.assertEqual(self.dayroute.person_id, self.worker)

    def test_payment_opens_one_count_row_per_journal(self):
        self._collect(100.0)
        self._collect(60.0)
        rows = self.dayroute.dayroute_payment_ids
        self.assertEqual(len(rows), 1, "one row per journal, not per payment")
        self.assertEqual(rows.journal_id, self.bank_journal)
        self.assertEqual(rows.amount_collected, 160.0)

    def test_gap_between_collected_and_counted(self):
        self._collect(160.0)
        row = self.dayroute.dayroute_payment_ids
        row.amount_counted = 100.0
        self.assertEqual(row.difference, 60.0)

    def test_closing_the_route_books_the_missing_cash(self):
        """What was collected but not handed in becomes a receivable on the
        worker when the day-route is closed."""
        self._collect(160.0)
        row = self.dayroute.dayroute_payment_ids
        row.amount_counted = 100.0
        self.dayroute.stage_id = self.closed_stage
        self.assertTrue(row.move_id, "a journal entry for the 60.00 gap")
        self.assertEqual(row.move_id.state, "posted")
        self.assertEqual(sum(row.move_id.line_ids.mapped("debit")), 60.0)
        worker_partner = self.worker.partner_id.commercial_partner_id
        self.assertIn(worker_partner, row.move_id.line_ids.partner_id)

    def test_closing_a_balanced_route_books_nothing(self):
        self._collect(160.0)
        row = self.dayroute.dayroute_payment_ids
        row.amount_counted = 160.0
        self.dayroute.stage_id = self.closed_stage
        self.assertFalse(row.move_id)
