from datetime import datetime

from pydantic import BaseModel, Field


class AddressWrite(BaseModel):
    receiver_name: str = Field(min_length=1, max_length=80)
    receiver_phone: str = Field(min_length=6, max_length=32)
    province: str = Field(min_length=1, max_length=64)
    city: str = Field(min_length=1, max_length=64)
    district: str = Field(min_length=1, max_length=64)
    detail_address: str = Field(min_length=1, max_length=255)
    postal_code: str | None = Field(default=None, max_length=16)
    is_default: bool = False


class AddressCreate(AddressWrite):
    pass


class AddressUpdate(AddressWrite):
    pass


class AddressItem(AddressWrite):
    address_code: str
    created_at: datetime
    updated_at: datetime
