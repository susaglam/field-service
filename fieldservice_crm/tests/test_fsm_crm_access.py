# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""Who sees work orders once the CRM link is installed.

This module used to give every internal user read access to ALL orders so a
salesperson could see the order count on a lead. Permissions are OR'd since
19.4, so that row also overruled "User (only own documents)": a fitter saw
every customer's visits.
"""

from odoo.tests.common import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestFieldserviceCrmAccess(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        customer = cls.env["res.partner"].create({"name": "CRM access customer"})
        cls.location = cls.env["fsm.location"].create(
            {"name": "CRM access site", "owner_id": customer.id}
        )
        cls.lead = cls.env["crm.lead"].create(
            {"name": "Bathroom renovation", "fsm_location_id": cls.location.id}
        )
        cls.fitter_user = new_test_user(
            cls.env, login="crm_own_fitter", groups="fieldservice.group_fsm_user_own"
        )
        fitter = cls.env["fsm.person"].create(
            {"name": "Own fitter", "partner_id": cls.fitter_user.partner_id.id}
        )
        cls.mine = cls.env["fsm.order"].create(
            {
                "location_id": cls.location.id,
                "person_id": fitter.id,
                "opportunity_id": cls.lead.id,
            }
        )
        cls.someone_elses = cls.env["fsm.order"].create(
            {"location_id": cls.location.id, "opportunity_id": cls.lead.id}
        )
        cls.salesperson = new_test_user(
            cls.env, login="crm_only_sales", groups="sales_team.group_sale_salesman"
        )

    def test_fitter_sees_only_own_orders(self):
        Order = self.env["fsm.order"].with_user(self.fitter_user)
        visible = Order.search([("id", "in", (self.mine + self.someone_elses).ids)])
        self.assertEqual(visible, self.mine.with_user(self.fitter_user))

    def test_salesperson_reads_the_count_without_fsm_rights(self):
        lead = self.lead.with_user(self.salesperson)
        self.lead.user_id = self.salesperson
        self.assertEqual(lead.fsm_order_count, 2)
        self.assertFalse(
            self.env["fsm.order"].with_user(self.salesperson).has_access("read")
        )
