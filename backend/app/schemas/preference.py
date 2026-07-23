from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


PreferenceKind = Literal["ALLERGEN", "DIETARY_RESTRICTION", "NUTRITION_TARGET"]


class PreferenceCreate(BaseModel):
    kind: PreferenceKind
    code: str = Field(min_length=2, max_length=40, pattern=r"^[A-Za-z0-9_-]+$")
    name: str = Field(min_length=1, max_length=120)
    strength: int = Field(default=100, ge=0, le=100)


class PreferenceItem(BaseModel):
    id: int
    preference_code: str
    kind: PreferenceKind
    code: str
    name: str
    preference_type: Literal["EXCLUDE", "PREFER"]
    strength: int
    is_enabled: bool
    created_at: datetime
    updated_at: datetime
