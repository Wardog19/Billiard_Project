
import sys
import math
from PyQt5.QtCore import QTimer, QPointF, Qt, QEvent
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QCursor
from PyQt5.QtWidgets import QApplication, QWidget
from pynput import mouse, keyboard
import win32gui
import win32con
import win32api

class Ball:
    def __init__(self, x, y, radius, color, control_key=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.control_key = control_key
        self.follow_mouse = False
        self.velocity = (0, 0)
        self.new_velocity = None
        self.collision_point = None
        self.new_velocity = None
        self.collision_other = None
        self.secondary_collision_point = None
        self.secondary_collision_other = None

        print(f"Ball created at ({x}, {y}) with radius {radius}, color {color}, and control_key {control_key}.")

    def set_position(self, x, y):
        print(f"Setting position of ball from ({self.x}, {self.y}) to ({x}, {y}).")
        self.x = x
        self.y = y

    def calculate_collision_point(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        center_distance = math.sqrt(dx**2 + dy**2)

        print(f"Calculating collision: dx={dx}, dy={dy}, center_distance={center_distance}")

        if center_distance <= (self.radius + other.radius):
            if center_distance != 0:
                normal = (dx / center_distance, dy / center_distance)
            else:
                normal = (1, 0)  # Arbiträre Normalvektor, falls die Kugeln genau übereinander liegen

            contact_x = other.x - normal[0] * other.radius
            contact_y = other.y - normal[1] * other.radius

            self.collision_point = (contact_x, contact_y)
            self.collision_other = other

            print(f"Collision detected at point: {self.collision_point}")

            # Berechne die neue Geschwindigkeit der Hauptkugel nach Kollision
            # Hier wird einfach die Richtung der Geschwindigkeit umgedreht (vereinfachte Annahme)
            self.new_velocity = (
                -self.velocity[0],  # Beispielhafte neue Geschwindigkeit nach Kollision
                -self.velocity[1]
            )
        else:
            print("No collision detected.")
            self.collision_point = None
            self.new_velocity = None
            self.collision_other = None

    def project_and_check_collision(self, other_balls):
        if self.new_velocity is None:
            print("No new velocity; cannot project and check for collisions.")
            return None, None

        projected_x = self.x + self.new_velocity[0]
        projected_y = self.y + self.new_velocity[1]
        print(f"Projecting ball position to ({projected_x}, {projected_y}) based on velocity {self.new_velocity}.")

        for other in other_balls:
            if other != self.collision_other:
                dx = other.x - projected_x
                dy = other.y - projected_y
                center_distance = math.sqrt(dx**2 + dy**2)
                print(f"Checking collision with another ball at ({other.x}, {other.y}): distance={center_distance}")

                if center_distance <= (self.radius + other.radius):
                    contact_x = other.x - (dx / center_distance) * other.radius
                    contact_y = other.y - (dy / center_distance) * other.radius
                    print(f"Secondary collision detected at ({contact_x}, {contact_y}) with ball at ({other.x}, {other.y}).")
                    return (contact_x, contact_y), other

        print("No secondary collision detected.")
        return None, None


# Beispiel-Testfälle zur Veranschaulichung der Funktionalität

# Fall: Kollision des Hauptballs (ball1) mit ball2, gefolgt von einer möglichen Projektion und Kollision von ball2 mit ball3
ball1 = Ball(100, 100, 18, (255, 0, 0))
ball2 = Ball(130, 100, 18, (0, 255, 0))
ball3 = Ball(160, 100, 18, (0, 0, 255))

ball1.velocity = (10, 0)  # Bewegt sich horizontal auf ball2 zu
ball1.calculate_collision_point(ball2)
if ball1.collision_point:
    print(f"Erste Kollision: {ball1.collision_point} mit Ball 2")

# Projektion der Bewegung von ball2 nach der Kollision
collision_point_secondary, colliding_ball_secondary = ball2.project_and_check_collision([ball1, ball3])
if collision_point_secondary:
    print(f"Zweite Kollision: {collision_point_secondary} mit Ball 3")
else:
    print("Keine zweite Kollision festgestellt.")
    pass

class BilliardWidget(QWidget):
    def __init__(self, balls, app_instance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.balls = balls
        self.app_instance = app_instance  # Speichern der app_instance
        self.mouse_pos = QPointF()
        self.setMouseTracking(True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.initUI()
        self.overlay_frozen = False
        self.current_ball = None
        self.freeze_mouse = False
        self.l_alt_pressed = True
        self.is_foreground = False
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.mouse_listener = mouse.Listener(on_move=self.on_move)
        self.listener.start()
        self.mouse_listener.start()
        
        print("BilliardWidget initialized with balls and app_instance.")
        
    def event(self, event):
        if event.type() == QEvent.MouseMove:
            print(f"Mouse move event detected at position ({event.x()}, {event.y()}).")
            self.mouseMoveEvent(event)
        return super().event(event)


    def initUI(self):
        self.setWindowTitle('Transparent Billiard Overlay')
        self.setGeometry(100, 100, 1600, 900)
        self.show()
        print("UI initialized: window titled 'Transparent Billiard Overlay' with geometry (100, 100, 1600, 900).")
        
    def on_move(self, x, y):
        self.mouse_pos = QPointF(x, y)
        print(f"Global mouse moved to: ({x}, {y}).")

        if self.l_alt_pressed:
            main_ball = self.balls[0]
            dx = self.mouse_pos.x() - main_ball.x
            dy = self.mouse_pos.y() - main_ball.y
            angle = math.atan2(dy, dx)
            print(f"Main ball angle updated based on mouse position: {math.degrees(angle)} degrees.")
            self.update()


    def on_press(self, key):
        if key == keyboard.Key.alt_l:
            if not self.is_foreground: 
                if not self.l_alt_pressed:
                    self.l_alt_pressed = True
                    self.bring_to_foreground()
                    self.is_foreground = True
                    print("L-ALT gedrückt und Fenster in den Vordergrund gebracht.")
            else:
                print("L-ALT gedrückt, aber Fenster war bereits im Vordergrund.")

        
    def on_release(self, key):
        if key == keyboard.Key.alt_l:
            self.l_alt_pressed = False
            print("L-ALT losgelassen.")
            if self.is_foreground:
                self.is_foreground = False
                print("Fokusstatus zurückgesetzt, Fenster kann wieder in den Vordergrund gebracht werden.")

        
    def bring_to_foreground(self):
        hwnd = self.winId().__int__()
        win32gui.SetForegroundWindow(hwnd)
        self.setFocus()
        self.is_foreground = True
        print("Fenster in den Vordergrund gebracht und Fokus gesetzt.")
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
        print("L-ALT-Taste losgelassen, um potenzielle Blockaden zu vermeiden.")

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        try:
            self.drawBalls(qp)
            self.drawGuidelines(qp)
            self.drawCollisionPoints(qp)
            print("Paint event: Balls, guidelines, and collision points drawn.")
        except Exception as e:
            print(f"Error in paintEvent: {e}")

    def drawBalls(self, qp):
        for ball in self.balls:
            color = QColor(*ball.color)
            color.setAlphaF(0.8)
            qp.setBrush(QBrush(color))
            qp.setPen(Qt.NoPen)
            qp.drawEllipse(QPointF(ball.x, ball.y), ball.radius, ball.radius)
            print(f"Ball drawn at ({ball.x}, {ball.y}) with radius {ball.radius}.")

    def drawGuidelines(self, qp):
        for ball in self.balls:
            self.drawBallGuidelines(qp, ball)
            print(f"Guidelines drawn for ball at ({ball.x}, {ball.y}).")


    def drawBallGuidelines(self, qp, ball):
        if ball == self.balls[0]:
            direction = QPointF(self.mouse_pos.x() - ball.x, self.mouse_pos.y() - ball.y)
            length = math.sqrt(direction.x()**2 + direction.y()**2)
            if length == 0:
                print("Direction length is zero for the main ball.")
                return
            direction.setX(direction.x() / length)
            direction.setY(direction.y() / length)

            ball.velocity = (direction.x(), direction.y())
        else:
            if ball.new_velocity:
                direction = QPointF(ball.new_velocity[0], ball.new_velocity[1])
            else:
                direction = QPointF(ball.velocity[0], ball.velocity[1])

        print(f"Drawing guidelines for ball at ({ball.x}, {ball.y}) with direction {direction}.")
        length = 1600

        qp.setPen(QPen(Qt.white, 1, Qt.SolidLine))
        qp.drawLine(QPointF(ball.x, ball.y), QPointF(ball.x + direction.x() * length, ball.y + direction.y() * length))

        normal = QPointF(-direction.y(), direction.x())
        qp.setPen(QPen(Qt.yellow, 1, Qt.DotLine))
        qp.drawLine(QPointF(ball.x + normal.x() * ball.radius, ball.y + normal.y() * ball.radius),
                    QPointF(ball.x + normal.x() * ball.radius + direction.x() * length,
                            ball.y + normal.y() * ball.radius + direction.y() * length))
        qp.drawLine(QPointF(ball.x - normal.x() * ball.radius, ball.y - normal.y() * ball.radius),
                    QPointF(ball.x - normal.x() * ball.radius + direction.x() * length,
                            ball.y - normal.y() * ball.radius + direction.y() * length))

        # Zeichnen der Kollisionslinie durch den Kollisionspunkt und Mittelpunkt
        if ball.collision_point:
            coll_x, coll_y = ball.collision_point
            center_x, center_y = ball.collision_other.x, ball.collision_other.y
            ref_dir_x = center_x - coll_x
            ref_dir_y = center_y - coll_y
            ref_length = math.sqrt(ref_dir_x**2 + ref_dir_y**2)
            if ref_length != 0:
                ref_dir_x /= ref_length
                ref_dir_y /= ref_length

                # Zeichne die Linie durch den Kollisionspunkt und den Mittelpunkt der Kugel
                qp.setPen(QPen(Qt.cyan, 1, Qt.SolidLine))
                qp.drawLine(QPointF(coll_x, coll_y), QPointF(center_x, center_y))
                # Verlängere die Linie durch den Mittelpunkt hinaus
                qp.drawLine(QPointF(center_x, center_y), 
                            QPointF(center_x + ref_dir_x * 1600, center_y + ref_dir_y * 1600))

                # Zeichnen der parallelen Linien
                self.drawParallelLines(qp, coll_x, coll_y, center_x, center_y, ball.radius)

                # Kollisionserkennung für die getroffene Kugel
                if ball.collision_other:
                    ball.collision_other.calculate_secondary_collision_point(self.balls)
                    self.drawSecondaryGuidelines(qp, ball.collision_other)
            else:
                print("Reference direction length is zero; cannot draw collision line.")
        else:
            print("No collision point; no collision lines drawn.")



    def drawParallelLines(self, qp, coll_x, coll_y, center_x, center_y, radius):
        # Berechnung der Richtung der Linie
        direction = QPointF(center_x - coll_x, center_y - coll_y)
        length = math.sqrt(direction.x()**2 + direction.y()**2)
        if length == 0:
            print("Direction length is zero; cannot draw parallel lines.")
            return
        direction.setX(direction.x() / length)
        direction.setY(direction.y() / length)

        # Berechnung der Normalen zur Linie
        normal = QPointF(-direction.y(), direction.x())

        # Berechnung der Punkte für die parallelen Linien
        offset_up = QPointF(coll_x + normal.x() * radius, coll_y + normal.y() * radius)
        offset_down = QPointF(coll_x - normal.x() * radius, coll_y - normal.y() * radius)
        end_up = QPointF(center_x + normal.x() * radius, center_y + normal.y() * radius)
        end_down = QPointF(center_x - normal.x() * radius, center_y - normal.y() * radius)

        # Zeichnen der oberen parallelen Linie
        qp.setPen(QPen(Qt.green, 1, Qt.SolidLine))
        qp.drawLine(QPointF(offset_up.x(), offset_up.y()), QPointF(end_up.x(), end_up.y()))
        qp.drawLine(QPointF(end_up.x(), end_up.y()), QPointF(end_up.x() + direction.x() * 1600, end_up.y() + direction.y() * 1600))

        # Zeichnen der unteren parallelen Linie
        qp.drawLine(QPointF(offset_down.x(), offset_down.y()), QPointF(end_down.x(), end_down.y()))
        qp.drawLine(QPointF(end_down.x(), end_down.y()), QPointF(end_down.x() + direction.x() * 1600, end_down.y() + direction.y() * 1600))

        print(f"Parallel lines drawn from collision point ({coll_x}, {coll_y}) through center ({center_x}, {center_y}).")


    def drawSecondaryGuidelines(self, qp, ball):
        if ball.secondary_collision_point:
            coll_x, coll_y = ball.secondary_collision_point
            center_x, center_y = ball.secondary_collision_other.x, ball.secondary_collision_other.y
            ref_dir_x = center_x - coll_x
            ref_dir_y = center_y - coll_y
            ref_length = math.sqrt(ref_dir_x**2 + ref_dir_y**2)
            if ref_length != 0:
                ref_dir_x /= ref_length
                ref_dir_y /= ref_length

                # Zeichne die sekundäre Kollisionslinie
                qp.setPen(QPen(Qt.magenta, 1, Qt.SolidLine))
                qp.drawLine(QPointF(coll_x, coll_y), QPointF(center_x, center_y))
                qp.drawLine(QPointF(center_x, center_y), 
                            QPointF(center_x + ref_dir_x * 1600, center_y + ref_dir_y * 1600))

                print(f"Secondary collision line drawn from ({coll_x}, {coll_y}) to ({center_x}, {center_y}).")
            else:
                print("Reference direction length is zero; cannot draw secondary collision line.")
        else:
            print("No secondary collision point; no secondary guidelines drawn.")


    def drawCollisionPoints(self, qp):
        for ball in self.balls:
            if ball.collision_point:
                x, y = ball.collision_point
                print(f"Drawing collision point at: ({x}, {y})")
                qp.setPen(QPen(Qt.white, 2))
                qp.drawPoint(QPointF(x, y))
            if ball.secondary_collision_point:
                x, y = ball.secondary_collision_point
                print(f"Drawing secondary collision point at: ({x}, {y})")
                qp.setPen(QPen(Qt.red, 2))
                qp.drawPoint(QPointF(x, y))
                
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Control:
            # Umschalten des eingefrorenen Zustands des Overlays
            self.overlay_frozen = not self.overlay_frozen
            print(f"Overlay frozen state: {self.overlay_frozen}")
        elif not self.overlay_frozen:
            ball = None
            # Auswahl des entsprechenden Balls basierend auf der gedrückten Taste
            if event.key() == Qt.Key_1:
                ball = self.balls[0]
            elif event.key() == Qt.Key_2:
                ball = self.balls[1]
            elif event.key() == Qt.Key_3:
                ball = self.balls[2]
            else:
                # Überprüfen, ob die Steuerungstaste eines Balls gedrückt wurde
                for ball in self.balls:
                    if event.key() == ball.control_key:
                        ball.follow_mouse = True
                        print(f"Ball at ({ball.x}, {ball.y}) now follows mouse.")
                return  # Keine weiteren Aktionen erforderlich, wenn keine der Tasten 1, 2 oder 3 gedrückt wurde

            if ball is not None:
                # Konvertieren der globalen Mausposition in Widget-Koordinaten
                global_mouse_pos = QCursor.pos()
                widget_mouse_pos = self.mapFromGlobal(global_mouse_pos)
                ball.set_position(widget_mouse_pos.x(), widget_mouse_pos.y())
                print(f"Ball moved to mouse position at ({widget_mouse_pos.x()}, {widget_mouse_pos.y()}).")
                self.update()


    def update(self):
        if not self.overlay_frozen:
            super().update()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.freeze_mouse = False
            print("Control key released; freeze_mouse set to False.")
        else:
            for ball in self.balls:
                if event.key() == ball.control_key:
                    ball.follow_mouse = False
                    print(f"Ball at ({ball.x}, {ball.y}) stopped following mouse.")


    def would_collide(self, ball, new_x, new_y, other):
        dx = new_x - other.x
        dy = new_y - other.y
        distance = math.sqrt(dx**2 + dy**2)
        collision = distance < ball.radius + other.radius
        print(f"Checking collision: ball at ({ball.x}, {ball.y}), other at ({other.x}, {other.y}), distance={distance}, collision={collision}")
        return collision

    
    def mousePressEvent(self, event):
        pos = event.pos()
        for ball in self.balls:
            distance = math.sqrt((pos.x() - ball.x)**2 + (pos.y() - ball.y)**2)
            if distance <= ball.radius:
                self.current_ball = ball
                ball.follow_mouse = True
                print(f"Mouse pressed at ({pos.x()}, {pos.y()}), ball at ({ball.x}, {ball.y}) selected.")
                break

            
    def mouseMoveEvent(self, event):
        if not self.overlay_frozen:
            global_mouse_pos = QCursor.pos()
            widget_mouse_pos = self.mapFromGlobal(global_mouse_pos)

            print(f"Global mouse moved to: ({global_mouse_pos.x()}, {global_mouse_pos.y()})")
            print(f"Mouse in widget coordinates: ({widget_mouse_pos.x()}, {widget_mouse_pos.y()})")

            self.mouse_pos = widget_mouse_pos
            print(f"Mouse moved to: ({self.mouse_pos.x()}, {self.mouse_pos.y()})")

            if self.current_ball and self.current_ball.follow_mouse:
                self.current_ball.set_position(self.mouse_pos.x(), self.mouse_pos.y())
                print(f"Current ball moved to: ({self.current_ball.x}, {self.current_ball.y})")
                self.update()
            elif self.l_alt_pressed:
                main_ball = self.balls[0]
                dx = self.mouse_pos.x() - main_ball.x
                dy = self.mouse_pos.y() - main_ball.y
                angle = math.atan2(dy, dx)

                # Hier wird die velocity aktualisiert, basierend auf der Mausbewegung
                speed = 1  # Beispielhafte Geschwindigkeit, kann angepasst werden
                main_ball.velocity = (speed * math.cos(angle), speed * math.sin(angle))

                print(f"Main ball at: ({main_ball.x}, {main_ball.y})")
                print(f"dx: {dx}, dy: {dy}, angle: {math.degrees(angle)} degrees")
                print(f"New velocity: {main_ball.velocity}")
            
                self.update()
  
    def mouseReleaseEvent(self, event):
        if self.current_ball:
            print(f"Mouse released. Ball at ({self.current_ball.x}, {self.current_ball.y}) stopped following mouse.")
            self.current_ball.follow_mouse = False
            self.current_ball = None


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

if __name__ == '__main__':
    app = BilliardApp()
    app.run()

