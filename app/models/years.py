from pydantic import BaseModel

class Year(BaseModel):
    name: str
    years: list[int]


class YearPutModel(BaseModel):
    urteak: list[int]