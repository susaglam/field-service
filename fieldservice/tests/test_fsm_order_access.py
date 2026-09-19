# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""What each Field Service level may do with a work order.

The 19.4 ACL migration turned two RESTRICTING record rules into GRANTING
permissions, and in 19.4 permissions are OR'd: "User (only own documents)"
could create, read, write and DELETE every order in the company, and plain
"User" the same. Found 2026-09-18 on erp.badkamertien, where no fitter had a
login yet — the day one did, they would have seen every customer's address.
"""

from odoo.tests.common import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestFSMOrderAccess(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Built here, not taken from demo data: this suite also runs against a
        # live database, where the demo records do not exist.
        customer = cls.env["res.partner"].create({"name": "Klant toegangstest"})
        cls.location = cls.env["fsm.location"].create({
            "name": "Toegangstest locatie",
            "partner_id": customer.id,
            "owner_id": customer.id,
        })
        cls.fitter_user = new_test_user(
            cls.env, login="fsm_own_fitter", groups="fieldservice.group_fsm_user_own"
        )
        cls.person = cls.env["fsm.person"].create(
            {"name": "Eigen monteur", "partner_id": cls.fitter_user.partner_id.id}
        )
        cls.mine = cls.env["fsm.order"].create(
            {"location_id": cls.location.id, "person_id": cls.person.id}
        )
        cls.someone_elses = cls.env["fsm.order"].create({"location_id": cls.location.id})

    def test_own_documents_means_own_documents(self):
        Order = self.env["fsm.order"].with_user(self.fitter_user)
        visible = Order.search([("id", "in", (self.mine + self.someone_elses).ids)])
        self.assertEqual(visible, self.mine.with_user(self.fitter_user))

    def test_own_documents_cannot_create_or_delete(self):
        Order = self.env["fsm.order"].with_user(self.fitter_user)
        self.assertFalse(Order.has_access("create"))
        self.assertFalse(Order.has_access("unlink"))
        self.assertTrue(self.mine.with_user(self.fitter_user).has_access("write"))

    def test_a_plain_user_reads_every_order_but_deletes_none(self):
        user = new_test_user(
            self.env, login="fsm_plain_user", groups="fieldservice.group_fsm_user"
        )
        Order = self.env["fsm.order"].with_user(user)
        self.assertEqual(
            Order.search([("id", "in", (self.mine + self.someone_elses).ids)]),
            (self.mine + self.someone_elses).with_user(user),
        )
        self.assertFalse(Order.has_access("unlink"))
        self.assertFalse(Order.has_access("create"))

    def test_the_dispatcher_still_runs_the_board(self):
        user = new_test_user(
            self.env, login="fsm_dispatcher", groups="fieldservice.group_fsm_dispatcher"
        )
        Order = self.env["fsm.order"].with_user(user)
        self.assertTrue(Order.has_access("create"))
        self.assertTrue(Order.has_access("unlink"))
