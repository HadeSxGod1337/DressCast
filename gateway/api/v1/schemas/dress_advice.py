"""Dress advice schemas."""

from pydantic import BaseModel


class DressAdviceResponse(BaseModel):
    advice_text: str
