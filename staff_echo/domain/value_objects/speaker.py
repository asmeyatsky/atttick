"""
Speaker Value Object

Architectural Intent:
- Identifies participants in voice recordings
- SpeakerRole distinguishes staff (training source) from customers
- Used by speaker diarization to tag transcript segments
"""

from dataclasses import dataclass
from enum import Enum


class SpeakerRole(Enum):
    STAFF = "staff"
    CUSTOMER = "customer"


@dataclass(frozen=True)
class Speaker:
    id: str
    name: str
    role: SpeakerRole
