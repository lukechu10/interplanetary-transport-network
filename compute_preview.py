from manim.utils.color.XKCD import LIMEGREEN
import numpy as np
from manim import *
from manim.opengl import *
from manim_slides.slide import Slide

class LeoToMoonCompute(Slide):
    def construct(self):
        print("Loading data")
        bodies_data = np.load("data/leo_to_moon_compute_bodies.npy")
        ship_data = np.load("data/leo_to_moon_compute_ships.npy")
        time_steps = bodies_data.shape[0]
        assert ship_data.shape[0] == time_steps, "ship data and bodies data should have the same number of time steps"
        bodies_count = bodies_data.shape[1]

        ship_data = ship_data.reshape((time_steps, -1, 2))

        print("Transforming to Earth frame")
        # Transform positions to (non-corotating) Earth frame.
        earth_pos = bodies_data[:, 1].reshape((time_steps, 1, 2))
        ship_data -= earth_pos
        bodies_data -= earth_pos

        print("Done!")

        # Apply scaling so that everything fits on the screen
        scale = 3

        colors = [YELLOW, BLUE, GRAY]
        body_dots = []
        for i in range(bodies_count):
            color = colors[i % len(colors)]
            body_dots.append(Dot(color=color, point=[bodies_data[0,i,0] * scale, bodies_data[0,i,1] * scale, 0])) # type: ignore

        self.add(*body_dots)

        self.wait(0.1)

        self.next_slide()

        # Add ships
        ship_dots = TrueDot(center=ORIGIN)
        ship_dots.clear_points()
        ship_points = np.pad(ship_data[0] * scale, ((0, 0), (0, 1)), mode="constant")
        ship_dots.add_points(ship_points)
        ship_dots.set_color(WHITE)

        self.add(ship_dots)
        self.wait(0.1)

        self.next_slide()

        time_step = ValueTracker(0)
        def update(data, n):
            def f(mob):
                coords = data[int((len(data) - 1) * time_step.get_value()), n] * scale
                mob.move_to((coords[0], coords[1], 0))
            return f
        for i in range(bodies_count):
            body_dots[i].add_updater(update(bodies_data, i))

        def update_ships(mob: TrueDot):
            time_index = int((len(ship_data) - 1) * time_step.get_value())
            ship_points = np.pad(ship_data[time_index] * scale, ((0, 0), (0, 1)), mode="constant")

            mob.clear_points()
            mob.add_points(ship_points)
        ship_dots.add_updater(update_ships)


        self.play(time_step.animate.set_value(1), run_time=25, rate_func=linear)
        self.interactive_embed()

class LeoToMoonTest(Slide):
    def construct(self):
        print("Loading data")
        bodies_data = np.load("data/leo_to_moon_test_bodies.npy")
        ship_data = np.load("data/leo_to_moon_test_ships.npy")
        time_steps = bodies_data.shape[0]
        assert ship_data.shape[0] == time_steps, "ship data and bodies data should have the same number of time steps"
        bodies_count = bodies_data.shape[1]

        print("Transforming to Earth frame")
        # Transform positions to (non-corotating) Earth frame.
        earth_pos = bodies_data[:, 1].reshape((time_steps, 1, 2))
        ship_data -= earth_pos
        bodies_data -= earth_pos

        print("Done!")

        # Apply scaling so that everything fits on the screen
        scale = 1

        colors = [YELLOW, BLUE, GRAY]
        body_dots = []
        for i in range(bodies_count):
            color = colors[i % len(colors)]
            body_dots.append(Dot(color=color, point=[bodies_data[0,i,0] * scale, bodies_data[0,i,1] * scale, 0])) # type: ignore

        self.add(*body_dots)

        self.wait(0.1)

        self.next_slide()

        # Add ships
        ship_dots = TrueDot(center=ORIGIN)
        ship_dots.clear_points()
        ship_points = np.pad(ship_data[0] * scale, ((0, 0), (0, 1)), mode="constant")
        ship_dots.add_points(ship_points)
        ship_dots.set_color(WHITE)

        self.add(ship_dots)
        self.wait(0.1)

        best_ship = np.load("data/leo_to_moon_test_best_ship.npy")[0]
        best_ship_start = ship_data[0, best_ship]
        best_ship_dot = Dot(color=LIMEGREEN, point=(best_ship_start[0] * scale, best_ship_start[1] * scale, 0)) # type: ignore

        best_ship_trace = TracedPath(best_ship_dot.get_center, stroke_color=LIMEGREEN, stroke_width=2)
        self.add(best_ship_trace, best_ship_dot)

        # L1 Lagrange point circle
        l1_circle = Circle(radius=3.902 * scale, color=BLUE)
        self.add(l1_circle)

        self.next_slide()

        time_step = ValueTracker(0)

        def update(data, n):
            def f(mob):
                coords = data[int((len(data) - 1) * time_step.get_value()), n] * scale
                mob.move_to((coords[0], coords[1], 0))
            return f
        for i in range(bodies_count):
            body_dots[i].add_updater(update(bodies_data, i))

        def update_ships(mob: TrueDot):
            time_index = int((len(ship_data) - 1) * time_step.get_value())
            ship_points = np.pad(ship_data[time_index] * scale, ((0, 0), (0, 1)), mode="constant")

            mob.clear_points()
            mob.add_points(ship_points)
        ship_dots.add_updater(update_ships)

        def update_best_ship(mob: Dot):
            time_index = int((len(ship_data) - 1) * time_step.get_value())
            coords = ship_data[time_index, best_ship] * scale
            mob.move_to((coords[0], coords[1], 0))
        best_ship_dot.add_updater(update_best_ship)

        self.play(time_step.animate.set_value(1), run_time=10, rate_func=linear)
        self.interactive_embed()

class HaloOrbitsPreview(Slide):
    def construct(self):
        print("Loading data")
        search_data = np.load("data/halo_orbits_sun_earth_search.npy")
        l1 = np.array([0.9900268049994121, 0])

        print("Transforming to frame centered on L1")
        search_data -= l1.reshape((1, 1, 2))

        # Get rid of any values under y=0
        np.clip(search_data[:,:,1], 0, None, out=search_data[:,:,1])
        print("Done!")

        m1 = 1.
        m2 = 1/333_480
        mu = m1 * m2 / (m1 + m2)

        # Apply scaling so that everything fits on the screen
        scale = 200

        # Add L1 point
        l1_dot = Dot(point=(0, 0, 0), color=WHITE)
        l1_label = MathTex("L_1").next_to(l1_dot, DOWN)
        self.add(l1_dot, l1_label)

        # Add y=0 line
        y_line = Line(start=(-8, 0, 0), end=(8, 0, 0), color=WHITE)
        self.add(y_line)

        # Add Earth, Sun points
        earth_r = [1 - mu, 0] - l1
        earth_dot = Dot(point=(*earth_r * scale, 0), color=GRAY)
        earth_label = Text("Earth", font_size=14).next_to(earth_dot, DOWN)
        self.add(earth_dot, earth_label)

        sun_r = [-mu, 0] - l1
        sun_dot = Dot(point=(*sun_r * scale, 0), color=GRAY)
        sun_label = Text("Sun", font_size=14).next_to(sun_dot, DOWN)
        self.add(sun_dot, sun_label)

        # Add Moon point
        earth_moon_mu = 0.0123 / (1 + 0.0123)
        moon_r = earth_r + np.array([1 - earth_moon_mu, 0]) / 387.6
        moon_dot = Dot(point=(*moon_r * scale, 0), color=GRAY)
        moon_label = Text("Moon", font_size=14).next_to(moon_dot, DOWN)
        self.add(moon_dot, moon_label)

        # Add ships
        ship_dots = TrueDot(center=ORIGIN)
        ship_dots.clear_points()
        ship_points = np.pad(search_data[0] * scale, ((0, 0), (0, 1)), mode="constant")
        ship_dots.add_points(ship_points)
        ship_dots.set_color(WHITE)
        self.add(ship_dots)

        # Add a trace on all the ships except the first one.
        search_traces = VGroup()
        for i in range(search_data.shape[1]):
            trace = TracedPath(lambda i=i: ship_dots.points[i], stroke_color=WHITE)
            search_traces.add(trace)
        self.add(search_traces)

        self.wait(0.1)
        self.next_slide()

        time_step = ValueTracker(0)

        def update_ships(mob: TrueDot):
            time_index = int((len(search_data) - 1) * time_step.get_value())
            ship_points = np.pad(search_data[time_index] * scale, ((0, 0), (0, 1)), mode="constant")

            mob.clear_points()
            mob.add_points(ship_points)
            mob.set_color(WHITE)
        ship_dots.add_updater(update_ships)

        self.play(time_step.animate.set_value(1), run_time=4, rate_func=smooth)
        self.next_slide()

        self.interactive_embed()
