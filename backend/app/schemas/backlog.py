from pydantic import BaseModel


class BacklogItem(BaseModel):
    id: str
    title: str
    type: str
    status: str
    priority: str
