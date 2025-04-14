import heapq

def solve_tsp(graph_nodes, graph_edges):
    if not graph_nodes:
        return [], 0

    # Строим матрицу смежности
    node_count = len(graph_nodes)
    node_index = {node: idx for idx, node in enumerate(graph_nodes)}
    adj_matrix = [[False]*node_count for _ in range(node_count)]
    
    for edge in graph_edges:
        i, j = node_index[edge[0]], node_index[edge[1]]
        adj_matrix[i][j] = True
        adj_matrix[j][i] = True

    # Алгоритм ветвей и границ
    n = node_count
    min_distance = float('inf')
    best_path = None
    
    # Стартуем с первого узла (индекс 0)
    heap = []
    heapq.heappush(heap, (0, 0, [True] + [False]*(n-1), [0], 0))

    while heap:
        _, current, visited, path, cost = heapq.heappop(heap)
        
        # Все узлы посещены - проверяем возврат в старт
        if len(path) == n:
            if adj_matrix[current][0]:  # Есть обратное ребро
                total_cost = cost + 1
                if total_cost < min_distance:
                    min_distance = total_cost
                    best_path = path
            continue
        
        # Добавляем непосещённых соседей
        for neighbor in range(n):
            if adj_matrix[current][neighbor] and not visited[neighbor]:
                new_visited = visited.copy()
                new_visited[neighbor] = True
                heapq.heappush(heap, (
                    cost + 1,  # Приоритет
                    neighbor,
                    new_visited,
                    path + [neighbor],
                    cost + 1  # Фактическая стоимость
                ))
    
    if not best_path:
        return [], 0
    
    # Преобразуем индексы в исходные узлы (без дублирования старта)
    result_path = [graph_nodes[i] for i in best_path]
    return result_path, min_distance


# Тесты
if __name__ == "__main__":
    # Пример 1:
    nodes = [1, 2, 3, 4]
    edges = [[1,2],[2,3],[3,4],[4,1],[1,3]]
    path, dist = solve_tsp(nodes, edges)
    print(f"Путь: {path}, Расстояние: {dist}")
    
    # Пример 2: 
    nodes = [1, 2, 3, 4, 5]
    edges = [[1,2],[1,3],[3,4],[2,5],[4,5],[1,5]]
    path, dist = solve_tsp(nodes, edges)
    print(f"Путь: {path}, Расстояние: {dist}")