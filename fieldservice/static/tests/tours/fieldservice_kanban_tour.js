/**
 * Test-only tour (web.assets_tests, run by tests/test_ui.py): the team dashboard
 * and the order board of Field Service render and their card menus open.
 *
 * Written for the 20.0 port. The order board coloured its cards with
 * kanban_color(), which the 19.x/20.0 kanban no longer defines, so every card
 * threw; and the card menus were declared as "kanban-menu", a name the kanban
 * never reads, so the colour picker and the Edit/Configuration links never showed.
 */
import {registry} from "@web/core/registry";

const openCardMenu = (card) => ({
    trigger: `.o_kanban_record:contains(${card})`,
    run: `hover && click .o_kanban_record:contains(${card}) .o_dropdown_kanban .dropdown-toggle`,
});

registry.category("web_tour.tours").add("fieldservice.kanban_views_tour", {
    steps: () => [
        // Team dashboard: the manager's card menu
        {trigger: ".o_fsm_team_kanban .o_kanban_record:contains(FSM Tour Team)"},
        openCardMenu("FSM Tour Team"),
        {trigger: ".o-dropdown--kanban-record-menu .o_kanban_colorpicker"},
        {
            trigger: ".o-dropdown--kanban-record-menu a:contains(Configuration)",
            run: "press Escape",
        },
        {trigger: "body:not(:has(.o-dropdown--kanban-record-menu))"},
        // -> the team's orders
        {
            trigger: ".o_kanban_record:contains(FSM Tour Team) button:contains(To Do)",
            run: "click",
        },
        // Order board: the card renders, its menu has the colour picker and Edit
        {trigger: ".o_kanban_view .o_kanban_record:contains(FSM Tour Order)"},
        openCardMenu("FSM Tour Order"),
        {trigger: ".o-dropdown--kanban-record-menu .o_kanban_colorpicker"},
        {trigger: ".o-dropdown--kanban-record-menu a:contains(Edit)", run: "click"},
        {trigger: ".o_form_view .o_field_widget[name=name]:contains(FSM Tour Order)"},
    ],
});
