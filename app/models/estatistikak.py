from enum import Enum

# from pydantic import BaseModel
# from datetime import datetime

class EstatistikaTypeEnum(str, Enum):
    cumulative = 'cumulative'
    points = 'points'
    rank = 'rank'
    ages = 'ages'
    incorporations = 'incorporations'
