# Copyright 2026 — rewritten for saas-19.4
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""Portal tests that build their own fixtures.

The previous version of this file could only pass on a database installed WITH
demo data: it logged in as ``portal`` / ``demo``, read ``fsm.order.search([])[0]``
and asserted on the literal string "Demo Order". On any real database those
users do not exist and that search is empty, so all eight tests errored — and
before that they never ran at all, because ``from odoo.http import Request``
stopped importing in saas-19.4 and took the whole registry load down with it.

Everything the tests need is created here instead. That also lets them assert
the thing the demo-data version could not: a portal customer must see THEIR
orders and only theirs. There is a second customer in the fixture for exactly
that reason — without a stranger in the database, every scoping test passes by
accident.
"""

from odoo import Command
from odoo.tests.common import HttpCase, tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestFsmOrderPortal(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.customer = cls._make_customer("Portal Customer", "fsm_portal_customer")
        cls.stranger = cls._make_customer("Someone Else", "fsm_portal_stranger")

        cls.my_order = cls._make_order(cls.customer, "Kitchen tap replacement")
        # Two for the stranger, so that a count which ignores the record rule
        # cannot coincide with the right answer.
        cls.their_order = cls._make_order(cls.stranger, "Boiler service")
        cls._make_order(cls.stranger, "Radiator bleed")

    @classmethod
    def _make_customer(cls, name, login):
        partner = cls.env["res.partner"].create(
            {"name": name, "email": "%s@example.invalid" % login}
        )
        cls.env["res.users"].create(
            {
                "name": name,
                "login": login,
                "password": login,
                "partner_id": partner.id,
                "group_ids": [Command.set([cls.env.ref("base.group_portal").id])],
            }
        )
        return partner

    @classmethod
    def _make_order(cls, owner, description):
        location = cls.env["fsm.location"].create(
            {
                "name": "Location for %s" % owner.name,
                "partner_id": owner.id,
                "owner_id": owner.id,
            }
        )
        return cls.env["fsm.order"].create(
            {"location_id": location.id, "description": description}
        )

    # ------------------------------------------------------------------
    # The list
    # ------------------------------------------------------------------
    def test_my_orders_page_opens(self):
        self.authenticate("fsm_portal_customer", "fsm_portal_customer")
        response = self.url_open("/my/fsm_orders")
        self.assertEqual(response.status_code, 200)

    def test_the_list_shows_my_order_and_not_a_strangers(self):
        self.authenticate("fsm_portal_customer", "fsm_portal_customer")
        response = self.url_open("/my/fsm_orders?filterby=all")
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.my_order.name, response.text)
        self.assertNotIn(
            self.their_order.name,
            response.text,
            "a portal customer was shown another customer's work order",
        )

    def test_a_search_matching_nothing_leaves_the_list_empty(self):
        self.authenticate("fsm_portal_customer", "fsm_portal_customer")
        response = self.url_open(
            "/my/fsm_orders?groupby=none&filterby=all&search_in=name"
            "&search=zzz-no-such-order"
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.my_order.name, response.text)

    def test_grouping_and_sorting_render(self):
        self.authenticate("fsm_portal_customer", "fsm_portal_customer")
        response = self.url_open(
            "/my/fsm_orders?groupby=stage_id&filterby=all&sortby=location"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.my_order.name, response.text)

    # ------------------------------------------------------------------
    # A single order
    # ------------------------------------------------------------------
    def test_my_order_opens(self):
        self.authenticate("fsm_portal_customer", "fsm_portal_customer")
        response = self.url_open("/my/fsm_order/%d" % self.my_order.id)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.my_order.name, response.text)

    def test_query_parameters_are_tolerated(self):
        self.authenticate("fsm_portal_customer", "fsm_portal_customer")
        response = self.url_open(
            "/my/fsm_order/%d?success='success'" % self.my_order.id
        )
        self.assertEqual(response.status_code, 200)

    @mute_logger("odoo.http")
    def test_a_strangers_order_is_refused(self):
        """Refusal is a redirect to /my, not a 403 — assert the real contract.

        The controller catches AccessError and redirects. That is reasonable
        for a customer-facing page (a bare 403 is a dead end), so the test
        asserts what the module actually promises rather than forcing the
        module to match the test. What must never happen is the order itself
        appearing, and the follow-through below checks exactly that.
        """
        self.authenticate("fsm_portal_customer", "fsm_portal_customer")
        response = self.url_open(
            "/my/fsm_order/%d" % self.their_order.id, allow_redirects=False
        )
        self.assertIn(
            response.status_code,
            (302, 303),
            "a portal customer was not turned away from another customer's order",
        )
        self.assertURLEqual(response.headers.get("Location", ""), "/my")

        followed = self.url_open("/my/fsm_order/%d" % self.their_order.id)
        self.assertNotIn(
            self.their_order.name,
            followed.text,
            "another customer's work order leaked into the page",
        )

    # ------------------------------------------------------------------
    # The portal home and its counter
    # ------------------------------------------------------------------
    def test_the_portal_home_offers_the_section(self):
        self.authenticate("fsm_portal_customer", "fsm_portal_customer")
        response = self.url_open("/my/home")
        self.assertEqual(response.status_code, 200)
        self.assertIn("/my/fsm_orders", response.text)

    def test_the_counter_counts_only_my_orders(self):
        """The number on the portal home is the customer's, not the company's.

        The counter used to be read with ``sudo()`` against a domain that only
        filtered on the stage, so every portal customer was shown the total
        number of work orders in the database. That is a leak of business
        volume, and it contradicts the page it links to: the list underneath
        applies the record rule, so one row would appear under a heading that
        said 143.
        """
        self.authenticate("fsm_portal_customer", "fsm_portal_customer")
        result = self.make_jsonrpc_request(
            "/my/counters", {"counters": ["fsm_order_count"]}
        )
        self.assertEqual(result["fsm_order_count"], 1)

        self.authenticate("fsm_portal_stranger", "fsm_portal_stranger")
        result = self.make_jsonrpc_request(
            "/my/counters", {"counters": ["fsm_order_count"]}
        )
        self.assertEqual(result["fsm_order_count"], 2)
