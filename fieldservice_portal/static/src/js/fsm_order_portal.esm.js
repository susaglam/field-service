/** @odoo-module **/

// Keep the Work Orders card on the portal home page even when the counter is
// zero, so a customer whose work is finished can still find their history.
//
// Ported to saas-19.4 on 2026-07-30. Three things changed at once, and the old
// code failed on the first of them:
//
//   path    @portal/js/portal            -> @portal/interactions/portal_home_counters
//   method  _getCountersAlwaysDisplayed  -> getCountersAlwaysDisplayed (no underscore)
//   extend  PortalHomeCounters.include() -> patch(PortalHomeCounters.prototype)
//
// The root cause of all three is that PortalHomeCounters is no longer a Widget
// but a public Interaction, and `.include()` is the pre-OWL Widget API. With the
// import unresolvable the whole module was dropped, so EVERY portal page on the
// site logged two asset-loader errors:
//
//   missing:  ["@portal/js/portal"]
//   unloaded: ["@fieldservice_portal/js/fsm_order_portal.esm"]
//
// cs_dealer_portal/static/src/js/dealer_portal_home.esm.js already had the
// correct shape; this is the same pattern.

import { patch } from "@web/core/utils/patch";
import { PortalHomeCounters } from "@portal/interactions/portal_home_counters";

patch(PortalHomeCounters.prototype, {
    getCountersAlwaysDisplayed() {
        return [...super.getCountersAlwaysDisplayed(), "fsm_order_count"];
    },
});
