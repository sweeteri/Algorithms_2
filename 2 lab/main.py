import sys
import math
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTreeWidget, QTreeWidgetItem, QInputDialog)
from PyQt5.QtGui import QPainter, QPen, QBrush
from PyQt5.QtCore import Qt, QRectF, pyqtSignal


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
            for vertex in self.vertices:
                distance = math.sqrt((x - vertex.x) ** 2 + (y - vertex.y) ** 2)
                if distance < 20:
                    if self.selected_vertex is None:
                        self.selected_vertex = vertex
                        self.update()
                        return
                    else:
                        if self.selected_vertex != vertex:
                            edge_exists = False
                            edge_index = -1

                            for idx, edge in enumerate(self.edges):
                                if (edge.start_vertex.id == self.selected_vertex.id and
                                        edge.end_vertex.id == vertex.id):
                                    edge_exists = True
                                    edge_index = idx
                                    break

                            if edge_exists:
                                current_weight = self.edges[edge_index].weight
                                new_weight, ok = QInputDialog.getInt(self, "Вес рёбра",
                                                                     f"Ребро между {self.selected_vertex.id} и {vertex.id} уже существует. Текущий вес: {current_weight}\nВведите новый вес:",
                                                                     current_weight)
                                if ok:
                                    old_edge = self.edges[edge_index]
                                    self.edges[edge_index].weight = new_weight
                                    self.action_stack.append(("weight_change", old_edge, self.edges[edge_index]))
                                    self.update()

                                self.selected_vertex = None
                                self.update()
                                self.edge_added.emit()
                                return

                            weight, ok = QInputDialog.getInt(self, "Вес рёбра",
                                                             f"Введите вес рёбра от {self.selected_vertex.id} до {vertex.id}:")
                            if not ok:
                                return

                            edge = Edge(self.selected_vertex, vertex, weight)
                            self.edges.append(edge)
                            self.action_stack.append(("edge", edge))
                            self.update()

                            self.selected_vertex = None
                            self.update()
                            self.edge_added.emit()
                            return
                        else:
                            self.selected_vertex = None
                            self.update()
        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(QPen(Qt.black, 2, Qt.DashLine))
            painter.drawRect(10, 10, self.width() - 20, self.height() - 20)

            for edge in self.edges:
                if edge is None or edge.start_vertex is None or edge.end_vertex is None:
                    continue
                self.draw_directed_edge(painter, edge)

            for vertex in self.vertices:
                if vertex is None:
                    continue
                self.draw_vertex(painter, vertex)

            if self.selected_vertex and not self.is_output:
                if self.selected_vertex is not None:
                    self.draw_selected_vertex(painter, self.selected_vertex)

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
        self.setWindowTitle("Задача коммивояжёра - Имитация отжига")
        self.setGeometry(100, 100, 900, 600)

        self.input_graph = GraphWidget(is_output=False)
        self.output_graph = GraphWidget(is_output=True)
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Вершина 1", "Вершина 2", "Вес"])

        self.results_label = QLabel("Пусто")
        self.results_label.setAlignment(Qt.AlignCenter)

        self.calculate_button = QPushButton("Имитация отжига")
        self.calculate_modified_button = QPushButton("Больцмановский отжиг")
        self.clear_button = QPushButton("Очистить")

        self.calculate_button.clicked.connect(self.simulated_annealing)
        self.calculate_modified_button.clicked.connect(self.boltzmann_annealing)
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

    def calculate_path_distance(self, path, adj_matrix):
        distance = 0
        for i in range(len(path) - 1):
            if path[i] not in adj_matrix or path[i + 1] not in adj_matrix[path[i]]:
                return float('inf')
            distance += adj_matrix[path[i]][path[i + 1]]

        if path[-1] not in adj_matrix or path[0] not in adj_matrix[path[-1]]:
            return float('inf')
        distance += adj_matrix[path[-1]][path[0]]
        return distance

    def get_adjacency_matrix(self):
        adj_matrix = {}
        for vertex in self.input_graph.vertices:
            adj_matrix[vertex.id] = {}

        for edge in self.input_graph.edges:
            adj_matrix[edge.start_vertex.id][edge.end_vertex.id] = edge.weight

        for vertex1 in self.input_graph.vertices:
            for vertex2 in self.input_graph.vertices:
                if vertex1.id != vertex2.id and vertex2.id not in adj_matrix[vertex1.id]:
                    adj_matrix[vertex1.id][vertex2.id] = float('inf')

        return adj_matrix

    def simulated_annealing(self):
        if len(self.input_graph.vertices) < 2:
            self.results_label.setText("Недостаточно вершин для решения задачи")
            return

        adj_matrix = self.get_adjacency_matrix()
        vertices = [v.id for v in self.input_graph.vertices]

        initial_temp = 1000
        final_temp = 0.1
        cooling_rate = 0.99
        iterations_per_temp = 100

        current_path = vertices.copy()
        random.shuffle(current_path)
        current_distance = self.calculate_path_distance(current_path, adj_matrix)

        best_path = current_path.copy()
        best_distance = current_distance

        temp = initial_temp

        while temp > final_temp:
            for _ in range(iterations_per_temp):

                new_path = current_path.copy()
                i, j = random.sample(range(len(new_path)), 2)
                new_path[i], new_path[j] = new_path[j], new_path[i]
                new_distance = self.calculate_path_distance(new_path, adj_matrix)

                delta = new_distance - current_distance

                if delta < 0 or random.random() < math.exp(-delta / temp):
                    current_path = new_path
                    current_distance = new_distance

                    if current_distance < best_distance:
                        best_path = current_path.copy()
                        best_distance = current_distance

            temp *= cooling_rate

        self.best_path = best_path
        results_text = f"Лучший путь (Имитация отжига): {' -> '.join(map(str, best_path))} -> {best_path[0]}\nРасстояние: {best_distance}"
        self.results_label.setText(results_text)
        self.update_output_graph()

    def boltzmann_annealing(self):
        if len(self.input_graph.vertices) < 2:
            self.results_label.setText("Недостаточно вершин для решения задачи")
            return

        adj_matrix = self.get_adjacency_matrix()
        vertices = [v.id for v in self.input_graph.vertices]

        initial_temp = 1000
        final_temp = 0.1
        cooling_rate = 0.95
        iterations_per_temp = 200

        current_path = vertices.copy()
        random.shuffle(current_path)
        current_distance = self.calculate_path_distance(current_path, adj_matrix)

        best_path = current_path.copy()
        best_distance = current_distance

        temp = initial_temp

        while temp > final_temp:
            accepted = 0
            for _ in range(iterations_per_temp):
                new_path = current_path.copy()
                if random.random() < 0.7:
                    i, j = random.sample(range(len(new_path)), 2)
                    new_path[i], new_path[j] = new_path[j], new_path[i]
                else:
                    i, j = sorted(random.sample(range(len(new_path)), 2))
                    new_path[i:j + 1] = reversed(new_path[i:j + 1])

                new_distance = self.calculate_path_distance(new_path, adj_matrix)

                delta = new_distance - current_distance

                if delta < 0 or random.random() < math.exp(-delta / temp):
                    current_path = new_path
                    current_distance = new_distance
                    accepted += 1

                    if current_distance < best_distance:
                        best_path = current_path.copy()
                        best_distance = current_distance

            acceptance_ratio = accepted / iterations_per_temp
            if acceptance_ratio > 0.6:
                cooling_rate = 0.99
            elif acceptance_ratio > 0.3:
                cooling_rate = 0.95
            else:
                cooling_rate = 0.9

            temp *= cooling_rate

        self.best_path = best_path
        results_text = f"Лучший путь (Больцмановский отжиг): {' -> '.join(map(str, best_path))} -> {best_path[0]}\nРасстояние: {best_distance}"
        self.results_label.setText(results_text)
        self.update_output_graph()

    def update_edges_table(self):
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