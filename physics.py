#physics.py
import math

class Ball:
    def __init__(self, x, y, radius, color, control_key=None, new_velocity=None):
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

    def calculate_theoretical_collision(self, other):
        if self.new_velocity is None or self.new_velocity == (0, 0):
            return

        # Line segment start and end points (ray)
        ray_start = (self.x, self.y)
        ray_end = (self.x + self.new_velocity[0], self.y + self.new_velocity[1])

        # Vector from the start of the ray to the other ball's center
        to_circle = (other.x - ray_start[0], other.y - ray_start[1])

        # Projection length
        ray_dir = (ray_end[0] - ray_start[0], ray_end[1] - ray_start[1])
        ray_length = math.sqrt(ray_dir[0] ** 2 + ray_dir[1] ** 2)
        if ray_length == 0:
            return
        ray_dir_normalized = (ray_dir[0] / ray_length, ray_dir[1] / ray_length)

        projection_length = to_circle[0] * ray_dir_normalized[0] + to_circle[1] * ray_dir_normalized[1]

        # Closest point on the ray to the other ball's center
        closest_point = (ray_start[0] + ray_dir_normalized[0] * projection_length,
                         ray_start[1] + ray_dir_normalized[1] * projection_length)

        # Distance from the closest point to the other ball's center
        closest_distance = math.sqrt((closest_point[0] - other.x) ** 2 +
                                     (closest_point[1] - other.y) ** 2)

        if closest_distance <= other.radius + self.radius:
            self.collision_point = closest_point
            self.collision_other = other
        else:
            self.collision_point = None
            self.collision_other = None

    def simulate_path_and_check_collision(self, other_balls, max_steps=1000, step_size=0.1):
        if self.new_velocity is None:
            return None, None

        velocity_x, velocity_y = self.new_velocity
        projected_x = self.x
        projected_y = self.y

        for step in range(max_steps):
            # Bewege die Phantomkugel entlang der berechneten Bahn
            projected_x += velocity_x * step_size
            projected_y += velocity_y * step_size
            

            # Überprüfe Kollisionen mit allen anderen Kugeln
            for other in other_balls:
                if other != self:  # Ausschluss der eigenen Kugel
                    dx = other.x - projected_x
                    dy = other.y - projected_y
                    center_distance = math.sqrt(dx**2 + dy**2)
                    

                    if center_distance <= (self.radius + other.radius):
                        # Berechnung des Kontaktpunkts
                        normal = (dx / center_distance, dy / center_distance)
                        contact_x = other.x - normal[0] * other.radius
                        contact_y = other.y - normal[1] * other.radius
                        return (contact_x, contact_y), other
                    

        return None, None


# Beispiel-Testfälle zur Veranschaulichung der Funktionalität

# Fall: Kollision des Hauptballs (ball1) mit ball2, gefolgt von einer möglichen Projektion und Kollision von ball2 mit ball3
ball1 = Ball(100, 100, 18, (255, 0, 0))
ball2 = Ball(130, 100, 18, (0, 255, 0))
ball3 = Ball(160, 100, 18, (0, 0, 255))

ball1.velocity = (10, 0)  # Bewegt sich horizontal auf ball2 zu
ball1.calculate_theoretical_collision(ball2)
if ball1.collision_point:
    print(f"Erste Kollision: {ball1.collision_point} mit Ball 2")

# Projektion der Bewegung von ball2 nach der Kollision
collision_point_secondary, colliding_ball_secondary = ball2.simulate_path_and_check_collision([ball1, ball3])
if collision_point_secondary:
    print(f"Zweite Kollision: {collision_point_secondary} mit Ball 3")
else:
    print("Keine zweite Kollision festgestellt.")
    pass


# Weitere physikalische Funktionen hier
