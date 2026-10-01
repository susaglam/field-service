# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# Models first, MCP last: fsm_stage_status_mcp extends fsm.order, and importing it
# before fsm_stage made the registry initialise fsm.order's NOT NULL sub_stage_id
# (default read from fsm.stage.sub_stage_id) before that column existed. On a
# database that already had orders the install died with UndefinedColumn.
from . import fsm_stage_status, fsm_stage, fsm_order, fsm_stage_status_mcp
