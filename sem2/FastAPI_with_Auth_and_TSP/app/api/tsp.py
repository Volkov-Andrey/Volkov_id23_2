from fastapi import APIRouter
from app.schemas.graph import Graph, PathResult
from app.services.tsp import solve_tsp

router = APIRouter()

@router.post("/shortest-path/", response_model=PathResult)
def find_shortest_path(graph: Graph):
    return solve_tsp(graph)