import sys
import math
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTreeWidget, QTreeWidgetItem, QInputDialog)
from PyQt5.QtGui import QPainter, QPen, QBrush
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtCore import pyqtSignal




class Vertex:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y


class Edge:
    def __init__(self, start_vertex, end_vertex, weight):
        self.start_vertex = start_vertex
        self.end_vertex = end_vertex
        self.weight = weight


class GraphWidget(QWidget):
    edge_added = pyqtSignal()

    def __init__(self, is_output=False):
        super().__init__()
        self.vertices = []
        self.edges = []
        self.selected_vertex = None
        self.min_distance = 50
        self.vertex_counter = 0
        self.removed_vertices = []
        self.action_stack = []
        self.is_output = is_output

    def add_vertex(self, x, y):
        if self.removed_vertices:
            vertex_id = min(self.removed_vertices)
            self.removed_vertices.remove(vertex_id)
        else:
            self.vertex_counter += 1
            vertex_id = self.vertex_counter

        for vertex in self.vertices:
            distance = math.sqrt((x - vertex.x) ** 2 + (y - vertex.y) ** 2)
            if distance < self.min_distance:
                return

        vertex = Vertex(vertex_id, x, y)
        self.vertices.append(vertex)
        self.action_stack.append(("vertex", vertex))
        self.update()

    def select_vertex_for_edge(self, x, y):
        try:
            print("Начало select_vertex_for_edge")
            for vertex in self.vertices:
                print(f"Проверка вершины {vertex.id} на расстояние")
                distance = math.sqrt((x - vertex.x) ** 2 + (y - vertex.y) ** 2)
                if distance < 20:
                    print(f"Вершина {vertex.id} находится в радиусе")
                    if self.selected_vertex is None:
                        print(f"Выбрана вершина {vertex.id} для начала ребра")
                        self.selected_vertex = vertex
                        self.update()
                        return
                    else:
                        if self.selected_vertex != vertex:
                            print(f"Попытка создать ребро между {self.selected_vertex.id} и {vertex.id}")
                            edge_exists = False
                            edge_index = -1

                            for idx, edge in enumerate(self.edges):
                                if (edge.start_vertex.id == self.selected_vertex.id and
                                        edge.end_vertex.id == vertex.id):
                                    edge_exists = True
                                    edge_index = idx
                                    break

                            if edge_exists:
                                print(f"Ребро уже существует, индекс {edge_index}")
                                current_weight = self.edges[edge_index].weight
                                new_weight, ok = QInputDialog.getInt(self, "Вес рёбра",
                                                                     f"Ребро между {self.selected_vertex.id} и {vertex.id} уже существует. Текущий вес: {current_weight}\nВведите новый вес:",
                                                                     current_weight)
                                if ok:
                                    print(f"Обновление веса ребра на {new_weight}")
                                    old_edge = self.edges[edge_index]
                                    self.edges[edge_index].weight = new_weight
                                    self.action_stack.append(("weight_change", old_edge, self.edges[edge_index]))
                                    self.update()

                                self.selected_vertex = None
                                self.update()
                                self.edge_added.emit()
                                return

                            print("Запрос веса ребра")
                            weight, ok = QInputDialog.getInt(self, "Вес рёбра",
                                                             f"Введите вес рёбра от {self.selected_vertex.id} до {vertex.id}:")
                            if not ok:
                                print("Пользователь отменил ввод веса")
                                return

                            print(f"Создание ребра с весом {weight}")
                            if self.selected_vertex is None or vertex is None:
                                print("Ошибка: одна из вершин равна None")
                                return

                            edge = Edge(self.selected_vertex, vertex, weight)
                            if edge is None:
                                print("Ошибка: не удалось создать ребро")
                                return

                            self.edges.append(edge)
                            if edge not in self.edges:
                                print("Ошибка: ребро не добавлено в список")
                                return

                            self.action_stack.append(("edge", edge))
                            if ("edge", edge) not in self.action_stack:
                                print("Ошибка: действие не добавлено в стек")
                                return
                            try:
                                self.update()
                                print("Виджет успешно обновлен")
                            except Exception as e:
                                print(f"Ошибка при обновлении виджета: {e}")
                                return

                            self.selected_vertex = None
                            self.update()
                            self.edge_added.emit()
                            return
                        else:
                            print("Выбрана та же вершина, сброс выбора")
                            self.selected_vertex = None
                            self.update()
        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def paintEvent(self, event):
        try:
            print("Начало paintEvent")
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(QPen(Qt.black, 2, Qt.DashLine))
            painter.drawRect(10, 10, self.width() - 20, self.height() - 20)
            print(f"Количество рёбер: {len(self.edges)}")
            for edge in self.edges:
                if edge is None:
                    print("Ошибка: ребро равно None")
                    continue
                if edge.start_vertex is None or edge.end_vertex is None:
                    print("Ошибка: одна из вершин ребра равна None")
                    continue
                print(f"Отрисовка ребра между {edge.start_vertex.id} и {edge.end_vertex.id}")
                self.draw_directed_edge(painter, edge)

            print(f"Количество вершин: {len(self.vertices)}")
            for vertex in self.vertices:
                if vertex is None:
                    print("Ошибка: вершина равна None")
                    continue
                print(f"Отрисовка вершины {vertex.id}")
                self.draw_vertex(painter, vertex)

            if self.selected_vertex and not self.is_output:
                if self.selected_vertex is None:
                    print("Ошибка: выбранная вершина равна None")
                else:
                    print(f"Отрисовка выбранной вершины {self.selected_vertex.id}")
                    self.draw_selected_vertex(painter, self.selected_vertex)

            print("Завершение paintEvent")
        except Exception as e:
            print(f"Ошибка в paintEvent: {e}")

    def draw_vertex(self, painter, vertex):
        if self.is_output:
            painter.setPen(QPen(Qt.blue, 2))
            painter.setBrush(QBrush(Qt.blue))
        else:
            painter.setPen(QPen(Qt.red, 2))
            painter.setBrush(QBrush(Qt.red))
        painter.drawEllipse(QRectF(vertex.x - 15, vertex.y - 15, 30, 30))
        painter.setPen(QPen(Qt.black))
        painter.drawText(vertex.x - 5, vertex.y + 5, str(vertex.id))

    def draw_selected_vertex(self, painter, vertex):
        painter.setPen(QPen(Qt.green, 2))
        painter.drawText(vertex.x - 28, vertex.y - 28)

    def draw_directed_edge(self, painter, edge):
        start_vertex = edge.start_vertex
        end_vertex = edge.end_vertex
        radius = 15

        dx = end_vertex.x - start_vertex.x
        dy = end_vertex.y - start_vertex.y

        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance == 0:
            return

        dx /= distance
        dy /= distance

        start_x = start_vertex.x + dx * radius
        start_y = start_vertex.y + dy * radius
        end_x = end_vertex.x - dx * radius
        end_y = end_vertex.y - dy * radius

        start_x = int(start_x)
        start_y = int(start_y)
        end_x = int(end_x)
        end_y = int(end_y)

        if self.is_output:
            painter.setPen(QPen(Qt.red, 3))
        else:
            painter.setPen(QPen(Qt.black, 3))
        painter.drawLine(start_x, start_y, end_x, end_y)

        arrow_size = 10
        angle = math.atan2(dy, dx)
        arrow_point1 = (end_x - arrow_size * math.cos(angle - math.pi / 6),
                        end_y - arrow_size * math.sin(angle - math.pi / 6))
        arrow_point2 = (end_x - arrow_size * math.cos(angle + math.pi / 6),
                        end_y - arrow_size * math.sin(angle + math.pi / 6))

        painter.drawLine(end_x, end_y, int(arrow_point1[0]), int(arrow_point1[1]))
        painter.drawLine(end_x, end_y, int(arrow_point2[0]), int(arrow_point2[1]))

        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        painter.drawText(int(mid_x), int(mid_y), str(edge.weight))

    def mousePressEvent(self, event):
        if self.is_output:
            return

        x = event.x()
        y = event.y()

        if event.button() == Qt.LeftButton:
            self.add_vertex(x, y)
        elif event.button() == Qt.RightButton:
            self.select_vertex_for_edge(x, y)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.best_path = []
        self.setWindowTitle("Задача коммивояжёра")
        self.setGeometry(100, 100, 900, 600)

        self.input_graph = GraphWidget(is_output=False)
        self.output_graph = GraphWidget(is_output=True)
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Вершина 1", "Вершина 2", "Вес"])

        self.results_label = QLabel("Пусто")
        self.results_label.setAlignment(Qt.AlignCenter)

        self.calculate_button = QPushButton("Рассчитать")
        self.calculate_modified_button = QPushButton("Рассчитать модификацию")
        self.clear_button = QPushButton("Очистить")

        self.calculate_button.clicked.connect(self.calculate_tsp)
        self.calculate_modified_button.clicked.connect(self.calculate_tsp_modified)
        self.clear_button.clicked.connect(self.clear_all)

        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Входной граф"))
        left_layout.addWidget(self.input_graph)
        left_layout.addWidget(QLabel("Выходной граф"))
        left_layout.addWidget(self.output_graph)

        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Рёбра"))
        right_layout.addWidget(self.tree_widget)
        right_layout.addWidget(self.calculate_button)
        right_layout.addWidget(self.calculate_modified_button)
        right_layout.addWidget(self.clear_button)
        right_layout.addWidget(QLabel("Результаты"))
        right_layout.addWidget(self.results_label)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 1)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.input_graph.edge_added.connect(self.update_edges_table)

    def update_output_graph(self):
        self.output_graph.vertices.clear()
        self.output_graph.edges.clear()
        for vertex_id in self.best_path:
            vertex = next((v for v in self.input_graph.vertices if v.id == vertex_id), None)
            if vertex:
                self.output_graph.vertices.append(vertex)

        for i in range(len(self.best_path) - 1):
            start_id = self.best_path[i]
            end_id = self.best_path[i + 1]
            edge = next(
                (e for e in self.input_graph.edges if e.start_vertex.id == start_id and e.end_vertex.id == end_id),
                None)
            if edge:
                self.output_graph.edges.append(edge)

        if len(self.best_path) > 1:
            start_id = self.best_path[-1]
            end_id = self.best_path[0]
            edge = next(
                (e for e in self.input_graph.edges if e.start_vertex.id == start_id and e.end_vertex.id == end_id),
                None)
            if edge:
                self.output_graph.edges.append(edge)

        self.output_graph.update()

    def calculate_tsp(self):
        if len(self.input_graph.vertices) < 2:
            self.results_label.setText("Недостаточно вершин для решения задачи")
            return

        adj_matrix = {}
        for vertex in self.input_graph.vertices:
            adj_matrix[vertex.id] = {}

        for edge in self.input_graph.edges:
            adj_matrix[edge.start_vertex.id][edge.end_vertex.id] = edge.weight

        start = next((v for v in self.input_graph.vertices if v.id == 1), None)

        if start is None:
            self.results_label.setText("Вершина 1 не существует!")
            return

        visited = {v.id: False for v in self.input_graph.vertices}
        current_path = [start.id]
        current_distance = 0
        visited[start.id] = True
        current_vertex = start

        while len(current_path) < len(self.input_graph.vertices):
            min_dist = float('inf')
            next_vertex = None
            for neighbor_id, weight in adj_matrix[current_vertex.id].items():
                if not visited[neighbor_id] and weight < min_dist:
                    min_dist = weight
                    next_vertex = neighbor_id

            if next_vertex is None:
                self.results_label.setText("Невозможно найти путь: тупиковая ситуация")
                return

            current_path.append(next_vertex)
            current_distance += min_dist
            visited[next_vertex] = True
            current_vertex = next((v for v in self.input_graph.vertices if v.id == next_vertex), None)

        if len(current_path) == len(self.input_graph.vertices):
            if start.id in adj_matrix[current_vertex.id]:
                current_distance += adj_matrix[current_vertex.id][start.id]
            else:
                self.results_label.setText("Невозможно найти путь: нет обратного ребра")
                return

            results_text = f"Лучший путь: {' -> '.join(map(str, current_path))} -> {current_path[0]}\nРасстояние: {current_distance}"
            self.results_label.setText(results_text)

            self.best_path = current_path
            self.update_output_graph()
        else:
            self.results_label.setText("Невозможно найти путь")
            self.best_path = []
            self.output_graph.vertices.clear()
            self.output_graph.edges.clear()
            self.output_graph.update()

    def calculate_path_distance(self, path, adj_matrix):
        distance = 0
        for i in range(len(path) - 1):
            if path[i] not in adj_matrix or path[i + 1] not in adj_matrix[path[i]]:
                print(f"Ошибка: отсутствует ребро между {path[i]} и {path[i + 1]}")
                return float('inf')
            distance += adj_matrix[path[i]][path[i + 1]]

        if path[-1] not in adj_matrix or path[0] not in adj_matrix[path[-1]]:
            print(f"Ошибка: отсутствует ребро между {path[-1]} и {path[0]}")
            return float('inf')
        distance += adj_matrix[path[-1]][path[0]]
        return distance

    def two_opt(self, path, adj_matrix):
        improved = True
        while improved:
            improved = False
            for i in range(1, len(path) - 2):
                for j in range(i + 1, len(path)):
                    if j - i == 1:
                        continue

                    if i < 0 or j < 0 or i >= len(path) or j >= len(path):
                        print(f"Ошибка: некорректные индексы i={i}, j={j}")
                        continue
                    new_path = path[:i] + path[i:j][::-1] + path[j:]
                    new_distance = self.calculate_path_distance(new_path, adj_matrix)
                    if new_distance < self.calculate_path_distance(path, adj_matrix):
                        path = new_path
                        improved = True
        return path
    def calculate_tsp_modified(self):
        if len(self.input_graph.vertices) < 2:
            self.results_label.setText("Недостаточно вершин для решения задачи")
            return

        adj_matrix = {}
        for vertex in self.input_graph.vertices:
            adj_matrix[vertex.id] = {}

        for edge in self.input_graph.edges:
            adj_matrix[edge.start_vertex.id][edge.end_vertex.id] = edge.weight

        for vertex1 in self.input_graph.vertices:
            for vertex2 in self.input_graph.vertices:
                if vertex1.id != vertex2.id and vertex2.id not in adj_matrix[vertex1.id]:
                    adj_matrix[vertex1.id][vertex2.id] = float('inf')

        best_path = None
        best_distance = float('inf')

        for start in self.input_graph.vertices:
            visited = {v.id: False for v in self.input_graph.vertices}
            current_path = [start.id]
            current_distance = 0
            visited[start.id] = True
            current_vertex = start

            while len(current_path) < len(self.input_graph.vertices):
                min_dist = float('inf')
                next_vertex = None
                for neighbor_id, weight in adj_matrix[current_vertex.id].items():
                    if not visited[neighbor_id] and weight < min_dist:
                        min_dist = weight
                        next_vertex = neighbor_id

                if next_vertex is None:
                    break

                current_path.append(next_vertex)
                current_distance += min_dist
                visited[next_vertex] = True
                current_vertex = next((v for v in self.input_graph.vertices if v.id == next_vertex), None)

            if len(current_path) == len(self.input_graph.vertices):
                if start.id in adj_matrix[current_vertex.id]:
                    current_distance += adj_matrix[current_vertex.id][start.id]
                else:
                    continue

                if current_distance < best_distance:
                    best_distance = current_distance
                    best_path = current_path

        if best_path is not None:
            best_path = self.two_opt(best_path, adj_matrix)
            best_distance = self.calculate_path_distance(best_path, adj_matrix)

            results_text = f"Лучший путь (2-opt): {' -> '.join(map(str, best_path))} -> {best_path[0]}\nРасстояние: {best_distance}"
            self.results_label.setText(results_text)
            self.best_path = best_path
            self.update_output_graph()
        else:
            results_text = "Невозможно найти путь"
            self.results_label.setText(results_text)
            self.best_path = []
            self.output_graph.vertices.clear()
            self.output_graph.edges.clear()
            self.output_graph.update()

    def update_edges_table(self):
        print("Обновление таблицы рёбер")
        self.tree_widget.clear()
        for edge in self.input_graph.edges:
            item = QTreeWidgetItem([str(edge.start_vertex.id), str(edge.end_vertex.id), str(edge.weight)])
            self.tree_widget.addTopLevelItem(item)

    def clear_all(self):
        self.input_graph.vertices.clear()
        self.input_graph.edges.clear()
        self.input_graph.vertex_counter = 0
        self.input_graph.selected_vertex = None
        self.input_graph.removed_vertices.clear()
        self.input_graph.action_stack.clear()
        self.output_graph.vertices.clear()
        self.output_graph.edges.clear()
        self.tree_widget.clear()
        self.results_label.setText("")
        self.input_graph.update()
        self.output_graph.update()

   





if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
