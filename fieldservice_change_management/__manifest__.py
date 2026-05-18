# Copyright (c) 2020 Pavlov Media <https://www.pavlovmedia.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Location Change Journal",
    "summary": (
        "Track structural and configuration changes at Field Service "
        "locations over time. Site change journal / audit trail."
    ),
    "description": """
Field Service - Location Change Journal
=======================================

Adds a *change journal* to every Field Service location so dispatchers,
technicians, and customers can track what has changed at a site over
time. Each entry records:

* **Title + description** — what was changed
* **Location** — which FSM location the change happened at
* **Stage** — Draft → In Progress → Implemented → Closed
* **Impact** — Minor / Moderate / Major / Critical
* **Type** — Structural / Electrical / Plumbing / HVAC / Configuration / etc.
* **Tags** — free-text labels for filtering
* **Implemented On** — when the change actually went live
* **User** — who logged the change

Typical use cases:

- After a renovation: log what was replaced or added so the next
  technician knows the current site state.
- Audit trail for warranty / liability cases — printable PDF reports
  per location summarise every change.
- Customer-facing change history: "here is everything we have done at
  your site since 2023".

The module is NOT ITIL-style IT change management; this is a *site
change journal* tied to FSM locations.
""",
    "author": "Pavlov Media, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "category": "Field Service",
    "version": "saas~19.3.1.0.4",
    "license": "AGPL-3",
    "depends": [
        "fieldservice",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "data/change_log_impact.xml",
        "data/change_log_stage.xml",
        "data/change_log_type.xml",
        "report/change_log_reports.xml",
        "views/change_log.xml",
        "views/change_log_impact.xml",
        "views/change_log_stage.xml",
        "views/change_log_tags.xml",
        "views/change_log_type.xml",
        "views/fsm_location.xml",
    ],
    "application": True,
    "development_status": "Beta",
    "maintainers": ["patrickrwilson"],
}
