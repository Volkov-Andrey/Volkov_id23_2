import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton,
                             QSlider, QSpinBox, QLabel)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor

class SolarEclipseApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Солнечное затмение")
        self.setGeometry(100, 100, 800, 600)

        self.moon_radius = 70
        self.speed = 10
        self.moon_position = 0
        self.distance_from_earth = 200

        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_moon_position)

    def initUI(self):
        layout = QVBoxLayout()

        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(self.speed)
        self.speed_slider.valueChanged.connect(self.update_speed)

        self.radius_spinbox = QSpinBox()
        self.radius_spinbox.setRange(10, 100)
        self.radius_spinbox.setValue(self.moon_radius)
        self.radius_spinbox.valueChanged.connect(self.update_radius)

        self.distance_slider = QSlider(Qt.Horizontal)
        self.distance_slider.setRange(100, 400)
        self.distance_slider.setValue(self.distance_from_earth)
        self.distance_slider.valueChanged.connect(self.update_distance)

        self.start_button = QPushButton("Запустить анимацию")
        self.start_button.clicked.connect(self.start_animation)

        self.reset_button = QPushButton("Сбросить параметры")
        self.reset_button.clicked.connect(self.reset_parameters)

        layout.addWidget(QLabel("Скорость движения Луны:"))
        layout.addWidget(self.speed_slider)
        layout.addWidget(QLabel("Радиус Луны:"))
        layout.addWidget(self.radius_spinbox)
        layout.addWidget(QLabel("Расстояние между Луной и Землей:"))
        layout.addWidget(self.distance_slider)
        layout.addWidget(self.start_button)
        layout.addWidget(self.reset_button)

        self.setLayout(layout)

    def update_speed(self, value):
        self.speed = value

    def update_radius(self, value):
        self.moon_radius = value

    def update_distance(self, value):
        self.distance_from_earth = value

    def start_animation(self):
        self.timer.start(1000 // self.speed)

    def reset_parameters(self):
        self.speed_slider.setValue(10)
        self.radius_spinbox.setValue(70)
        self.distance_slider.setValue(200)
        self.timer.stop()
        self.moon_position = 0
        self.update()

    def update_moon_position(self):
        self.moon_position += self.speed
        if self.moon_position > self.width():
            self.moon_position = -self.moon_radius
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        sun_radius = 100
        sun_x = (self.width() - sun_radius) // 2
        sun_y = (self.height() - sun_radius) // 2
        painter.setBrush(QColor(255, 204, 0))
        painter.drawEllipse(sun_x, sun_y, sun_radius, sun_radius)

        moon_x = self.moon_position + self.distance_from_earth
        moon_y = (self.height() - self.moon_radius) // 2
        painter.setBrush(QColor(200, 200, 200))
        painter.drawEllipse(moon_x, moon_y, self.moon_radius, self.moon_radius)

        if (moon_x + self.moon_radius > sun_x) and (moon_x < sun_x + sun_radius):
            painter.setBrush(QColor(0, 0, 0))
            painter.drawEllipse(moon_x, moon_y, self.moon_radius, self.moon_radius)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SolarEclipseApp()
    window.show()
    sys.exit(app.exec_())
