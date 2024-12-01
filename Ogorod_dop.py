from PyQt5.QtCore import Qt, QPointF, QTimer, QVariantAnimation, QRectF
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QSlider, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QComboBox
from math import ceil
import sys, random


class View(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Сцена с капустой и стадом")

        # Основной layout
        main_layout = QVBoxLayout(self)

        # Создание QGraphicsView и QGraphicsScene
        self.graphics_view = QGraphicsView()
        self.scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.scene)
        self.graphics_view.setSceneRect(0, 0, 1200, 600)
        main_layout.addWidget(self.graphics_view)

        # Инициализация состояния
        self.hunger = 1
        self.eatingspeed = 3
        self.animation_paused = False  # Флаг для паузы анимации

        # Список для хранения стад
        self.herds = []

        # Тикер для обновлений сцены
        self.tick = QTimer(self)
        self.tick.timeout.connect(self.updscene)
        for _ in range(5):
            self.spawn_cab()
        self.herd = Herd(300, 600, 10, self)
        self.scene.addItem(self.herd)
        self.herds.append(self.herd)  # Сохраняем стадо в список
        self.herd.find_next_cab()
        self.tick.start(1000)

        # Тикер для появления новой капусты
        cabtick = QTimer(self)
        cabtick.timeout.connect(self.spawn_cab)
        cabtick.start(10000)

        # Элементы управления для настройки параметров стада
        self.setup_controls()

    def setup_controls(self):
        # Панель управления
        layout = QVBoxLayout()

        # Панель для выбора стада
        self.herd_selector = QComboBox()
        self.herd_selector.currentIndexChanged.connect(self.update_selected_herd)
        layout.addWidget(QLabel("Выберите стадо:"))
        layout.addWidget(self.herd_selector)

        # Панель с настройками стада
        herd_settings_layout = QHBoxLayout()

        # Слайдер для скорости
        speed_label = QLabel("Скорость стада:")
        herd_settings_layout.addWidget(speed_label)
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(1)
        herd_settings_layout.addWidget(self.speed_slider)

        # Слайдер для выносливости
        stamina_label = QLabel("Выносливость стада:")
        herd_settings_layout.addWidget(stamina_label)
        self.stamina_slider = QSlider(Qt.Horizontal)
        self.stamina_slider.setRange(1, 100)
        self.stamina_slider.setValue(15)
        herd_settings_layout.addWidget(self.stamina_slider)

        # Слайдер для скорости поедания
        eating_speed_label = QLabel("Скорость поедания:")
        herd_settings_layout.addWidget(eating_speed_label)
        self.eating_speed_slider = QSlider(Qt.Horizontal)
        self.eating_speed_slider.setRange(1, 10)
        self.eating_speed_slider.setValue(3)
        herd_settings_layout.addWidget(self.eating_speed_slider)

        # Кнопка для обновления параметров выбранного стада
        update_herd_button = QPushButton("Обновить параметры стада")
        update_herd_button.clicked.connect(self.update_herd_parameters)
        herd_settings_layout.addWidget(update_herd_button)

        layout.addLayout(herd_settings_layout)

        # Кнопка для добавления нового стада
        add_herd_button = QPushButton("Добавить новое стадо")
        add_herd_button.clicked.connect(self.add_herd)
        layout.addWidget(add_herd_button)

        # Панель с настройками капусты
        cabbage_settings_layout = QHBoxLayout()

        # Слайдер для радиуса капусты
        cabbage_size_label = QLabel("Размер капусты:")
        cabbage_settings_layout.addWidget(cabbage_size_label)
        self.cabbage_size_slider = QSlider(Qt.Horizontal)
        self.cabbage_size_slider.setRange(10, 50)
        self.cabbage_size_slider.setValue(20)
        cabbage_settings_layout.addWidget(self.cabbage_size_slider)

        layout.addLayout(cabbage_settings_layout)

        # Установка layout для панели управления
        self.layout().addLayout(layout)

    def spawn_cab(self):
        # Создание капусты в случайном месте
        self.animation_paused = False
        if not self.animation_paused:
            d = random.sample(range(0, 600), 2)
            v = random.randint(10, 50)  # Увеличен диапазон радиуса капусты
            self.scene.addItem(Cabbage(*d, v))

    def updscene(self):
        # Обновление сцены
        if self.herd.stamina - self.hunger <= 0:
            self.herd.r -= 2.5
            R = self.herd.r
            self.herd.setRect(QRectF(-R, -R, 2 * R, 2 * R))
        else:
            self.herd.stamina -= self.hunger

    def eat_circle(self, cabbage, herd):
        # Запуск процесса поедания капусты
        self.cab = cabbage
        self.herd = herd
        self.tick.stop()
        cabbage.setStartAngle(0)
        cabbage.setSpanAngle(-180 * 16)
        herd.setStartAngle(0)
        herd.setSpanAngle(180 * 16)
        self.etick = QTimer(self)
        self.etick.timeout.connect(self.crunch)
        self.etick.start(1000)

    def crunch(self):
        # Обновление поедания капусты
        if self.cab.r - self.herd.eating_speed <= 0:
            self.herd.r += ceil(self.cab.r * self.herd.raising)
            R = self.herd.r
            self.herd.setRect(QRectF(-R, -R, 2 * R, 2 * R))
            self.scene.removeItem(self.cab)
            self.etick.stop()
            self.herd.setStartAngle(0)
            self.herd.setSpanAngle(360 * 16)
            self.tick.start(1000)
            self.herd.find_next_cab()
        else:
            if not self.animation_paused:  # Проверка на паузу перед обновлением
                self.cab.r -= self.herd.eating_speed
                R = self.cab.r
                self.cab.setRect(QRectF(-R, -R, 2 * R, 2 * R))
                self.herd.r += ceil(self.herd.eating_speed * self.herd.raising)
                R = self.herd.r
                self.herd.setRect(QRectF(-R, -R, 2 * R, 2 * R))

    def toggle_pause(self):  # Метод для переключения паузы
        if not hasattr(self, 'animation_paused'):
            return

        if not self.animation_paused:
            # Пауза анимации
            if hasattr(self.cab, 'animation'):
                self.cab.animation.pause()
            if hasattr(self.herd, 'animation'):
                self.herd.animation.pause()
            print("Анимация приостановлена")
        else:
            # Возобновление анимации
            if hasattr(self.cab, 'animation'):
                self.cab.animation.resume()
            if hasattr(self.herd, 'animation'):
                self.herd.animation.resume()
            print("Анимация возобновлена")

        # Переключение флага паузы
        self.animation_paused = not self.animation_paused

    def add_herd(self):
        # Создание нового стада с параметрами из элементов управления
        speed = self.speed_slider.value()
        stamina = self.stamina_slider.value()
        eating_speed = self.eating_speed_slider.value()
        new_herd = Herd(600, 600, 10, self)
        new_herd.speed = speed
        new_herd.stamina = stamina
        new_herd.eating_speed = eating_speed
        self.scene.addItem(new_herd)
        self.herds.append(new_herd)  # Сохраняем новое стадо в список
        new_herd.find_next_cab()
        self.update_herd_selector()

    def update_herd_selector(self):
        # Обновление выпадающего списка с существующими стадами
        self.herd_selector.clear()
        for herd in self.herds:
            self.herd_selector.addItem(f"Стадо {self.herds.index(herd) + 1}")

    def update_selected_herd(self):
        # Обновление значений слайдеров в зависимости от выбранного стада
        selected_herd = self.herds[self.herd_selector.currentIndex()]
        self.speed_slider.setValue(selected_herd.speed)
        self.stamina_slider.setValue(selected_herd.stamina)
        self.eating_speed_slider.setValue(selected_herd.eating_speed)

    def update_herd_parameters(self):
        # Обновление параметров выбранного стада
        selected_herd = self.herds[self.herd_selector.currentIndex()]
        selected_herd.speed = self.speed_slider.value()
        selected_herd.stamina = self.stamina_slider.value()
        selected_herd.eating_speed = self.eating_speed_slider.value()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Создание капусты на основе настроек
            x, y = event.pos().x(), event.pos().y()
            size = self.cabbage_size_slider.value()
            self.scene.addItem(Cabbage(x, y, size))


class Cabbage(QGraphicsEllipseItem):
    def __init__(self, x, y, r):
        super().__init__(0, 0, r, r)
        self.setPos(x, y)
        self.r = r
        self.setBrush(Qt.green)
        self.setRect(QRectF(-r, -r, 2 * r, 2 * r))


class Herd(QGraphicsEllipseItem):
    def __init__(self, x, y, r, view):
        super().__init__(0, 0, r, r)
        self.setPos(x, y)
        self.r = r
        self.view = view
        self.setBrush(Qt.black)
        self.setRect(QRectF(-r, -r, 2 * r, 2 * r))

        # Начальные параметры стада
        self.speed = 1
        self.stamina = 15
        self.raising = 1
        self.eating_speed = 3

    def move_to(self, x, y):
        dist = (((self.x() - x) ** 2 + (self.y() - y) ** 2) ** 0.5) * 10
        animation_duration = int(dist / self.speed)

        if not hasattr(self.view, 'animation_paused') or not self.view.animation_paused:
            # Создание и запуск анимации только если не на паузе
            animation = QVariantAnimation(duration=animation_duration)
            animation.valueChanged.connect(self.setPos)
            animation.finished.connect(self.eating)

            animation.setStartValue(self.pos())
            animation.setEndValue(QPointF(x, y))

            animation.start()

            # Сохранение ссылки на анимацию для последующего управления
            setattr(self, 'animation', animation)

    def eating(self):
        if not hasattr(self.view, 'animation_paused') or not self.view.animation_paused:
            # Запуск процесса поедания только если не на паузе
            self.view.eat_circle(self.next_cab, self)

    def find_next_cab(self):
        if not hasattr(self.view, 'animation_paused') or not self.view.animation_paused:
            self.mn = 10000
            self.next_cab = None
            for ti in self.view.scene.items():
                if isinstance(ti, Cabbage):
                    dist = (((self.x() - ti.x()) ** 2 + (self.y() - ti.y()) ** 2) ** 0.5)
                    if dist <= self.mn:
                        self.mn = min(dist, self.mn)
                        self.next_cab = ti

            self.move_to(self.next_cab.x(), self.next_cab.y())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = View()
    view.show()

    # Привязка клавиши для переключения паузы (например "P")
    view.keyPressEvent = lambda event: view.toggle_pause() if event.key() == Qt.Key_P else None

    sys.exit(app.exec_())

