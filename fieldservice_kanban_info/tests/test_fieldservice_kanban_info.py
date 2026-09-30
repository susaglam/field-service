# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from odoo import fields

from odoo.addons.base.tests.common import BaseCommon


class TestFieldServiceKanbanInfo(BaseCommon):
    # 20.0 BaseCommon runs each test as a "Test User" holding only these groups
    # (19.4 ran them as the superuser): the dispatcher who plans the orders on
    # the board. Settings and languages are an administrator's, set with sudo().
    _test_user_groups = ("base.group_user", "fieldservice.group_fsm_dispatcher")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.location = cls.env.ref("fieldservice.test_location")

    def _set_format(self, value):
        self.env["ir.config_parameter"].sudo().set_str(
            "fieldservice.schedule_time_range_format", value
        )

    def _create_order(self, start=None, end=None):
        order = self.env["fsm.order"].create(
            {
                "scheduled_date_start": start,
                "scheduled_date_end": end,
                "location_id": self.location.id,
            }
        )
        order._compute_schedule_time_range()
        return order

    def test_schedule_time_range_time_only_same_day(self):
        self._set_format("time_only")
        now = fields.Datetime.now()
        order = self._create_order(now, now + relativedelta(hours=2))
        self.assertIn("-", order.schedule_time_range)

    def test_schedule_time_range_date_and_time_same_day(self):
        self._set_format("date_and_time")
        now = fields.Datetime.now()
        order = self._create_order(now, now + relativedelta(hours=2))
        self.assertIn("/", order.schedule_time_range)
        self.assertIn("-", order.schedule_time_range)

    def test_schedule_time_range_no_start_date(self):
        order = self._create_order()
        self.assertFalse(order.schedule_time_range)

    @freeze_time("2025-08-14 09:00:00")
    def test_schedule_time_range_us_format(self):
        """Test %m/%d/%Y %I:%M %p (US format with AM/PM)"""
        self.env.user.lang = "en_US"
        self.env["res.lang"].sudo()._lang_get("en_US").write(
            # saas-19.4 made time_format a selection: '%I:%M:%S %p' is the 12-hour
            # value; the compute drops the seconds itself
            {"date_format": "%m/%d/%Y", "time_format": "%I:%M:%S %p"}
        )
        self._set_format("date_and_time")

        now = fields.Datetime.now()
        order = self._create_order(now, now + relativedelta(hours=2))
        self.assertRegex(
            order.schedule_time_range,
            r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}\s*(AM|PM)? - \d{2}:\d{2}\s*(AM|PM)?",
        )

    @freeze_time("2025-08-14 09:00:00")
    def test_schedule_time_range_eu_format(self):
        """Test %d/%m/%Y %H:%M:%S (EU format with seconds)"""
        self.env["res.lang"].sudo()._activate_lang("es_ES")
        self.env.user.lang = "es_ES"
        self.env["res.lang"].sudo()._lang_get("es_ES").write(
            {"date_format": "%d/%m/%Y", "time_format": "%H:%M:%S"}
        )
        self._set_format("date_and_time")

        now = fields.Datetime.now()
        order = self._create_order(now, now + relativedelta(hours=2))
        self.assertRegex(
            order.schedule_time_range, r"\d{2}/\d{2}/\d{4} \d{2}:\d{2} - \d{2}:\d{2}"
        )
