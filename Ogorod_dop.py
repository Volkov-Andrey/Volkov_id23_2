from PyQt5.QtCore import Qt, QTimer, QPointF, QVariantAnimation, QRectF
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGraphicsEllipseItem, QGraphicsScene, QGraphicsView, QApplication, QSlider, QLabel, QHBoxLayout, QPushButton, QComboBox
from math import ceil
import sys, random

class View(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Сцена с капустой и стадом")
        main_layout = QVBoxLayout(self)
        self.graphics_view = QGraphicsView()
        self.scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.scene)
        self.graphics_view.setSceneRect(0, 0, 1200, 600)
        main_layout.addWidget(self.graphics_view)
        self.hunger_level = 1
        self.eating_speed = 3
        self.is_animation_paused = False
        self.herd_list = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_scene)
        for _ in range(5):
            self.spawn_cabbage()
        self.main_herd = Herd(300, 600, 10, self)
        self.scene.addItem(self.main_herd)
        self.herd_list.append(self.main_herd)
        self.main_herd.find_next_cabbage()
        self.timer.start(1000)
        cabbage_timer = QTimer(self)
        cabbage_timer.timeout.connect(self.spawn_cabbage)
        cabbage_timer.start(10000)
        self.setup_controls()

    def setup_controls(self):
        layout = QVBoxLayout()
        self.herd_selector = QComboBox()
        self.herd_selector.currentIndexChanged.connect(self.update_selected_herd)
        layout.addWidget(QLabel("Выберите стадо:"))
        layout.addWidget(self.herd_selector)
        herd_settings_layout = QHBoxLayout()
        speed_label = QLabel("Скорость стада:")
        herd_settings_layout.addWidget(speed_label)
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(1)
        herd_settings_layout.addWidget(self.speed_slider)
        stamina_label = QLabel("Выносливость стада:")
        herd_settings_layout.addWidget(stamina_label)
        self.stamina_slider = QSlider(Qt.Horizontal)
        self.stamina_slider.setRange(1, 100)
        self.stamina_slider.setValue(15)
        herd_settings_layout.addWidget(self.stamina_slider)
        eating_speed_label = QLabel("Скорость поедания:")
        herd_settings_layout.addWidget(eating_speed_label)
        self.eating_speed_slider = QSlider(Qt.Horizontal)
        self.eating_speed_slider.setRange(1, 10)
        self.eating_speed_slider.setValue(3)
        herd_settings_layout.addWidget(self.eating_speed_slider)
        update_herd_button = QPushButton("Обновить параметры стада")
        update_herd_button.clicked.connect(self.update_herd_parameters)
        herd_settings_layout.addWidget(update_herd_button)
        layout.addLayout(herd_settings_layout)
        add_herd_button = QPushButton("Добавить новое стадо")
        add_herd_button.clicked.connect(self.add_herd)
        layout.addWidget(add_herd_button)
        cabbage_settings_layout = QHBoxLayout()
        cabbage_size_label = QLabel("Размер капусты:")
        cabbage_settings_layout.addWidget(cabbage_size_label)
        self.cabbage_size_slider = QSlider(Qt.Horizontal)
        self.cabbage_size_slider.setRange(10, 50)
        self.cabbage_size_slider.setValue(20)
        cabbage_settings_layout.addWidget(self.cabbage_size_slider)
        layout.addLayout(cabbage_settings_layout)
        self.layout().addLayout(layout)

    def spawn_cabbage(self):
        self.is_animation_paused = False
        if not self.is_animation_paused:
            position = random.sample(range(0, 600), 2)
            size = random.randint(10, 50)
            self.scene.addItem(Cabbage(*position, size))

    def update_scene(self):
        if self.main_herd.stamina - self.hunger_level <= 0:
            self.main_herd.radius -= 2.5
            R = self.main_herd.radius
            self.main_herd.setRect(QRectF(-R, -R, 2 * R, 2 * R))
        else:
            self.main_herd.stamina -= self.hunger_level

    def eat_circle(self, cabbage, herd):
        self.current_cabbage = cabbage
        self.current_herd = herd
        self.timer.stop()
        cabbage.setStartAngle(0)
        cabbage.setSpanAngle(-180 * 16)
        herd.setStartAngle(0)
        herd.setSpanAngle(180 * 16)
        self.eat_timer = QTimer(self)
        self.eat_timer.timeout.connect(self.crunch)
        self.eat_timer.start(1000)

    def crunch(self):
        if self.current_cabbage.radius - self.current_herd.eating_speed <= 0:
            self.current_herd.radius += ceil(self.current_cabbage.radius * self.current_herd.raising)
            R = self.current_herd.radius
            self.current_herd.setRect(QRectF(-R, -R, 2 * R, 2 * R))
            self.scene.removeItem(self.current_cabbage)
            self.eat_timer.stop()
            self.current_herd.setStartAngle(0)
            self.current_herd.setSpanAngle(360 * 16)
            self.timer.start(1000)
            self.current_herd.find_next_cabbage()
        else:
            if not self.is_animation_paused:
                self.current_cabbage.radius -= self.current_herd.eating_speed
                R = self.current_cabbage.radius
                self.current_cabbage.setRect(QRectF(-R, -R, 2 * R, 2 * R))
                self.current_herd.radius += ceil(self.current_herd.eating_speed * self.current_herd.raising)
                R = self.current_herd.radius
                self.current_herd.setRect(QRectF(-R, -R, 2 * R, 2 * R))

    def toggle_pause(self):
        if not hasattr(self, 'is_animation_paused'):
            return
        if not self.is_animation_paused:
            if hasattr(self.current_cabbage, 'animation'):
                self.current_cabbage.animation.pause()
            if hasattr(self.current_herd, 'animation'):
                self.current_herd.animation.pause()
        else:
            if hasattr(self.current_cabbage, 'animation'):
                self.current_cabbage.animation.resume()
            if hasattr(self.current_herd, 'animation'):
                self.current_herd.animation.resume()
        self.is_animation_paused = not self.is_animation_paused

    def add_herd(self):
        speed = self.speed_slider.value()
        stamina = self.stamina_slider.value()
        eating_speed = self.eating_speed_slider.value()
        new_herd = Herd(600, 600, 10, self)
        new_herd.speed = speed
        new_herd.stamina = stamina
        new_herd.eating_speed = eating_speed
        self.scene.addItem(new_herd)
        self.herd_list.append(new_herd)
        new_herd.find_next_cabbage()
        self.update_herd_selector()

    def update_herd_selector(self):
        self.herd_selector.clear()
        for herd in self.herd_list:
            self.herd_selector.addItem(f"Стадо {self.herd_list.index(herd) + 1}")

    def update_selected_herd(self):
        selected_herd = self.herd_list[self.herd_selector.currentIndex()]
        self.speed_slider.setValue(selected_herd.speed)
        self.stamina_slider.setValue(selected_herd.stamina)
        self.eating_speed_slider.setValue(selected_herd.eating_speed)

    def update_herd_parameters(self):
        selected_herd = self.herd_list[self.herd_selector.currentIndex()]
        selected_herd.speed = self.speed_slider.value()
        selected_herd.stamina = self.stamina_slider.value()
        selected_herd.eating_speed = self.eating_speed_slider.value()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x, y = event.pos().x(), event.pos().y()
            size = self.cabbage_size_slider.value()
            self.scene.addItem(Cabbage(x, y, size))

class Cabbage(QGraphicsEllipseItem):
    def __init__(self, x, y, radius):
        super().__init__(0, 0, radius, radius)
        self.radius = radius
        self.setBrush(Qt.darkGreen)
        self.setPos(x, y)
        self.setRect(QRectF(-radius, -radius, 2 * radius, 2 * radius))

class Herd(QGraphicsEllipseItem):
    def __init__(self, x, y, radius, view):
        super().__init__(0, 0, radius, radius)
        self.radius = radius
        self.setPos(x, y)
        self.setBrush(Qt.black)
        self.view = view
        self.setRect(QRectF(-radius, -radius, 2*radius, 2*radius))
        self.speed = 1
        self.stamina = 15
        self.raising = 1
        self.eating_speed = 3

    def move_to(self, x, y):
        distance = (((self.x() - x) ** 2 + (self.y() - y) ** 2) ** 0.5) * 10
        animation_duration = int(distance / self.speed)

        if not hasattr(self.view, 'is_animation_paused') or not self.view.is_animation_paused:
            animation = QVariantAnimation(duration=animation_duration)
            animation.valueChanged.connect(self.setPos)
            animation.finished.connect(self.eating)
            animation.setEndValue(QPointF(x, y))
            animation.setStartValue(self.pos())
            animation.start()
            setattr(self, 'animation', animation)

    def eating(self):
        if not hasattr(self.view, 'is_animation_paused') or not self.view.is_animation_paused:
            self.view.eat_circle(self.next_cabbage, self)

    def find_next_cabbage(self):
        if not hasattr(self.view, 'is_animation_paused') or not self.view.is_animation_paused:
            self.min_distance = 10000
            self.next_cabbage = None
            for item in self.view.scene.items():
                if isinstance(item, Cabbage):
                    distance = (((self.x() - item.x()) ** 2 + (self.y() - item.y()) ** 2) ** 0.5)
                    if distance <= self.min_distance:
                        self.min_distance = min(distance, self.min_distance)
                        self.next_cabbage = item
            self.move_to(self.next_cabbage.x(), self.next_cabbage.y())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = View()
    view.show()
    view.keyPressEvent = lambda event: view.toggle_pause() if event.key() == Qt.Key_P else None
    sys.exit(app.exec_())
