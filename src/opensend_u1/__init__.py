"""OpenSend U1 — OrcaSlicer plugin entry point.

OrcaSlicer imports this package and looks for exactly one class decorated with
@orca.plugin. Its register_capabilities() announces every capability the plugin offers.
"""

import orca

from .capability import ToolheadMapping

__all__ = ["OpenSendU1"]


@orca.plugin
class OpenSendU1(orca.base):
    def register_capabilities(self):
        orca.register_capability(ToolheadMapping)
