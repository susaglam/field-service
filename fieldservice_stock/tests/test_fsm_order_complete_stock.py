# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""Completing an order books its transfers; transfer lines follow their order.

Self-contained fixtures (no demo XML IDs), so the suite also runs on a
database installed without demo data.
"""

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestFSMOrderCompleteStock(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)], limit=1
        )
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create(
            {"name": "Mixer tap", "type": "consu", "is_storable": True}
        )
        cls.customer = cls.env["res.partner"].create({"name": "FSM Stock Customer"})
        cls.site = cls.env["fsm.location"].create(
            {"name": "FSM Stock Site", "owner_id": cls.customer.id}
        )
        cls.order = cls._create_order()
        cls.completed = cls.env.ref("fieldservice.fsm_stage_completed")

    @classmethod
    def _create_order(cls):
        return cls.env["fsm.order"].create(
            {"location_id": cls.site.id, "warehouse_id": cls.warehouse.id}
        )

    def _create_delivery(self, qty=2.0, order=None):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.out_type_id.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "partner_id": self.customer.id,
                "fsm_order_id": order.id if order else False,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": qty,
                            "location_id": self.stock_location.id,
                            "location_dest_id": self.customer_location.id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        return picking

    def _put_in_stock(self, qty):
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.stock_location, qty
        )

    # -- transfer lines follow their order -------------------------------

    def test_linking_a_transfer_brings_its_lines(self):
        picking = self._create_delivery()
        self.assertFalse(self.order.move_ids)
        picking.fsm_order_id = self.order
        self.assertEqual(self.order.move_ids, picking.move_ids)

    def test_line_added_to_a_linked_transfer_shows_on_the_order(self):
        picking = self._create_delivery(order=self.order)
        extra = self.env["stock.move"].create(
            {
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "picking_id": picking.id,
            }
        )
        self.assertEqual(extra.fsm_order_id, self.order)
        self.assertIn(extra, self.order.move_ids)

    def test_line_of_another_order_keeps_its_order(self):
        other_order = self._create_order()
        picking = self._create_delivery()
        picking.move_ids.fsm_order_id = other_order
        picking.fsm_order_id = self.order
        self.assertEqual(picking.move_ids.fsm_order_id, other_order)

    # -- completing the order ----------------------------------------------

    def test_complete_leaves_transfer_open_when_setting_off(self):
        self.company.fsm_auto_validate_pickings = False
        self._put_in_stock(10)
        picking = self._create_delivery(order=self.order)
        self.order.action_complete()
        self.assertEqual(self.order.stage_id, self.completed)
        self.assertNotEqual(picking.state, "done")

    def test_complete_validates_transfer(self):
        self.company.fsm_auto_validate_pickings = True
        self._put_in_stock(10)
        picking = self._create_delivery(qty=2.0, order=self.order)
        self.order.action_complete()
        self.assertEqual(picking.state, "done")
        self.assertEqual(self.order.stage_id, self.completed)
        self.assertEqual(self.product.with_company(self.company).qty_available, 8.0)

    def test_complete_blocked_and_explained_when_stock_short(self):
        self.company.fsm_auto_validate_pickings = True
        self._put_in_stock(1)
        picking = self._create_delivery(qty=2.0, order=self.order)
        with self.assertRaisesRegex(UserError, "cannot be completed yet") as caught:
            self.order.action_complete()
        message = str(caught.exception)
        self.assertIn(picking.name, message)
        self.assertIn("Mixer tap", message)
        self.assertNotEqual(self.order.stage_id, self.completed)
        self.assertNotEqual(picking.state, "done")
