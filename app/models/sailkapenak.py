from pydantic import BaseModel
from .estropadak import EstropadaTypeEnum


class Rower(BaseModel):
    altak: int
    bajak: int


class Age(BaseModel):
    min_age: float
    max_age: float
    avg_age: float


class Rank(BaseModel):
    best: int
    worst: int
    wins: int
    points: float
    position: int
    positions: list[int]
    cumulative: list[float]
    rowers: Rower = Rower(altak=0, bajak=0)
    age: Age = Age(min_age=0, avg_age=0, max_age=0)


class TeamRank(BaseModel):
    name: str
    value: Rank


class Sailkapena(BaseModel):
    id: str | None = None
    stats: list[TeamRank] = []
    league: EstropadaTypeEnum
    year: int


class SailkapenakModel(BaseModel):
    id: str
    stats: list[TeamRank] = []


class SailkapenakList(BaseModel):
    docs: list[Sailkapena]
    total: int
