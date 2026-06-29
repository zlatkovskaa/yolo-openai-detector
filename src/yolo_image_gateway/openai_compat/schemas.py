"""OpenAI-compatible request and response schemas."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class ChatMessageTextContent(BaseModel):
    type: Literal["text"] = "text"
    text: str


class ChatMessageImageURL(BaseModel):
    url: str


class ChatMessageImageContent(BaseModel):
    type: Literal["image_url"] = "image_url"
    image_url: ChatMessageImageURL


ChatMessageContent = Annotated[
    ChatMessageTextContent | ChatMessageImageContent,
    Field(discriminator="type"),
]


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    role: str
    content: list[ChatMessageContent]


class ChatCompletionRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    model: str
    messages: list[ChatMessage]


class ModelObject(BaseModel):
    id: str
    object: Literal["model"] = "model"
    created: int
    owned_by: str = "local"


class ModelListResponse(BaseModel):
    object: Literal["list"] = "list"
    data: list[ModelObject]


class ChatCompletionMessage(BaseModel):
    role: Literal["assistant"] = "assistant"
    content: str


class ChatCompletionChoice(BaseModel):
    index: int = 0
    message: ChatCompletionMessage
    finish_reason: Literal["stop"] = "stop"


class ChatCompletionResponse(BaseModel):
    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: list[ChatCompletionChoice]
