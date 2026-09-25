from dataclasses import dataclass
from typing import Optional
from app.utils.constants import MAX_CALLBACK_DATA_LENGTH


@dataclass(frozen=True, slots=True)
class CallbackData:
    prefix: str
    action: str
    identifier: str | None = None
    extra: str | None = None

    def serialize(self) -> str:
        parts = [self.prefix, self.action]
        if self.identifier:
            parts.append(self.identifier)
        if self.extra:
            parts.append(self.extra)
        data = ":".join(parts)
        if len(data) > MAX_CALLBACK_DATA_LENGTH:
            raise ValueError(f"Callback data exceeds {MAX_CALLBACK_DATA_LENGTH} characters: {data}")
        return data

    @classmethod
    def parse(cls, data: str) -> "CallbackData":
        parts = data.split(":")
        if len(parts) < 2:
            raise ValueError(f"Invalid callback data format: {data}")

        prefix = parts[0]
        action = parts[1]
        identifier = parts[2] if len(parts) > 2 else None
        extra = parts[3] if len(parts) > 3 else None

        return cls(prefix=prefix, action=action, identifier=identifier, extra=extra)


def create_callback(prefix: str, action: str, identifier: str | int | None = None, extra: str | None = None) -> str:
    return CallbackData(prefix=prefix, action=action, identifier=str(identifier) if identifier else None, extra=extra).serialize()


def parse_callback(data: str) -> CallbackData:
    return CallbackData.parse(data)