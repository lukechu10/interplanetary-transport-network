from manim.utils.color.XKCD import LIMEGREEN
import numpy as np
from manim import *
from manim.opengl import *
from manim_slides.slide import Slide

class EmptyScene(Scene):
    def construct(self):
        self.interactive_embed()

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
        m2 = 1/333000
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

class Manifolds3BodyPreview(Slide):
    def construct(self):
        # === Sun-Earth manifolds ===
        print("Loading data")
        orbit_data = np.load("data/manifolds_sun_earth_orbit.npy")
        unstable_data = np.load("data/manifolds_sun_earth_unstable.npy")
        stable_data = np.load("data/manifolds_sun_earth_stable.npy")
        l1_sun_earth = np.load("data/manifolds_sun_earth_l1.npy")
        
        m1 = 1
        m2 = 1/333000
        mu = m1 * m2 / (m1 + m2)
        earth_pos = np.array([1 - mu, 0])
        earth_pos = earth_pos.reshape((1, 1, 2))

        # Transform positions so that Earth is at the origin.
        orbit_data -= earth_pos
        unstable_data -= earth_pos
        stable_data -= earth_pos
        l1_sun_earth -= earth_pos.reshape(2)

        # Apply scaling so that everything fits on the screen
        scale = 200

        # Add L1 point
        l1_dot = Dot(point=(*l1_sun_earth * scale, 0), color=WHITE, radius=0.04)
        l1_label = MathTex("L_1", font_size=14).next_to(l1_dot, DOWN)
        self.add(l1_dot, l1_label)

        # Center on Earth.
        earth_r = np.array([0, 0])
        earth_dot = Dot(point=(*earth_r * scale, 0), color=GRAY)
        earth_label = Text("Earth", font_size=14).next_to(earth_dot, DOWN)
        self.add(earth_dot, earth_label)

        self.wait(0.1)
        self.next_slide()

        # Add ships
        unstable_dots = TrueDot(center=ORIGIN)
        unstable_dots.clear_points()
        unstable_points = np.pad(unstable_data[0] * scale, ((0, 0), (0, 1)), mode="constant")
        unstable_dots.add_points(unstable_points)
        unstable_dots.set_color(RED)
        self.add(unstable_dots)

        stable_dots = TrueDot(center=ORIGIN)
        stable_dots.clear_points()
        stable_points = np.pad(stable_data[0] * scale, ((0, 0), (0, 1)), mode="constant")
        stable_dots.add_points(stable_points)
        stable_dots.set_color(BLUE)
        self.add(stable_dots)

        # Add a trace on all the ships
        unstable_traces = VGroup()
        for i in range(0, unstable_data.shape[1]):
            trace = TracedPath(lambda i=i: unstable_dots.points[i], stroke_color=RED)
            unstable_traces.add(trace)
        self.add(unstable_traces)

        stable_traces = VGroup()
        for i in range(0, stable_data.shape[1]):
            trace = TracedPath(lambda i=i: stable_dots.points[i], stroke_color=BLUE)
            stable_traces.add(trace)
        self.add(stable_traces)
        
        self.wait(0.1)
        self.next_slide()

        time_step = ValueTracker(0)

        def update_unstable(mob: TrueDot):
            time_index = int((len(unstable_data) - 1) * time_step.get_value())
            ship_points = np.pad(unstable_data[time_index] * scale, ((0, 0), (0, 1)), mode="constant")

            mob.clear_points()
            mob.add_points(ship_points)
            mob.set_color(RED)
        unstable_dots.add_updater(update_unstable)
        def update_stable(mob: TrueDot):
            time_index = int((len(stable_data) - 1) * time_step.get_value())
            ship_points = np.pad(stable_data[time_index] * scale, ((0, 0), (0, 1)), mode="constant")

            mob.clear_points()
            mob.add_points(ship_points)
            mob.set_color(BLUE)
        stable_dots.add_updater(update_stable)

        # Add orbit trace
        orbit_dot = Dot(point=(*orbit_data[0, 0] * scale, 0)).set_opacity(0)
        self.add(orbit_dot)
        def update_orbit(mob: Dot):
            time_index = int((len(orbit_data) - 1) * time_step.get_value())
            coords = orbit_data[time_index, 0] * scale
            mob.move_to((coords[0], coords[1], 0))
        orbit_trace = TracedPath(orbit_dot.get_center, stroke_color=LIMEGREEN, stroke_width=4)
        orbit_dot.add_updater(update_orbit) # type: ignore
        self.add(orbit_trace)

        # Set opacity
        stable_traces.set_opacity(0.5)
        unstable_traces.set_opacity(0.5)

        self.play(time_step.animate.set_value(1), run_time=8, rate_func=linear)

        legend = VGroup(
            Text("Stable", font_size=22, color=BLUE),
            Text("Unstable", font_size=22, color=RED),
        )
        legend.arrange(DOWN, buff=1).to_edge(LEFT)
        self.play(Write(legend))

        self.next_slide()
        
        self.interactive_embed()

class Manifolds3BodyEarthMoon(Slide):
    def construct(self):
        # === Earth-Moon manifolds ===
        print("Loading data")
        orbit_data = np.load("data/manifolds_earth_moon_orbit.npy")
        unstable_data = np.load("data/manifolds_earth_moon_unstable.npy")
        stable_data = np.load("data/manifolds_earth_moon_stable.npy")

        mu = 1 * 0.0123 / (1 + 0.0123)

        # Apply scaling so that everything fits on the screen
        scale = 6

        earth_r = np.array([-mu, 0])
        # Transform everything to Earth frame
        orbit_data -= earth_r.reshape((1, 1, 2))
        unstable_data -= earth_r.reshape((1, 1, 2))
        stable_data -= earth_r.reshape((1, 1, 2))

        earth_dot = Dot(point=(0, 0, 0), color=GRAY)
        moon_dot = Dot(point=(1, 0, 0), color=GRAY)
        self.add(earth_dot, moon_dot)

        # Add all the unstable manifold ships as parametric functions
        time_steps = unstable_data.shape[0]
        assert stable_data.shape[0] == time_steps, "stable data and unstable data should have the same number of time steps"
        
        num_ships = unstable_data.shape[1]
        assert stable_data.shape[1] == num_ships, "stable data and unstable data should have the same number of ships"

        unstable_traces = VGroup()
        stable_traces = VGroup()
        for i in range(num_ships):
            unstable = ParametricFunction(
                function=lambda t, i=i: (*unstable_data[int(t * (time_steps - 1)), i] * scale, 0),
                t_range=[0, 1],
                color=RED,
            )
            unstable_traces.add(unstable)
            stable = ParametricFunction(
                function=lambda t, i=i: (*stable_data[int(t * (time_steps - 1)), i] * scale, 0),
                t_range=[0, 1],
                color=BLUE,
            )
            stable_traces.add(stable)
        
        orbit_time_steps = orbit_data.shape[0]
        orbit_trace = ParametricFunction(
            function=lambda t: (*orbit_data[int(t * (orbit_time_steps - 1)), 0] * scale, 0),
            t_range=[0, 1],
            color=LIMEGREEN,
        ).set_stroke(width=2)

        unstable_traces.set_stroke(width=1, opacity=0.5)
        stable_traces.set_stroke(width=1, opacity=0.5)

        # Whole frame is constantly rotating.
        omega = (1 + 0.0123) / 1
        always_rotate(unstable_traces, rate=omega, about_point=earth_dot.get_center())
        always_rotate(stable_traces, rate=omega, about_point=earth_dot.get_center())
        always_rotate(orbit_trace, rate=omega, about_point=earth_dot.get_center())
        always_rotate(moon_dot, rate=omega, about_point=earth_dot.get_center())

        self.play(FadeIn(unstable_traces), FadeIn(stable_traces), FadeIn(orbit_trace))
        self.wait(2 * PI / omega) # Full cycle
