from typing import Generic, TypeVar, List
from pydantic import BaseModel, ConfigDict

T = TypeVar('T')

class Page(BaseModel, Generic[T]):

    total: int
    limit: int 
    offset: int
    items: List[T]

    model_config = ConfigDict(from_attributes=True)