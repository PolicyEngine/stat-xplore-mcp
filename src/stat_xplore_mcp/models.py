"""Pydantic models for Stat-Xplore API."""

from pydantic import BaseModel, Field


class SchemaItem(BaseModel):
    """A schema item (folder or database)."""

    id: str
    label: str
    location: str
    type: str | None = None
    children: list["SchemaItem"] | None = None


class RateLimitInfo(BaseModel):
    """Rate limit status."""

    limit: int
    remaining: int
    reset_timestamp: int


class FieldItem(BaseModel):
    """A field value item."""

    type: str | None = None
    labels: list[str] = Field(default_factory=list)
    uris: list[str] = Field(default_factory=list)


class FieldInfo(BaseModel):
    """Field information in query results."""

    uri: str
    label: str
    items: list[FieldItem] = Field(default_factory=list)


class MeasureInfo(BaseModel):
    """Measure information."""

    uri: str
    label: str


class CubeData(BaseModel):
    """Cube data with values and precision."""

    values: list
    precision: int = 0


class TableQueryResponse(BaseModel):
    """Response from a table query."""

    fields: list[FieldInfo] = Field(default_factory=list)
    measures: list[MeasureInfo] = Field(default_factory=list)
    cubes: dict[str, CubeData] = Field(default_factory=dict)
    database: dict | None = None


class TableQuery(BaseModel):
    """A table query request."""

    database: str
    measures: list[str]
    dimensions: list[list[str]]
    recodes: dict[str, dict] | None = None


class RecodeMap(BaseModel):
    """Recode specification for filtering/grouping."""

    map: list[list[str]]
    total: bool = False
