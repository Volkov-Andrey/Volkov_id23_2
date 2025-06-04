from typing import List, Tuple
from fastapi import HTTPException
from app.schemas.graph import Graph, PathResult

def branch_and_bound_tsp(graph: Graph) -> PathResult:
    nodes = graph.nodes
    edges = graph.edges
    n = len(nodes)

    # Проверка входных данных
    if not nodes or not edges:
        raise HTTPException(status_code=400, detail="Nodes or edges cannot be empty")
    if min(nodes) < 1:
        raise HTTPException(status_code=400, detail="Node indices must be positive integers")

    # Создание матрицы смежности
    distance_matrix = [[float('inf')] * n for _ in range(n)]
    for i, j in edges:
        if i not in nodes or j not in nodes:
            raise HTTPException(status_code=400, detail=f"Invalid edge ({i}, {j}): nodes not in graph")
        distance_matrix[nodes.index(i)][nodes.index(j)] = 1.0
        distance_matrix[nodes.index(j)][nodes.index(i)] = 1.0  # Ненаправленный граф

    min_distance = float('inf')
    best_route = None

    def tsp(node_index, visited, cost, path):
        nonlocal min_distance, best_route

        # Если посетили все узлы
        if len(path) == n:
            # Проверяем возможность возврата к начальному узлу
            return_cost = distance_matrix[node_index][start_index]
            if return_cost != float('inf'):
                total_cost = cost + return_cost
                if total_cost < min_distance:
                    min_distance = total_cost
                    best_route = path[:]
            return

        # Перебираем все возможные следующие узлы
        for next_node_index in range(n):
            if not visited[next_node_index] and distance_matrix[node_index][next_node_index] != float('inf'):
                visited[next_node_index] = True
                tsp(next_node_index, visited, cost + distance_matrix[node_index][next_node_index], path + [nodes[next_node_index]])
                visited[next_node_index] = False

    # Начинаем с первого узла
    start_index = 0  # Индекс первого узла
    visited = [False] * n
    visited[start_index] = True
    tsp(start_index, visited, 0, [nodes[start_index]])

    if not best_route:
        raise HTTPException(status_code=400, detail="No valid Hamiltonian cycle exists")

    # Добавляем возврат к начальному узлу
    best_route.append(nodes[start_index])
    return PathResult(path=best_route, total_distance=float(min_distance))

def solve_tsp(graph: Graph) -> PathResult:
    return branch_and_bound_tsp(graph)