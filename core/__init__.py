"""
AutoмataLol - Core Module
Componentes principales del sistema
"""

from .constants import *
from .exceptions import *
from .events import get_event_bus, EventBus, EventType

__all__ = [
    "get_event_bus",
    "EventBus",
    "EventType",
]
