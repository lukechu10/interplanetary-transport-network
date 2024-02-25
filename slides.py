import numpy as np
from manim import *
from manim.opengl import *
from manim_slides.slide import Slide, ThreeDSlide

EARTH_MASS = 1.0
MOON_MASS = 0.0123
EARTH_MOON_MU = EARTH_MASS * MOON_MASS / (EARTH_MASS + MOON_MASS)

# ----------
# Slides
# ----------

class TitleSlide(Slide):
    def construct(self):
        title = Text("Budget-friendly space travel")
        author = Text("Luke Chu").next_to(title, DOWN)
        author.font_size = 18

        date = Text("6 March 2024").to_corner(DR)
        date.font_size = 12

        self.add(title, author, date)
        self.wait()

# TODO: Fix layout, add animations
class ReducedNBodyProblem(Slide):
    def construct(self):
        left = VGroup(Text("Full n-body problem"), Tex("3 bodies"), Tex("3 forces")).arrange(DOWN)
        center = VGroup(Text("Planets"), Tex("2 bodies"), Tex("2 forces")).arrange(DOWN)
        right = VGroup(Text("Ship reaction"), Tex("1 body"), Tex("2 forces")).arrange(DOWN)

        left.align_on_border(LEFT)
        center.next_to(left, RIGHT)
        right.next_to(center, RIGHT)

        self.play(Write(left))
        self.play(Write(center), Write(right))


# 1. Building a tracer.
class Part1(Slide):
    def construct(self):
        pass

# 2. Phase space
class Part2(Slide):
    def construct(self):
        pass

# 3. The 3-body problem
class Part3(Slide):
    def construct(self):

        pass

# 3.c. Effective potential.
class EffectivePotential(ThreeDSlide):
    def construct(self):
        scale = 2

        axes = ThreeDAxes()

        x_label = axes.get_x_axis_label(Tex("x"))
        y_label = axes.get_y_axis_label(Tex("y")).shift(UP * 1.8)
        z_label = axes.get_z_axis_label(Tex("V(x, y)"))

        # self.set_camera_orientation(zoom=0.5)

        self.play(Create(axes), FadeIn(x_label), FadeIn(y_label), FadeIn(z_label))


        earth_pos = np.array([-EARTH_MOON_MU, 0, 0])
        earth = Dot3D(point=earth_pos * scale, color=BLUE, radius=0.2)
        moon_pos = np.array([1 - EARTH_MOON_MU, 0, 0])
        moon = Dot3D(point=moon_pos * scale, color=GRAY, radius=0.1)
        self.play(Create(earth), Create(moon))

        self.move_camera(phi=50 * DEGREES, theta=-60 * DEGREES, zoom=1, run_time=1.5)

        def grav_potential(x, y):
            pos = np.array([x, y, 0])
            r_earth = earth_pos - pos
            r_moon = moon_pos - pos
            return -1 / np.linalg.norm(r_earth) - 0.0123 / np.linalg.norm(r_moon)

        grav_potential_surface = OpenGLSurface(
            uv_func=lambda u, v: np.array([u, v, max(grav_potential(u, v), -20)]) * scale,
            u_range=[-1.5, 1.5], v_range=[-1.5,1.5],
            axes=axes,
            color=RED,
            resolution=(64, 64),
            opacity=0.5,
        )
        self.play(Create(grav_potential_surface))
        
        def centripetal_potential(x, y):
            # Fc = m omega^2 r so Vc = omega^2 r^2 / 2
            r_squared = x * x + y * y
            omega = 1
            return - (omega ** 2) * r_squared / 2
        
        def effective_potential(x, y):
            return grav_potential(x, y) + centripetal_potential(x, y)

        effective_potential_surface = OpenGLSurface(
            uv_func=lambda u, v: np.array([u, v, max(effective_potential(u, v), -20)]) * scale,
            u_range=[-1.5, 1.5], v_range=[-1.5,1.5],
            axes=axes,
            color=BLUE,
            resolution=(64, 64),
            opacity=0.5,
        )
        self.play(Transform(grav_potential_surface, effective_potential_surface))
        self.interactive_embed()

# 4. Stable and unstable manifolds
class Part4(Slide):
    def construct(self):
        pass

# 5. The interplanetary transport network
class Part5(Slide):
    def construct(self):
        pass

class PartN(Slide):
    def construct(self):
        bodies_data = np.load("data/bodies.npy")
        ships_data = np.load("data/ships.npy")
        bodies_count = len(bodies_data[0])
        ships_count = len(ships_data[0])

        # Apply scaling so that everything fits on the screen
        scale = 2

        number_plane = NumberPlane(background_line_style={
            "stroke_color": BLUE,
            "stroke_width": 2,
            "stroke_opacity": 0.5
        })
        self.add(number_plane)

        colors = [BLUE, GRAY, RED, YELLOW, PURPLE]
        dots = []
        for i in range(bodies_count):
            color = colors[i % len(colors)]
            dots.append(Dot(color=color).set_x(bodies_data[0][i][0] * scale).set_y(bodies_data[0][i][1] * scale))

        self.add(*dots)

        self.next_slide()

        # Add ships
        ship_dots = []
        ship_colors = [RED, YELLOW, PURPLE, GREEN, ORANGE]
        for i in range(ships_count):
            color = ship_colors[i % len(ship_colors)]
            ship_dots.append(Dot(color=color).set_x(ships_data[0][i][0] * scale).set_y(ships_data[0][i][1] * scale))
        ship_traces = []
        for i in range(ships_count):
            color = ship_colors[i % len(ship_colors)]
            ship_traces.append(TracedPath(ship_dots[i].get_center, stroke_color=color, dissipating_time=0.3))

        self.add(*ship_dots)
        self.add(*ship_traces)

        self.next_slide()

        time_step = ValueTracker(0)
        def update(data, n):
            def f(mob):
                coords = data[int((len(data) - 1) * time_step.get_value())][n] * scale
                mob.move_to((coords[0], coords[1], 0))
            return f
        for i in range(bodies_count):
            dots[i].add_updater(update(bodies_data, i))
        for i in range(ships_count):
            ship_dots[i].add_updater(update(ships_data, i))


        self.play(time_step.animate.set_value(1), run_time=10, rate_func=linear)
