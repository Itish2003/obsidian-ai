from typing import Any
from pydantic import BaseModel

class RunRequest(BaseModel):
    app_name: str
    user_id: str
    session_id: str
    new_message: str

class Event(BaseModel):
    type: str
    content: Any
    is_final_response: bool = False