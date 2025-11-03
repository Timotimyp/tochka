import sys
from collections import deque, defaultdict


def solve(edges: list[tuple[str, str]]) -> list[str]:
    """
    Решение задачи об изоляции вируса

    Args:
        edges: список коридоров в формате (узел1, узел2)

    Returns:
        список отключаемых коридоров в формате "Шлюз-узел"
    """

    # Построение графа
    graph = defaultdict(set)
    gateways = set()
    nodes = set()

    for node1, node2 in edges:
        graph[node1].add(node2)
        graph[node2].add(node1)
        nodes.add(node1)
        nodes.add(node2)

        # Определяем шлюзы (заглавные буквы)
        if node1.isupper():
            gateways.add(node1)
        if node2.isupper():
            gateways.add(node2)

    result = []
    virus_pos = 'a'

    def bfs_distance(start, graph):
        """BFS для нахождения кратчайших расстояний от start до всех узлов"""
        distances = {start: 0}
        queue = deque([start])

        while queue:
            node = queue.popleft()
            for neighbor in sorted(graph[node]):  # Сортируем для детерминированности
                if neighbor not in distances:
                    distances[neighbor] = distances[node] + 1
                    queue.append(neighbor)

        return distances

    def find_next_move(virus_pos, graph, gateways):
        """Находит следующий узел, куда переместится вирус"""
        distances = bfs_distance(virus_pos, graph)

        # Находим ближайший шлюз
        min_dist = float('inf')
        target_gateway = None

        for gateway in sorted(gateways):  # Лексикографический порядок
            if gateway in distances:
                if distances[gateway] < min_dist:
                    min_dist = distances[gateway]
                    target_gateway = gateway

        if target_gateway is None or min_dist == float('inf'):
            return None

        # Если вирус рядом со шлюзом
        if min_dist == 1:
            return target_gateway

        # Находим следующий узел на пути к целевому шлюзу
        # Используем BFS от целевого шлюза обратно
        gateway_distances = bfs_distance(target_gateway, graph)

        # Выбираем соседа вируса, который ближе всего к шлюзу
        best_neighbor = None
        best_dist = float('inf')

        for neighbor in sorted(graph[virus_pos]):  # Лексикографический порядок
            if neighbor in gateway_distances:
                if gateway_distances[neighbor] < best_dist:
                    best_dist = gateway_distances[neighbor]
                    best_neighbor = neighbor

        return best_neighbor

    def find_critical_edge(virus_pos, graph, gateways):
        """Находит критический коридор для отключения"""
        # Находим все коридоры gateway-node
        gateway_edges = []

        for gateway in sorted(gateways):
            for node in sorted(graph[gateway]):
                if not node.isupper():  # Только обычные узлы
                    gateway_edges.append((gateway, node))

        # Сортируем лексикографически
        gateway_edges.sort()

        # Проверяем каждый коридор
        for gateway, node in gateway_edges:
            # Временно удаляем коридор
            graph[gateway].discard(node)
            graph[node].discard(gateway)

            # Проверяем, может ли вирус достичь какого-либо шлюза
            distances = bfs_distance(virus_pos, graph)
            can_reach = any(g in distances for g in gateways)

            # Восстанавливаем коридор
            graph[gateway].add(node)
            graph[node].add(gateway)

            # Если после удаления этого коридора вирус все еще может достичь шлюза,
            # но это приведет к правильному решению, выбираем его
            if can_reach:
                # Симулируем дальнейшее развитие
                test_graph = defaultdict(set)
                for n in graph:
                    test_graph[n] = graph[n].copy()

                test_graph[gateway].discard(node)
                test_graph[node].discard(gateway)

                # Проверяем следующий ход вируса
                next_pos = find_next_move(virus_pos, test_graph, gateways)

                if next_pos and not next_pos.isupper():
                    return (gateway, node)
            else:
                # Если вирус не может достичь ни одного шлюза, это хороший выбор
                return (gateway, node)

        # Возвращаем первый доступный коридор
        return gateway_edges[0] if gateway_edges else None

    # Основной цикл
    while True:
        # Проверяем, может ли вирус достичь какого-либо шлюза
        distances = bfs_distance(virus_pos, graph)
        reachable_gateways = [g for g in gateways if g in distances]

        if not reachable_gateways:
            break

        # Находим критический коридор для отключения
        edge = find_critical_edge(virus_pos, graph, gateways)

        if edge is None:
            break

        gateway, node = edge

        # Отключаем коридор
        graph[gateway].discard(node)
        graph[node].discard(gateway)

        result.append(f"{gateway}-{node}")

        # Перемещаем вирус
        next_pos = find_next_move(virus_pos, graph, gateways)

        if next_pos is None:
            break

        virus_pos = next_pos

        # Если вирус достиг шлюза, что-то пошло не так
        if virus_pos.isupper():
            break

    return result


def main():
    edges = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            node1, sep, node2 = line.partition('-')
            if sep:
                edges.append((node1, node2))

    result = solve(edges)
    for edge in result:
        print(edge)


if __name__ == "__main__":
    main()