#ui.py
import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QCursor
from PyQt5.QtCore import QPointF, Qt, QEvent
from pynput import mouse, keyboard
import win32gui
import win32con
import win32api
import logging

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
            self.drawBalls(qp)  # Zeichnet die realen Bälle
    
            # Für jeden Ball die Projektionen und ggf. Richtlinien zeichnen
            for ball in self.balls:
                self.drawBallProjection(qp, ball, draw_guideline=True, draw_phantom=True)
        except Exception as e:
            logging.error(f"Error in paintEvent: {e}")

    def drawBalls(self, qp):
        for i, ball in enumerate(self.balls):
            # Zeichnen der realen Kugeln
            color = QColor(*ball.color)
            color.setAlphaF(0.8)
            qp.setBrush(QBrush(color))
            qp.setPen(Qt.NoPen)
            qp.drawEllipse(QPointF(ball.x, ball.y), ball.radius, ball.radius)

            # Nummerierung in der Mitte der Kugeln
            qp.setPen(Qt.white)  # Weißer Text für bessere Sichtbarkeit
            font = qp.font()
            font.setPointSize(10)  # Setze eine angemessene Schriftgröße
            qp.setFont(font)
            text_rect = qp.boundingRect(ball.x - ball.radius, ball.y - ball.radius,
                                        ball.radius * 2, ball.radius * 2,
                                        Qt.AlignCenter, str(i + 1))
            qp.drawText(text_rect, Qt.AlignCenter, str(i + 1))
                    
    def drawBallProjection(self, qp, ball, draw_guideline=True, draw_phantom=True, step_size=0.01, max_steps=1000):
        if draw_guideline:
            # Zeichne statische Richtlinien, falls benötigt
            self.drawGuidelinesAndCollisions(qp, ball, show_primary=True, show_parallel=True, show_secondary=True)

        if draw_phantom and ball.new_velocity:
            # Zeichne Phantomkugel basierend auf der Bewegung
            projected_x = ball.x
            projected_y = ball.y
            velocity_x, velocity_y = ball.new_velocity

            for step in range(max_steps):
                projected_x += velocity_x * step_size
                projected_y += velocity_y * step_size
                qp.setBrush(QBrush(QColor(255, 255, 255, 100)))  # Weiß, halbtransparent
                qp.setPen(Qt.NoPen)
                qp.drawEllipse(QPointF(projected_x, projected_y), ball.radius, ball.radius)
        
                # Falls die Projektion den Rand erreicht, beenden
                if projected_x < 0 or projected_x > self.width() or projected_y < 0 or projected_y > self.height():
                    break

                # Falls eine Kollision erkannt wird, zeige den Punkt an
                for other_ball in self.balls:
                    if other_ball != ball:
                        ball.calculate_theoretical_collision(other_ball)
                        if ball.collision_point:
                            self.drawCollisionPoint(qp, ball.collision_point)

    def drawGuidelinesAndCollisions(self, qp, ball, show_primary=True, show_parallel=True, show_secondary=True):
        if show_primary:
            direction = self.getDirection(ball)
            self.drawPrimaryGuideline(qp, ball, direction)

        if show_parallel and ball.collision_point:
            coll_x, coll_y = ball.collision_point
            center_x, center_y = ball.collision_other.x, ball.collision_other.y
            self.drawParallelLines(qp, coll_x, coll_y, ball.collision_other, ball.radius)

        if show_secondary and ball.secondary_collision_point:
            self.drawSecondaryGuidelines(qp, ball)

    def getDirection(self, ball):
        if ball == self.balls[0]:
            direction = QPointF(self.mouse_pos.x() - ball.x, self.mouse_pos.y() - ball.y)
            length = math.sqrt(direction.x()**2 + direction.y()**2)
            if length != 0:
                direction.setX(direction.x() / length)
                direction.setY(direction.y() / length)
        else:
            if ball.new_velocity:
                direction = QPointF(ball.new_velocity[0], ball.new_velocity[1])
            else:
                direction = QPointF(ball.velocity[0], ball.velocity[1])
        return direction

    def drawParallelLines(self, qp, coll_x, coll_y, other_ball, radius):
        center_x, center_y = other_ball.x, other_ball.y
        direction = QPointF(center_x - coll_x, center_y - coll_y)
        length = math.sqrt(direction.x()**2 + direction.y()**2)
        if length == 0:
            print("Direction length is zero; cannot draw parallel lines.")
            return
        direction.setX(direction.x() / length)
        direction.setY(direction.y() / length)

        normal = QPointF(-direction.y(), direction.x())
        offset_up = QPointF(coll_x + normal.x() * radius, coll_y + normal.y() * radius)
        offset_down = QPointF(coll_x - normal.x() * radius, coll_y - normal.y() * radius)
        end_up = QPointF(center_x + normal.x() * radius, center_y + normal.y() * radius)
        end_down = QPointF(center_x - normal.x() * radius, center_y - normal.y() * radius)

        qp.setPen(QPen(Qt.green, 1, Qt.SolidLine))
        qp.drawLine(QPointF(offset_up.x(), offset_up.y()), QPointF(end_up.x(), end_up.y()))
        qp.drawLine(QPointF(end_up.x(), end_up.y()), QPointF(end_up.x() + direction.x() * 1600, end_up.y() + direction.y() * 1600))
        qp.drawLine(QPointF(offset_down.x(), offset_down.y()), QPointF(end_down.x(), end_down.y()))
        qp.drawLine(QPointF(end_down.x(), end_down.y()), QPointF(end_down.x() + direction.x() * 1600, end_down.y() + direction.y() * 1600))

        print(f"Parallel lines drawn from collision point ({coll_x}, {coll_y}) through center ({center_x}, {center_y}).")
        
    def drawPrimaryGuideline(self, qp, ball, direction):
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
        
    def drawCollisionPoint(self, qp, point):
        qp.setPen(QPen(Qt.red, 3))  # Farbe und Dicke des Kollisionspunkts
        qp.drawPoint(QPointF(point[0], point[1]))
             
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