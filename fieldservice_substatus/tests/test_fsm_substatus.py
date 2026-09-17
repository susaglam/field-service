# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class FSMSubstatusCase(TransactionCase):
    def setUp(self):
        super().setUp()
        self.WorkOrder = self.env["fsm.order"]
        self.stage_id = self.WorkOrder._default_stage_id()
        self.init_values = {"sub_stage_id": self.stage_id.sub_stage_id.id}
        self.StageStatus = self.env["fsm.stage.status"]
        # create a Res Partner to be converted to FSM Location/Person
        self.test_loc_partner = self.env["res.partner"].create(
            {"name": "Test Loc Partner", "phone": "ABC", "email": "tlp@email.com"}
        )
        # create expected FSM Location to compare to converted FSM Location
        self.test_location = self.env["fsm.location"].create(
            {
                "name": "Test Location",
                "phone": "123",
                "email": "tp@email.com",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
            }
        )
        self.stage = self.env["fsm.stage"].create(
            {
                "name": "Stage 1",
                "sequence": 2,
                "stage_type": "order",
                "sub_stage_id": self.stage_id.sub_stage_id.id,
            }
        )

    def test_fsm_orders(self):
        """Test creating new workorders, and test following functions."""
        # Create an Orders
        hours_diff = 100
        date_start = fields.Datetime.today()
        order = self.WorkOrder.create(
            {
                "location_id": self.test_location.id,
                "date_start": date_start,
                "date_end": date_start + timedelta(hours=hours_diff),
                "request_early": fields.Datetime.today(),
            }
        )
        order._track_log_get_default_subtype(self.init_values)
        order._track_log_get_default_subtype({})
        self.stage.onchange_sub_stage_id()
        stage_status_id = self.StageStatus.with_context(
            fsm_order_stage_id=self.stage_id.id
        ).create({"name": "Test"})
        stage_status_id.search([])
        order.stage_id = self.stage.id

    def test_sub_status_dropdown_for_stage(self):
        """The order form's sub-status dropdown offers only what the order's
        stage allows, and still filters on the text typed into it."""
        extra = self.StageStatus.create({"name": "Waiting for parts"})
        other = self.StageStatus.create({"name": "Not for this stage"})
        self.stage.sub_stage_ids = extra
        Status = self.StageStatus.with_context(fsm_order_stage_id=self.stage.id)
        allowed = Status.search([])
        self.assertEqual(allowed, self.stage.sub_stage_id | extra)
        self.assertNotIn(other, allowed)
        self.assertEqual(Status.search([("name", "=", "Waiting for parts")]), extra)
