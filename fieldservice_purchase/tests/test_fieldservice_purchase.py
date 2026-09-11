# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestFieldServicePurchase(TransactionCase):
    """A technician's vendor price lists are counted and opened by vendor.

    The vendor on product.supplierinfo is `partner_id` since Odoo 16. This
    test still created its rows with `name` and the model searched on `name`,
    so the technician form raised "Invalid field product.supplierinfo.name"
    on the live database while this file could never have passed. A price
    list row also needs a product in 19.4 (product_tmpl_id is required).
    """

    def setUp(self):
        super().setUp()
        self.product_supplierinfo_obj = self.env["product.supplierinfo"]
        self.fsm_person_obj = self.env["fsm.person"]
        self.product = self.env["product.template"].create(
            {"name": "Tiles bought from this technician"})

    def _price_list(self, person, min_qty, price):
        return self.product_supplierinfo_obj.create({
            "partner_id": person.partner_id.id,
            "product_tmpl_id": self.product.id,
            "min_qty": min_qty,
            "price": price,
        })

    def test_fieldservice_purchase(self):
        fsm_person = self.fsm_person_obj.create({"name": "Test FSM Person"})

        # Test with 1 records Vendor Pricelist
        self._price_list(fsm_person, 1.0, 100)
        fsm_person._compute_pricelist_count()
        self.assertEqual(
            fsm_person.pricelist_count, 1, "Wrong no of vendors pricelist!"
        )
        action = fsm_person.action_view_pricelists()
        self.assertTrue(action.get("res_id"), "one price list opens its form")

        # Test with 2 records Vendor Pricelist
        self._price_list(fsm_person, 2.0, 200)
        fsm_person._compute_pricelist_count()
        self.assertEqual(
            fsm_person.pricelist_count, 2, "Wrong no of vendors pricelist!"
        )
        action = fsm_person.action_view_pricelists()
        self.assertEqual(len(action["domain"][0][2]), 2, "two open as a list")

    def test_the_technician_form_can_be_read(self):
        """What the browser does when the form opens: read the counter."""
        fsm_person = self.fsm_person_obj.create({"name": "Form reader"})
        values = fsm_person.web_read({"pricelist_count": {}})
        self.assertEqual(values[0]["pricelist_count"], 0)
