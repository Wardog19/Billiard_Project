from PyQt5.QtCore import QTimer, QPointF, Qt, QEvent
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
        self.widget = BilliardWidget(self.balls, self)  # Übergabe der app_instance
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # ~60 FPS
        self.paused = False  # Initialisieren des Pausenstatus
        self.previous_positions = [(ball.x, ball.y) for ball in self.balls]

    def update(self):
        if not self.paused:
            try:
                main_ball = self.balls[0]
                main_ball.collision_point = None
                main_ball.new_velocity = None
                main_ball.secondary_collision_point = None
                main_ball.secondary_collision_other = None
                
                if main_ball.velocity != (0, 0):
                    for other_ball in self.balls[1:]:
                        main_ball.calculate_collision_point(other_ball)
                self.widget.update()
            except Exception as e:
                print(f"Error in update: {e}")

    def run(self):
        sys.exit(self.app.exec_())

    def set_paused(self, paused):
        self.paused = paused