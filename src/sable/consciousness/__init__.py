"""
Three-level consciousness implementation based on Antonio Damasio's framework.

Modules:
- proto_self: Body state representation and homeostatic regulation
- core_consciousness: Emotions, feelings, and somatic markers
- extended_consciousness: Autobiographical memory and narrative self
"""

from sable.consciousness.proto_self import ProtoSelf
from sable.consciousness.core_consciousness import CoreConsciousness
from sable.consciousness.extended_consciousness import ExtendedConsciousness

__all__ = [
    "ProtoSelf",
    "CoreConsciousness",
    "ExtendedConsciousness",
]
