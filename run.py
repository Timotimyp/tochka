import sys
from heapq import heappush, heappop
from itertools import count


def solve(lines: list[str]) -> int:
    """
    Решение задачи о сортировке в лабиринте

    Args:
        lines: список строк, представляющих лабиринт

    Returns:
        мин энергия для достижения целевой конфигурации
    """
    # Парсинг входных данных
    rooms = [[], [], [], []]
    room_depth = len(lines) - 3

    # Читаем комнаты снизу вверх
    for depth in range(room_depth, 0, -1):
        line = lines[depth + 1]
        for room_idx in range(4):
            pos = 3 + room_idx * 2
            if pos < len(line):
                char = line[pos]
                if char in 'ABCD':
                    rooms[room_idx].append(char)

    # Стоимость перемещения
    costs = {'A': 1, 'B': 10, 'C': 100, 'D': 1000}
    # Целевые комнаты
    target_rom = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    # Позиции входов в комнаты
    room_positions = [2, 4, 6, 8]

    # Начальное состояние: (коридор, комнаты)
    initial_hallway = tuple([None] * 11)
    initial_rooms = tuple(tuple(room) for room in rooms)
    initial_state = (initial_hallway, initial_rooms)

    # Проверка целевого состояния
    def is_goal(state):
        hallway, rooms = state
        if any(x is not None for x in hallway):
            return False
        for room_idx, room in enumerate(rooms):
            target = chr(ord('A') + room_idx)
            if len(room) != room_depth or any(x != target for x in room):
                return False
        return True

    # A* с приоритетной очередью
    counter = count()
    pq = [(0, next(counter), initial_state)]
    visited = {initial_state: 0}

    while pq:
        cost, _, state = heappop(pq)

        if cost > visited.get(state, float('inf')):
            continue

        if is_goal(state):
            return cost

        hallway, rooms = state

        # Генерация всех возможных ходов
        # 1. Перемещение из комнаты в коридор
        for room_idx in range(4):
            room = rooms[room_idx]
            if not room:
                continue

            # Проверяем, нужно ли выводить объекты из комнаты
            target = chr(ord('A') + room_idx)
            if all(x == target for x in room):
                continue

            # Берем верхний объект
            obj = room[-1]
            obj_cost = costs[obj]

            # Пробуем все позиции в коридоре
            for hall_pos in range(11):
                # Нельзя останавливаться над входами
                if hall_pos in room_positions:
                    continue

                # Проверяем путь
                room_pos = room_positions[room_idx]
                start = min(room_pos, hall_pos)
                end = max(room_pos, hall_pos)

                if any(hallway[i] is not None for i in range(start, end + 1)):
                    continue

                # Вычисляем стоимость
                # Шаги = расстояние до выхода из комнаты + расстояние по коридору
                steps_out_of_room = room_depth - len(room) + 1
                steps_in_hallway = abs(hall_pos - room_pos)
                steps = steps_out_of_room + steps_in_hallway
                move_cost = steps * obj_cost

                # Новое состояние
                new_hallway = list(hallway)
                new_hallway[hall_pos] = obj
                new_rooms = list(rooms)
                new_rooms[room_idx] = room[:-1]
                new_state = (tuple(new_hallway), tuple(tuple(r) for r in new_rooms))

                new_cost = cost + move_cost
                if new_cost < visited.get(new_state, float('inf')):
                    visited[new_state] = new_cost
                    heappush(pq, (new_cost, next(counter), new_state))

        # 2. Перемещение из коридора в комнату
        for hall_pos in range(11):
            if hallway[hall_pos] is None:
                continue

            obj = hallway[hall_pos]
            obj_cost = costs[obj]
            room_idx = target_rom[obj]
            room = rooms[room_idx]

            # Проверяем, можно ли войти в комнату
            if any(x != obj for x in room):
                continue

            if len(room) >= room_depth:
                continue

            # Проверяем путь
            room_pos = room_positions[room_idx]
            start = min(room_pos, hall_pos)
            end = max(room_pos, hall_pos)

            # Исключаем текущую позицию из проверки
            if any(hallway[i] is not None for i in range(start, end + 1) if i != hall_pos):
                continue

            # Вычисляем стоимость
            steps_in_hallway = abs(hall_pos - room_pos)
            steps_into_room = room_depth - len(room)
            steps = steps_in_hallway + steps_into_room
            move_cost = steps * obj_cost

            # Новое состояние
            new_hallway = list(hallway)
            new_hallway[hall_pos] = None
            new_rooms = list(rooms)
            new_rooms[room_idx] = room + (obj,)
            new_state = (tuple(new_hallway), tuple(tuple(r) for r in new_rooms))

            new_cost = cost + move_cost
            if new_cost < visited.get(new_state, float('inf')):
                visited[new_state] = new_cost
                heappush(pq, (new_cost, next(counter), new_state))

    return -1  # Решение не найдено


def main():
    # Чтение входных данных
    lines = []
    for line in sys.stdin:
        lines.append(line.rstrip('\n'))

    result = solve(lines)
    print(result)


if __name__ == "__main__":
    main()