from PyQt5.QtCore import QTimer
import sys
from PyQt5.QtWidgets import QApplication
from physics import Ball
from ui import BilliardWidget

class BilliardApp:
    def __init__(self):
        self.balls = [
            Ball(100, 100, 18, (255, 0, 0), control_key=Qt.Key_1),
            Ball(200, 150, 18, (0, 255, 0), control_key=Qt.Key_2),
            Ball(300, 200, 18, (0, 0, 255), control_key=Qt.Key_3)
        ]
        self.app = QApplication(sys.argv)
        self.widget = BilliardWidget(self.balls, self)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)
        self.paused = False

    def update(self):
        # Aktualisierungslogik hier

    def run(self):
        sys.exit(self.app.exec_())

    def set_paused(self, paused):
        self.paused = paused
