"""
API models for user metric related requests
"""

from pydantic import Field, model_validator, field_validator
from api.models.base import SecureBaseModel as BaseModel
from typing import Optional
from datetime import datetime, timezone


class GlobalMetricRequest(BaseModel):
    start_time: Optional[datetime] = Field(
        default=None,
        description="Start of the time range (ISO 8601)",
        example="2026-02-18T10:00:00"
    )

    end_time: Optional[datetime] = Field(
        default=None,
        description="End of the time range (ISO 8601)",
        example="2026-02-18T12:00:00"
    )

    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of records to return (1-1000)"
    )

    offset: int = Field(
        default=0,
        ge=0,
        description="Pagination offset (>= 0)"
    )

    newest_first: bool = Field(
        default=True,
        description="Return newest records first"
    )

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.start_time and self.end_time:
            if self.start_time > self.end_time:
                raise ValueError("start_time must be before end_time")
        return self

    @field_validator("start_time", "end_time")
    def prevent_future_dates(cls, value):
        if value and value > datetime.now(timezone.utc):
            raise ValueError("Datetime cannot be in the future")
        return value

class RouteMetricsRequest(BaseModel):
    route: Optional[str] = Field(
        default=None,
        max_length=255,
        pattern=r"^/.*",
        description="Filter metrics for a specific API route (must start with /)",
        example="/api/v1/users"
    )

    start: Optional[datetime] = Field(
        default=None,
        description="Start of the time range (ISO 8601)",
        example="2026-02-18T10:00:00"
    )

    end: Optional[datetime] = Field(
        default=None,
        description="End of the time range (ISO 8601)",
        example="2026-02-18T12:00:00"
    )

    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of rows returned (1-1000)"
    )

    cursor: Optional[datetime] = Field(
        default=None,
        description="Cursor for time-based pagination. Returns records older than this timestamp.",
        example="2026-02-18T11:59:00"
    )

    @model_validator(mode="after")
    def validate_logic(self):
        # start <= end
        if self.start and self.end:
            if self.start > self.end:
                raise ValueError("start must be before end")

        # cursor should not be used together with start > cursor
        if self.cursor and self.start:
            if self.cursor < self.start:
                raise ValueError("cursor cannot be older than start")

        return self

    @field_validator("start", "end", "cursor")
    def prevent_future_dates(cls, value):
        if value and value > datetime.now(timezone.utc):
            raise ValueError("Datetime cannot be in the future")
        return value

class RouteStatusCodeMetricsRerquest(BaseModel):
    route: Optional[str] = Field(
        default=None,
        max_length=255,
        pattern=r"^/.*",
        description="Filter metrics for a specific API route",
        example="/api/v1/users"
    )

    status_code: Optional[int] = Field(
        default=None,
        ge=100,
        le=599,
        description="Filter by HTTP status code",
        example=404
    )

    start_time: Optional[datetime] = Field(
        default=None,
        description="Start of the time range (ISO 8601)",
        example="2026-02-18T10:00:00"
    )

    end_time: Optional[datetime] = Field(
        default=None,
        description="End of the time range (ISO 8601)",
        example="2026-02-18T12:00:00"
    )

    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of rows returned (1-1000)"
    )

    offset: int = Field(
        default=0,
        ge=0,
        description="Pagination offset"
    )

    newest_first: bool = Field(
        default=True,
        description="Return newest records first"
    )

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.start_time and self.end_time:
            if self.start_time > self.end_time:
                raise ValueError("start_time must be before end_time")
        return self

    @field_validator("start_time", "end_time")
    def prevent_future_dates(cls, value):
        if value and value > datetime.now(timezone.utc):
            raise ValueError("Datetime cannot be in the future")
        return value