import uuid
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator


class Category(str, Enum):
    authentication = "authentication"
    authorization = "authorization"
    injection = "injection"
    container_security = "container_security"
    dependency_security = "dependency_security"
    iam = "IAM"
    network_configuration = "network_configuration"
    cloud_security = "cloud_security"
    iac = "IaC"
    secrets = "secrets"
    cryptography = "cryptography"
    other = "other"


class DecisionCreate(BaseModel):
    organization_id: uuid.UUID | None = None
    user_id: uuid.UUID
    model_id: uuid.UUID
    title: str = Field(min_length=3, max_length=200)
    prompt: str | None = Field(default=None, max_length=100000)
    recommendation_text: str = Field(min_length=10, max_length=100000)
    diff_content: str = Field(min_length=1, max_length=500000)
    category: Category
    affected_files: list[str] = Field(min_length=1, max_length=100)

    @field_validator("title", "recommendation_text")
    @classmethod
    def strip_required(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Must not be blank")
        return value

    @field_validator("diff_content")
    @classmethod
    def nonempty_diff(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Diff must not be blank")
        return value

    @field_validator("affected_files")
    @classmethod
    def safe_paths(cls, paths: list[str]) -> list[str]:
        normalized = []
        for path in paths:
            path = path.strip().replace("\\", "/")
            if not path or path.startswith("/") or any(part in ("", ".", "..") for part in path.split("/")) or len(path) > 500:
                raise ValueError("Affected files must be relative paths without traversal")
            normalized.append(path)
        return sorted(set(normalized))


class DecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    organization_id: uuid.UUID | None = Field(validation_alias="org_id")
    user_id: uuid.UUID
    model_id: uuid.UUID
    model_name: str | None = None
    title: str | None
    category: str
    prompt_hash: str
    recommendation_text: str
    diff_content: str | None
    affected_files: list[str]
    status: str
    created_at: datetime
    prev_hash: str | None
    row_hash: str


class DecisionPage(BaseModel):
    items: list[DecisionResponse]
    page: int
    page_size: int
    total: int
