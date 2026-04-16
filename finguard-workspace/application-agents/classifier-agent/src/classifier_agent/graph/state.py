from dataclasses import dataclass, field
from typing import Annotated

from langgraph.graph.message import add_messages


@dataclass
class GraphState:
    description: str = ""
    category: str = ""
    messages: Annotated[list, add_messages] = field(default_factory=list)
