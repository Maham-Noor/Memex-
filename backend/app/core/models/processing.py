from pydantic import BaseModel
from typing import List


class ContentChunk(BaseModel):
    chunkId: str
    text: str
    tokenCount: int
    embedding: List[float]
    category: str


class ProcessingResult(BaseModel):
    captureId: str
    category: str
    chunkCount: int
    chunks: List[ContentChunk]
