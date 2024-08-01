#game_logic.py
from PyQt5.QtCore import QTimer, QPointF, Qt, QEvent
import sys
from PyQt5.QtWidgets import QApplication
from physics import Ball
from ui import BilliardWidget
import logging

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
        
        logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


# game_logic.py

    def update(self):
        if not self.paused:
            try:
                for ball in self.balls:
                    ball.collision_point = None
                    ball.new_velocity = None
                    ball.secondary_collision_point = None
                    ball.secondary_collision_other = None

                    # Hier berechnen wir die potenziellen Kollisionen
                    for other_ball in self.balls:
                        if ball != other_ball:
                            ball.calculate_theoretical_collision(other_ball)

                # Aktualisieren der Benutzeroberfläche
                self.widget.update()
            except AttributeError as e:
                logging.error(f"AttributeError in update: {e}")
            except IndexError as e:
                logging.error(f"IndexError in update: {e}")
            except Exception as e:
                logging.error(f"Unexpected error in update: {e}")


    def run(self):
        sys.exit(self.app.exec_())

    def set_paused(self, paused):
        self.paused = paused