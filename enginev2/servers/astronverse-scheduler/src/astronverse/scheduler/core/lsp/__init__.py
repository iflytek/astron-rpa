from typing import Dict, Optional

from pydantic import BaseModel, Field

SessionId = str


class SessionOptions(BaseModel):
    type_checking_mode: Optional[str] = None
    config_overrides: Optional[Dict[str, bool]] = Field(default_factory=dict)
    locale: Optional[str] = None
    code: Optional[str] = None
    position: Optional[Dict[str, int]] = None
    newName: Optional[str] = None
    completionItem: Optional[Dict] = None
    project_id: Optional[str] = None
