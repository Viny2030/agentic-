"""
Suite de herramientas de control para Claude
"""
from .omni_route import tool_omni_route, schema_omni_route
from .claude_mem import tool_claude_mem, schema_claude_mem
from .headroom import tool_headroom, schema_headroom
from .claude_code_setup import tool_claude_code_setup, schema_claude_code_setup
from .task_observer import tool_task_observer, schema_task_observer

CONTROL_TOOLS_MAP = {
    "tool_omni_route": tool_omni_route,
    "tool_claude_mem": tool_claude_mem,
    "tool_headroom": tool_headroom,
    "tool_claude_code_setup": tool_claude_code_setup,
    "tool_task_observer": tool_task_observer
}

CONTROL_SCHEMAS = [
    schema_omni_route,
    schema_claude_mem,
    schema_headroom,
    schema_claude_code_setup,
    schema_task_observer
]
