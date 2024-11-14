from PyQt5.QtCore import Qt, QPointF, QTimer, QVariantAnimation, QRectF
from math import ceil
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsEllipseItem,
)
import sys, random


class GraphicView(QGraphicsView):
    def __init__(sf):
        super().__init__()
        scene = QGraphicsScene(sf)
        sf.setScene(scene)
        sf.setSceneRect(0, 0, 1200, 600)
        sf.tick = QTimer(sf)
        sf.tick.timeout.connect(sf.updscene)
        for _ in range(5):
            sf.spawn_cab()
        sf.herd = Herd(300, 600, 10, sf)
        sf.scene().addItem(sf.herd)
        sf.herd.find_next_cab()
        sf.tick.start(1000)
        cabtick = QTimer(sf)
        cabtick.timeout.connect(sf.spawn_cab)
        cabtick.start(5000)

        sf.hunger = 5
        sf.eatingspeed = 3

    def spawn_cab(sf):
        d = random.sample(range(0, 600), 2)
        v = random.randint(3, 10)
        sf.scene().addItem(Cabbage(*d, v))

    def updscene(sf):
        if sf.herd.stamina - sf.hunger <= 0:
            sf.herd.r -= 3
            R = sf.herd.r
            sf.herd.setRect(QRectF(-R, -R, 2 * R, 2 * R))
        else:
            sf.herd.stamina -= sf.hunger

    def eat_circle(sf, cabbage, herd):
        sf.cab = cabbage
        sf.herd = herd
        sf.tick.stop()
        cabbage.setStartAngle(0)
        cabbage.setSpanAngle(-180 * 16)
        herd.setStartAngle(0)
        herd.setSpanAngle(180 * 16)
        sf.etick = QTimer(sf)
        sf.etick.timeout.connect(sf.crunch)
        sf.etick.start(1000)

    def crunch(sf):
        if sf.cab.r - sf.eatingspeed <= 0:
            sf.herd.r += ceil(sf.cab.r * sf.herd.raising)
            R = sf.herd.r
            sf.herd.setRect(QRectF(-R, -R, 2 * R, 2 * R))
            sf.scene().removeItem(sf.cab)
            sf.etick.stop()
            sf.herd.setStartAngle(0)
            sf.herd.setSpanAngle(360 * 16)
            sf.tick.start(1000)
            sf.herd.find_next_cab()
        else:
            sf.cab.r -= sf.eatingspeed
            R = sf.cab.r
            sf.cab.setRect(QRectF(-R, -R, 2 * R, 2 * R))
            sf.herd.r += ceil(sf.eatingspeed * sf.herd.raising)
            R = sf.herd.r
            sf.herd.setRect(QRectF(-R, -R, 2 * R, 2 * R))


class Cabbage(QGraphicsEllipseItem):
    def __init__(sf, x, y, r):
        super().__init__(0, 0, r, r)
        sf.setPos(x, y)
        sf.r = r
        sf.setBrush(Qt.green)
        sf.setRect(QRectF(-r, -r, 2 * r, 2 * r))


class Herd(QGraphicsEllipseItem):
    def __init__(sf, x, y, r, view):
        super().__init__(0, 0, r, r)
        sf.setPos(x, y)
        sf.r = r
        sf.view = view
        sf.setBrush(Qt.black)
        sf.setRect(QRectF(-r, -r, 2 * r, 2 * r))

        sf.speed = 1
        sf.stamina = 5
        sf.raising = 1

    def move_to(sf, x, y):
        dist = (((sf.x() - x) ** 2 + (sf.y() - y) ** 2) ** 0.5) * 10
        sf._animation = QVariantAnimation(duration=int(dist / sf.speed))
        sf._animation.valueChanged.connect(sf.setPos)
        sf._animation.finished.connect(sf.eating)
        sf._animation.setStartValue(sf.pos())
        sf._animation.setEndValue(QPointF(x, y))
        sf._animation.start(100)

    def eating(sf):
        sf.view.eat_circle(sf.next_cab, sf)

    def find_next_cab(sf):
        sf.mn = 10000
        sf.next_cab = None
        for ti in sf.view.items():
            if isinstance(ti, Cabbage):
                dist = (((sf.x() - ti.x()) ** 2 + (sf.y() - ti.y()) ** 2) ** 0.5)
                if dist <= sf.mn:
                    sf.mn = min(dist, sf.mn)
                    sf.next_cab = ti
        sf.move_to(sf.next_cab.x(), sf.next_cab.y())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = GraphicView()
    view.show()
    sys.exit(app.exec_())
