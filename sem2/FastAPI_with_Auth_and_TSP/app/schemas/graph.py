from pydantic import BaseModel
from typing import List, Tuple

class Graph(BaseModel):
    nodes: List[int]
    edges: List[Tuple[int, int]]

class PathResult(BaseModel):
    path: List[int]
    total_distance: float