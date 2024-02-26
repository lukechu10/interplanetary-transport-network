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
            uv_func=lambda u, v: np.array([u, v, max(effective_potential(u, v), -20) + 1]) * scale,
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
        bodies_data = np.load("data/part1b_bodies.npy")
        ship_data = np.load("data/part1b_ships.npy")
        bodies_count = len(bodies_data[0])
        ships_count = len(ship_data[0])

        # Apply scaling so that everything fits on the screen
        scale = 3

        number_plane = NumberPlane(background_line_style={
            "stroke_color": BLUE,
            "stroke_width": 2,
            "stroke_opacity": 0.5
        })
        self.add(number_plane)

        colors = [RED]
        dots = []
        for i in range(bodies_count):
            color = colors[i % len(colors)]
            dots.append(Dot(color=color, point=[bodies_data[0,i,0] * scale, bodies_data[0,i,1] * scale, 0])) # type: ignore

        self.add(*dots)

        self.next_slide()

        # Add ships
        ship_dots = TrueDot(center=ORIGIN)
        ship_dots.clear_points()
        ship_points = np.pad(ship_data[0] * scale, ((0, 0), (0, 1)), mode="constant")
        ship_dots.add_points(ship_points)
        ship_dots.set_color(WHITE)

        self.add(ship_dots)

        self.next_slide()

        time_step = ValueTracker(0)
        def update(data, n):
            def f(mob):
                coords = data[int((len(data) - 1) * time_step.get_value()), n] * scale
                mob.move_to((coords[0], coords[1], 0))
            return f
        for i in range(bodies_count):
            dots[i].add_updater(update(bodies_data, i))

        def update_ships(mob):
            ship_points = np.pad(ship_data[int((len(ship_data) - 1) * time_step.get_value())] * scale, ((0, 0), (0, 1)), mode="constant")
            mob.clear_points()
            mob.add_points(ship_points)
            mob.set_color(WHITE)
        ship_dots.add_updater(update_ships)


        self.play(time_step.animate.set_value(1), run_time=25, rate_func=linear)
        self.interactive_embed()
