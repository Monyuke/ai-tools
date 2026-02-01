# src/ai_tools/page_modules/ask/state.py
from dataclasses import dataclass
from ai_tools.lib.st.state_manager import StateManager, BaseModel
from pydantic import BaseModel, Field

class AppState(BaseModel):
    ai_message: str = Field(default="")
    user_input: str = Field(default="")
    file_paths_input: str = Field(default="")
    sourcemap_paths_input: str = Field(default="")

# StateManager を使って session_state を管理
state_manager = StateManager[AppState](
    key="ask_state",
    model_cls=AppState
)