import math

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


# Weitere physikalische Funktionen hier
