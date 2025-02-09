from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SessionType(Enum):
    IN_MEMORY = "in_memory"
    REDIS = "redis"


class SessionConfigInMemory(BaseModel):
    pass


class SessionConfigRedis(BaseModel):
    class Config:
        extra = "allow"

    host: str = Field(default="localhost")
    port: int = Field(default=6379)
    db: int = Field(default=0)


class SessionConfig(BaseModel):
    session_type: SessionType
    in_memory: Optional[SessionConfigInMemory] = Field(
        default_factory=SessionConfigInMemory
    )
    redis: Optional[SessionConfigRedis] = Field(default_factory=SessionConfigRedis)


DefaultSessionConfig = SessionConfig(
    session_type=SessionType.IN_MEMORY,
    in_memory=SessionConfigInMemory(),
    redis=SessionConfigRedis(),
)
