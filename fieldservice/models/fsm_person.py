# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMPerson(models.Model):
    _name = "fsm.person"
    _inherits = {"res.partner": "partner_id"}
    _inherit = ["mail.thread.blacklist", "fsm.model.mixin"]
    _description = "Field Service Worker"
    _stage_type = "worker"

    partner_id = fields.Many2one(
        "res.partner",
        string="Related Partner",
        required=True,
        ondelete="restrict",
        delegate=True,
        auto_join=True,
    )
    category_ids = fields.Many2many("fsm.category", string="Categories")
    calendar_id = fields.Many2one("resource.calendar", string="Working Schedule")
    mobile = fields.Char()
    territory_ids = fields.Many2many("res.territory", string="Territories")
    active = fields.Boolean(default=True)
    active_partner = fields.Boolean(
        related="partner_id.active", readonly=True, string="Partner is Active"
    )

    def action_unarchive(self):
        # Mirror the pre-saas-19.x toggle_active cascade: reactivating a
        # worker brings its partner back too if the partner is also
        # archived. Archives do NOT cascade — only unarchives.
        partners_to_unarchive = self.mapped("partner_id").filtered(
            lambda p: not p.active
        )
        res = super().action_unarchive()
        partners_to_unarchive.action_unarchive()
        return res

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        **kwargs,
    ):
        # **kwargs catches forward-compatible additions like saas-19.3's
        # `bypass_access`; signature-widening is the recommended OCA pattern.
        res = super()._search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            **kwargs,
        )
        # Check for args first having location_ids as default filter
        for arg in args:
            if isinstance(args, (list)):
                if arg[0] == "location_ids":
                    # If given int search ID, else search name
                    if isinstance(arg[2], int):
                        self.env.cr.execute(
                            "SELECT person_id "
                            "FROM fsm_location_person "
                            "WHERE location_id=%s",
                            (arg[2],),
                        )
                    else:
                        arg_2 = "%" + arg[2] + "%"
                        self.env.cr.execute(
                            "SELECT id "
                            "FROM fsm_location "
                            "WHERE complete_name like %s",
                            (arg_2,),
                        )
                        location_ids = self.env.cr.fetchall()
                        if location_ids:
                            location_ids = [location[0] for location in location_ids]
                            self.env.cr.execute(
                                "SELECT DISTINCT person_id "
                                "FROM fsm_location_person "
                                "WHERE location_id in %s",
                                [tuple(location_ids)],
                            )
                    workers_ids = self.env.cr.fetchall()
                    return self.browse(workers_ids)._as_query()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.update({"fsm_person": True})
        return super().create(vals_list)
