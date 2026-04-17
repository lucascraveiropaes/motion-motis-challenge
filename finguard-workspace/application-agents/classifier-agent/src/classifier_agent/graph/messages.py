from typing import Annotated, Literal

from pydantic import BaseModel, Field


class SimpleMessage(BaseModel):
    type: Literal["simple"] = "simple"
    message: str


class ChatMessage(BaseModel):
    type: Literal["chat"] = "chat"
    role: Literal["assistant", "user", "system"] = "assistant"
    message: str


class DraftOrderMessage(BaseModel):
    type: Literal["draft_order"] = "draft_order"
    draft_id: str
    message: str
    requires_human_input: bool = True


class OrderMessage(BaseModel):
    type: Literal["order"] = "order"
    order_id: str
    status: Literal["approved", "rejected"]
    category: str


StreamMessage = Annotated[
    SimpleMessage | ChatMessage | DraftOrderMessage | OrderMessage,
    Field(discriminator="type"),
]
