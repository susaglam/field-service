Adds a *change journal* to every Field Service location so dispatchers,
technicians, and customers can track what has changed at a site over time. Each
entry records:

- **Title + description** — what was changed
- **Location** — which FSM location the change happened at
- **Stage** — Draft → In Progress → Implemented → Closed
- **Impact** — Minor / Moderate / Major / Critical
- **Type** — Structural / Electrical / Plumbing / HVAC / Configuration / etc.
- **Tags** — free-text labels for filtering
- **Implemented On** — when the change actually went live
- **User** — who logged the change

Typical use cases:

- After a renovation: log what was replaced or added so the next technician knows
  the current site state.
- Audit trail for warranty / liability cases — printable PDF reports per location
  summarise every change.
- Customer-facing change history: "here is everything we have done at your site
  since 2023".

The module is NOT ITIL-style IT change management; this is a *site change journal*
tied to FSM locations.
