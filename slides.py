import numpy as np
from manim import *
from manim.utils.color.XKCD import LIMEGREEN
from manim.opengl import *
from manim_slides.slide import Slide, ThreeDSlide

# ----------
# Slides
# ----------

class TitleSlide(Slide):
    def construct(self):
        title = Text("Low-energy transfers in space")
        author = Text("Luke Chu").next_to(title, DOWN)
        author.font_size = 18

        date = Text("6 March 2024").to_corner(DR)
        date.font_size = 12

        self.add(title, author, date)
        self.wait(0.1)
        self.next_slide(auto_next=True)

        self.play(FadeOut(title), FadeOut(author), FadeOut(date))
        self.wait(0.1)

class RestrictedNBodyProblem(Slide):
    def construct(self):
        title = Text("Building a tracer").to_edge(UP)
        text = VGroup(
            Text("Restricted n-body problem"),
            Text("Massive bodies (Sun, Earth, Moon, etc...)", font_size=20),
            Text("Spaceships feel influence (but do not influence other bodies themselves)", font_size=20),
        ).arrange(DOWN)

        self.play(Write(title))
        self.next_slide()
        self.play(Write(text))
        self.wait(0.1)

class SinglePlanet(Slide):
    def construct(self):
        axes = NumberPlane(
            x_range=[-3, 3],
            y_range=[-3, 3],
            x_length=8,
            y_length=8,
            background_line_style={
                "stroke_color": BLUE,
                "stroke_width": 3,
                "stroke_opacity": 0.5,
            },
        )

        bodies_data = np.load("data/single_planet_bodies.npy")
        ships_data = np.load("data/single_planet_ships.npy")
        ships_velocity_data = np.load("data/single_planet_ships_initial_velocities.npy")
        assert bodies_data.shape[1] == 1, "should only have one planet for this slide"

        planet = Dot(point=axes.c2p(*bodies_data[0,0]), color=RED, radius=0.2)
        ship_initial = Dot(point=axes.c2p(*ships_data[0,0], 0), color=WHITE, radius=0.1)

        self.add(planet, ship_initial)
        self.wait(0.1)
        self.next_slide()

        v_initial_text = Text(f"v = {ships_velocity_data[0][1]:.2f}", font_size=20).next_to(ship_initial, RIGHT)
        # Push off!
        def pos(t: float, ship_index: int = 0):
            time_step = int(t * ships_data.shape[0])
            return axes.c2p(*ships_data[time_step, ship_index], 0)
        func = ParametricFunction(pos, t_range=[0.0, 0.9]) # type: ignore

        self.play(Write(v_initial_text), Create(func, run_time=3))
        self.next_slide()

        # Vary the velocity now.
        ship_index = ValueTracker(0)
        v_initial_text.add_updater(
            lambda m: m.become(Text(f"v = {ships_velocity_data[int(ship_index.get_value())][1]:.2f}", font_size=20)).next_to(ship_initial, RIGHT), # type: ignore
        )
        func.add_updater(
            lambda m: m.become(ParametricFunction(lambda t: pos(t, int(ship_index.get_value())), t_range=[0.0, 0.9])), # type: ignore
        )
        num_ships = ships_data.shape[1]
        self.play(ship_index.animate.set_value(num_ships - 1), run_time=5, rate_func=smooth)

        self.wait(0.1)
        self.interactive_embed()

class MultiPlanet(Slide):
    def construct(self):
        axes = NumberPlane(
            x_range=[-3, 3],
            y_range=[-3, 3],
            x_length=8,
            y_length=8,
            background_line_style={
                "stroke_color": BLUE,
                "stroke_width": 3,
                "stroke_opacity": 0.5,
            },
        )

        bodies_data = np.load("data/multi_planet_bodies.npy")
        ships_data = np.load("data/multi_planet_ships.npy")
        ships_velocity_data = np.load("data/multi_planet_ships_initial_velocities.npy")
        assert bodies_data.shape[1] == 3, "should only have 3 planets for this slide"

        for i in range(bodies_data.shape[1]):
            planet = Dot(point=axes.c2p(*bodies_data[0,i]), color=RED, radius=0.2)
            self.add(planet)
        
        ship_initial = Dot(point=axes.c2p(*ships_data[0,0], 0), color=WHITE, radius=0.1)

        self.add(ship_initial)
        self.wait(0.1)
        self.next_slide()

        v_initial_text = Text(f"v = {ships_velocity_data[0][1]:.2f}", font_size=20).next_to(ship_initial, RIGHT)
        # Push off!
        def pos(t: float, ship_index: int = 0):
            time_step = int(t * ships_data.shape[0])
            return axes.c2p(*ships_data[time_step, ship_index], 0)
        func = ParametricFunction(pos, t_range=[0.0, 0.9]) # type: ignore

        self.play(Write(v_initial_text), Create(func, run_time=3))
        self.next_slide()

        # Vary the velocity now.
        ship_index = ValueTracker(0)
        v_initial_text.add_updater(
            lambda m: m.become(Text(f"v = {ships_velocity_data[int(ship_index.get_value())][1]:.2f}", font_size=20)).next_to(ship_initial, RIGHT), # type: ignore
        )
        func.add_updater(
            lambda m: m.become(ParametricFunction(lambda t: pos(t, int(ship_index.get_value())), t_range=[0.0, 0.9])), # type: ignore
        )
        num_ships = ships_data.shape[1]
        self.play(ship_index.animate.set_value(num_ships - 1), run_time=10, rate_func=smooth)

        self.wait(0.1)
        self.interactive_embed()

class LeoToMoon(Slide):
    def construct(self):
        print("Loading data")
        bodies_data = np.load("data/leo_to_moon_bodies.npy")
        ship_data = np.load("data/leo_to_moon_ships.npy")
        ship_status = np.load("data/leo_to_moon_ships_status.npy")
        time_steps = bodies_data.shape[0]
        assert ship_data.shape[0] == time_steps, "ship data and bodies data should have the same number of time steps"
        assert ship_status.shape[0] == time_steps, "ship status and bodies data should have the same number of time steps"
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

        l1_circle = Circle(radius=3.902 * scale, color=BLUE)
        self.add(l1_circle)

        l1_label = Text("Earth SOI", font_size=20, color=BLUE).next_to(l1_circle, LEFT)
        self.add(l1_label)

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
        
        best_ship = np.load("data/leo_to_moon_best_ship.npy")[0]
        best_ship_start = ship_data[0, best_ship]
        best_ship_dot = Dot(color=LIMEGREEN, point=(best_ship_start[0] * scale, best_ship_start[1] * scale, 0)) # type: ignore
        best_ship_trace = TracedPath(best_ship_dot.get_center, stroke_color=LIMEGREEN, stroke_width=2)

        self.add(best_ship_trace, best_ship_dot)

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
            # Transform ship status to color codes.
            # 0: default
            # 1: returned to Earth
            # 2: reached Moon
            # 3: captured by Moon
            colors = list(map(ManimColor.to_rgba, [WHITE, DARK_GRAY, RED, LIMEGREEN]))
            convert_to_color = np.vectorize(lambda x: colors[x], signature='()->(4)')
            ship_status_colors = convert_to_color(ship_status[time_index])

            mob.clear_points()
            mob.add_points(ship_points, rgbas=ship_status_colors)
        ship_dots.add_updater(update_ships)

        def update_best_ship(mob: Dot):
            time_index = int((len(ship_data) - 1) * time_step.get_value())
            coords = ship_data[time_index, best_ship] * scale
            mob.move_to((coords[0], coords[1], 0))
        best_ship_dot.add_updater(update_best_ship) # type: ignore

        self.play(time_step.animate.set_value(0.05), run_time=4, rate_func=smooth)
        self.next_slide()
        self.play(time_step.animate.set_value(1), run_time=20, rate_func=smooth)
        self.interactive_embed()

class EffectivePotential(ThreeDSlide):
    m_earth = 1.0
    m_moon = 0.0123
    mu = m_earth * m_moon / (m_earth + m_moon)
    r_earth = [-mu, 0, 0]
    r_moon = [1 - mu, 0, 0]

    def U_grav(self, x: float, y: float) -> float:
        pos = np.array([x, y, 0])
        d_earth = self.r_earth - pos
        d_moon = self.r_moon - pos
        return -self.m_earth / np.linalg.norm(d_earth) - self.m_moon / np.linalg.norm(d_moon) # type: ignore

    def U_centrifugal(self, x: float, y: float) -> float:
        # Fc = m omega^2 r so Vc = omega^2 r^2 / 2
        r_squared = x * x + y * y
        omega = 1
        return - (omega ** 2) * r_squared / 2

    def U_effective(self, x: float, y: float) -> float:
        return self.U_grav(x, y) + self.U_centrifugal(x, y)

    def construct_axes(self):
        self.axes = ThreeDAxes(x_range=[-1.5, 1.5], y_range=[-1.5, 1.5], z_range=[-6, 2], x_length=6, y_length=6, z_length=10)
        x_label = self.axes.get_x_axis_label(Tex("x"))
        y_label = self.axes.get_y_axis_label(Tex("y"), rotation=0)
        z_label = self.axes.get_z_axis_label(Tex("U"))
        earth = Dot3D(point=self.axes.c2p(*self.r_earth), color=BLUE, radius=0.2)
        moon = Dot3D(point=self.axes.c2p(*self.r_moon), color=GRAY, radius=0.1)
        self.play(
            Create(self.axes), FadeIn(x_label), FadeIn(y_label), FadeIn(z_label),
            Create(earth), Create(moon)
        )

    def construct_U_grav(self):
        self.U_grav_eqn = MathTex(r"U_{g} = -G\frac{m_E}{r_E} - G\frac{m_M}{r_M}").to_corner(UL)
        self.add_fixed_in_frame_mobjects(self.U_grav_eqn)

        self.U_grav_surface = OpenGLSurface(
            uv_func=lambda u, v: self.axes.c2p(u, v, self.U_grav(u, v)),
            u_range=[-1.5, 1.5], v_range=[-1.5, 1.5],
            axes=self.axes,
            color=BLUE,
            resolution=(64, 64),
            opacity=0.5,
        )
        self.play(Create(self.U_grav_surface), Write(self.U_grav_eqn))
    
    def construct_U_centrifugal(self):
        self.U_centrifugal_eqn = MathTex(r"U_{c} = -\frac{1}{2} \omega^2 r^2").next_to(self.U_grav_eqn, RIGHT).shift(RIGHT)

        self.U_centrifugal_surface = OpenGLSurface(
            uv_func=lambda u, v: self.axes.c2p(u, v, self.U_centrifugal(u, v)),
            u_range=[-1.5, 1.5], v_range=[-1.5, 1.5],
            axes=self.axes,
            color=PURPLE,
            resolution=(64, 64),
            opacity=0.5,
        )

        self.play(Uncreate(self.U_grav_surface))
        self.add_fixed_in_frame_mobjects(self.U_centrifugal_eqn)
        self.play(Create(self.U_centrifugal_surface), Write(self.U_centrifugal_eqn))
        self.wait(0.1)

    def construct_U_effective(self):
        self.U_effective_eqn = MathTex(r"U_{eff} = U_{g} + U_{c}").to_corner(UL)
        self.add_fixed_in_frame_mobjects(self.U_effective_eqn)

        self.U_effective_surface = OpenGLSurface(
            uv_func=lambda u, v: self.axes.c2p(u, v, self.U_effective(u, v)),
            u_range=[-1.5, 1.5], v_range=[-1.5, 1.5],
            axes=self.axes,
            color=RED,
            resolution=(64, 64),
            opacity=0.5,
        )
        self.play(
            ReplacementTransform(self.U_centrifugal_surface, self.U_effective_surface),
            ReplacementTransform(self.U_grav_eqn, self.U_effective_eqn),
            FadeOut(self.U_centrifugal_eqn)
        )

    def construct_lagrange_points(self):
        # Draw Lagrange points.
        l1_l2_radius = (self.mu / 3) ** (1 / 3)
        l3_radius = 7 / 12 * self.mu
        # Approximate positions of L1-L3 assuming that m_earth >> m_moon.
        lagrange_points = [
            (self.r_moon[0] - l1_l2_radius, 0, 0),
            (self.r_moon[0] + l1_l2_radius, 0, 0),
            (-1 + l3_radius + self.r_earth[0], 0, 0),
            (self.r_earth[0] + 1 * np.cos(PI / 3), self.r_earth[1] + 1 * np.sin(PI / 3), 0),
            (self.r_earth[0] + 1 * np.cos(PI / 3), self.r_earth[1] - 1 * np.sin(PI / 3), 0),
        ]
        dots = [Dot3D(self.axes.c2p(*point), color=WHITE, radius=0.1) for point in lagrange_points]
        labels = [MathTex(f"L_{i + 1}").next_to(dot, DOWN) for i, dot in enumerate(dots)]
        
        dots = VGroup(*dots)
        labels = VGroup(*labels)
        self.play(Create(dots), Write(labels))
        self.wait(0.1)

        self.l1_point = dots[0] # Save this so that we can zoom in to prepare for next slide.

    def construct(self):
        self.construct_axes()
        self.next_slide()
        self.move_camera(phi=PI / 4, theta=PI / 6, zoom=1, run_time=1.5)

        self.construct_U_grav()
        self.next_slide()

        self.construct_U_centrifugal()
        self.next_slide()

        self.construct_U_effective()
        self.next_slide()

        self.move_camera(phi=0, theta=0)

        contours = []
        for energy in np.arange(-1.6, -1.5, 0.025):
            implicit_fn = self.axes.plot_implicit_curve(lambda x, y: energy - self.U_effective(x, y), color=RED, stroke_width=1.5)
            contours.append(implicit_fn)

        self.play(*[Create(contour) for contour in contours], FadeOut(self.U_effective_surface))
        self.next_slide()

        self.construct_lagrange_points()
        
        self.interactive_embed()

class HaloOrbits(Slide):
    def construct(self):
        print("Loading data")
        search_data = np.load("data/halo_orbits_search.npy")
        orbit_data = np.load("data/halo_orbits.npy")
        l1 = np.load("data/halo_orbits_l1.npy")

        print("Transforming to frame centered on L1")
        search_data -= l1.reshape((1, 1, 2))
        orbit_data -= l1.reshape((1, 1, 2))

        # Get rid of any values under y=0
        np.clip(search_data[:,:,1], 0, None, out=search_data[:,:,1])
        np.clip(orbit_data[:,:,1], 0, None, out=orbit_data[:,:,1])
        print("Done!")

        mu = 1 * 0.0123 / (1 + 0.0123)

        # Apply scaling so that everything fits on the screen
        scale = 20

        # Add L1 point
        l1_dot = Dot(point=(0, 0, 0), color=WHITE)
        l1_label = MathTex("L_1").next_to(l1_dot, DOWN)
        self.add(l1_dot, l1_label)

        # Add y=0 line
        y_line = Line(start=(-8, 0, 0), end=(8, 0, 0), color=WHITE)
        self.add(y_line)

        # Add Moon, Earth points
        moon_r = [1 - mu, 0] - l1
        moon_dot = Dot(point=(*moon_r * scale, 0), color=GRAY)
        moon_label = Text("Moon", font_size=14).next_to(moon_dot, DOWN)
        self.add(moon_dot, moon_label)

        earth_r = [-mu, 0] - l1
        earth_dot = Dot(point=(*earth_r * scale, 0), color=GRAY)
        earth_label = Text("Earth", font_size=14).next_to(earth_dot, DOWN)
        self.add(earth_dot, earth_label)

        # Add ships
        ship_dots = TrueDot(center=ORIGIN)
        ship_dots.clear_points()
        ship_points = np.pad(search_data[0] * scale, ((0, 0), (0, 1)), mode="constant")
        ship_dots.add_points(ship_points)
        ship_dots.set_color(WHITE)
        self.add(ship_dots)

        # Add a trace on all the ships except the first one.
        search_traces = VGroup()
        for i in range(1, search_data.shape[1]):
            trace = TracedPath(lambda i=i: ship_dots.points[i], stroke_color=WHITE)
            search_traces.add(trace)
        self.add(search_traces)
        
        # Add trace on best ship. Simulation is setup so that the best ship is the first one.
        best_trace = TracedPath(lambda: ship_dots.points[0], stroke_color=LIMEGREEN, stroke_width=4)
        self.add(best_trace)
        best_trace.set_stroke(opacity=0)

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

        # Show best ship trace now.
        best_trace.set_stroke(opacity=1)
        self.wait(0.1)
        self.next_slide()
        
        # Reflect the best path across the y=0 line.
        best_trace_center = best_trace.get_center()
        reflected_best_trace = best_trace.copy().flip(RIGHT).shift(DOWN * best_trace_center[1] * 2)
        self.add(reflected_best_trace)
        self.wait(0.1)

        halo_orbit_text = Text("Halo Orbit (Lyapunov L1)", font_size=30).to_edge(DOWN).shift(RIGHT * 4)
        self.play(Write(halo_orbit_text))

        self.next_slide()

        self.remove(search_traces)

        # Now add the other orbits.
        ship_dots.clear_points()
        ship_points = np.pad(orbit_data[0] * scale, ((0, 0), (0, 1)), mode="constant")
        ship_dots.add_points(ship_points)
        ship_dots.set_color(WHITE)
        ship_dots.remove_updater(update_ships)
        time_step.set_value(0)
        def update_orbits(mob: TrueDot):
            time_index = int((len(search_data) - 1) * time_step.get_value())
            ship_points = np.pad(orbit_data[time_index] * scale, ((0, 0), (0, 1)), mode="constant")

            mob.clear_points()
            mob.add_points(ship_points)
            mob.set_color(WHITE)
        ship_dots.add_updater(update_orbits)

        orbit_traces = []
        for i in range(orbit_data.shape[1]):
            trace = TracedPath(lambda i=i: ship_dots.points[i], stroke_color=LIMEGREEN, stroke_width=4)
            orbit_traces.append(trace)
        orbit_traces = VGroup(*orbit_traces)
        self.add(orbit_traces)

        self.play(time_step.animate.set_value(1), run_time=4, rate_func=smooth)
        # Reflect all the traces across the y=0 line.
        orbit_traces_center = orbit_traces.get_center()
        reflected_orbit_traces = orbit_traces.copy().flip(RIGHT).shift(DOWN * orbit_traces_center[1] * 2)
        self.add(reflected_orbit_traces)
        self.wait(0.1)

        self.interactive_embed()

class EarthMoonManifolds(Slide):
    def construct(self):
        # === Earth-Moon manifolds ===
        print("Loading data")
        orbit_data = np.load("data/manifolds_earth_moon_orbit.npy")
        unstable_data = np.load("data/manifolds_earth_moon_unstable.npy")
        stable_data = np.load("data/manifolds_earth_moon_stable.npy")
        l1_earth_moon = np.load("data/manifolds_earth_moon_l1.npy")

        mu = 1 * 0.0123 / (1 + 0.0123)

        # Apply scaling so that everything fits on the screen
        scale = 6

        # Add L1 point
        l1_dot = Dot(point=(*l1_earth_moon * scale, 0), color=WHITE, radius=0.04)
        l1_label = MathTex("L_1", font_size=14).next_to(l1_dot, DOWN)
        self.add(l1_dot, l1_label)

        # Add Moon, Earth points
        moon_r = np.array([1 - mu, 0])
        moon_dot = Dot(point=(*moon_r * scale, 0), color=GRAY)
        moon_label = Text("Moon", font_size=14).next_to(moon_dot, RIGHT)
        self.add(moon_dot, moon_label)

        earth_r = np.array([-mu, 0])
        earth_dot = Dot(point=(*earth_r * scale, 0), color=GRAY)
        earth_label = Text("Earth", font_size=14).next_to(earth_dot, LEFT)
        self.add(earth_dot, earth_label)

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

        self.interactive_embed()

class PotentialHill(Slide):
    def construct(self):
        group = VGroup()

        physical_space = Axes(
            x_range=[0, 10],
            y_range=[-1.5, 1.5],
            x_length=6,
            y_length=5
        )
        phase_space = Axes(
            x_range=[0, 10],
            y_range=[-3, 3],
            x_length=6,
            y_length=5
        )
        group.add(physical_space, phase_space).arrange(RIGHT)
        physical_space_title = Text("Physical space", font_size=26).next_to(physical_space, DOWN)
        phase_space_title = Text("Phase space", font_size=26).next_to(phase_space, DOWN)

        physical_labels = physical_space.get_axis_labels(Tex("x"), Tex("U"))
        phase_space_labels = phase_space.get_axis_labels(Tex("x"), Tex("v"))
        physical_labels[0].shift(LEFT)
        phase_space_labels[0].shift(LEFT)

        x0 = 5
        sigma = 1
        def U(x):
            return np.exp(-(((x - x0) / sigma) ** 2) / 2)
        def dv(x):
            return -(x - x0) / (sigma ** 2) * U(x)
        u_curve = physical_space.plot(U, color=RED)
        area = physical_space.get_area(u_curve, (0, 10), color=RED, fill_opacity=0.5)

        self.play(Create(physical_space), Create(physical_labels), Write(physical_space_title))
        self.play(Create(u_curve), Create(area))

        self.play(Create(phase_space), Create(phase_space_labels), Write(phase_space_title))
        self.wait(0.1)
        self.next_slide()

        phase_traces = VGroup()
        # Shoot some rockets
        def shoot_rocket(x0: float, v0: float, t: ValueTracker, trace_color = LIMEGREEN, add_to_vgroup: bool = True) -> Dot:
            """
            Takes initial position and total energy and launches a rocket.
            Returns the phase space rocket dot.
            """
            physical_rocket = Dot(point=physical_space.c2p(x0, U(x0)))
            phase_space_rocket = Dot(point=phase_space.c2p(x0, v0))
            self.add(physical_rocket, phase_space_rocket)

            phase_trace = TracedPath(phase_space_rocket.get_center, stroke_color=trace_color, stroke_width=4)
            self.add(phase_trace)
            if add_to_vgroup:
                phase_traces.add(phase_trace)

            def physical_rocket_update(mob):
                x = phase_space.p2c(phase_space_rocket.get_center())[0]
                mob.move_to(physical_space.c2p(x, U(x)))

            prev_t = t.get_value()
            def phase_space_update(mob):
                nonlocal prev_t
                dt = t.get_value() - prev_t
                prev_t = t.get_value()

                [x, v] = phase_space.p2c(mob.get_center())
                a = -dv(x)
                x += v * dt
                v += a * dt

                # Check if the rocket has hit the edge
                if x < -0.01:
                    self.remove(physical_rocket)
                    mob.move_to(phase_space.c2p(0, v))
                    mob.clear_updaters()
                elif x > 10.01:
                    self.remove(physical_rocket)
                    mob.move_to(phase_space.c2p(10, v))
                    mob.clear_updaters()
                else:
                    mob.move_to(phase_space.c2p(x, v))
                
            physical_rocket.add_updater(physical_rocket_update)
            phase_space_rocket.add_updater(phase_space_update)
            return phase_space_rocket

        # First from the left.
        t = ValueTracker(0)
        rockets = []
        H_values = [0.1, 0.25, 0.55, 0.85, 1.15, 1.45, 1.75, 2.05]
        for H in H_values:
            v0 = np.sqrt(2 * H - 2 * U(0))
            rockets.append(shoot_rocket(0, v0, t))
        self.play(t.animate.set_value(15), run_time=6, rate_func=linear)
        self.play(*[FadeOut(rocket, run_time=0.2) for rocket in rockets])

        # Then from the right.
        t.set_value(0)
        rockets = []
        for H in H_values:
            v0 = -np.sqrt(2 * H - 2 * U(10))
            rockets.append(shoot_rocket(10, v0, t))
        self.play(t.animate.set_value(15), run_time=6, rate_func=linear)
        self.play(*[FadeOut(rocket, run_time=0.2) for rocket in rockets])

        self.next_slide()

        # Equilibrium point
        equilibrium = Dot(point=phase_space.c2p(x0, 0), color=WHITE)
        label = Text("Equilibrium", font_size=16).next_to(equilibrium, DOWN)

        self.add(equilibrium)
        self.play(Write(label))

        # Stable and unstable manifolds
        # ----
        # E = 0 at x = x0 = 5. So from conservation of momentum, H = 1 = p^2 / 2 + V(x)
        # which gives us p = sqrt(2 - 2 * V(x))
        # Stable manifold is positive if x < x0 and negative if x > x0.
        # Unstable manifold has opposite sign.
        # ----
        def stable_f(x):
            if x < x0:
                return np.sqrt(2 - 2 * U(x))
            else:
                return -np.sqrt(2 - 2 * U(x))
        stable = phase_space.plot(stable_f, color=BLUE)
        unstable = phase_space.plot(lambda x: -stable_f(x), color=RED)

        legend = VGroup(
            Text("Stable", font_size=22, color=BLUE),
            Text("Unstable", font_size=22, color=RED),
        )
        legend.arrange(RIGHT, buff=1).next_to(phase_space_title, UP)

        opacity = ValueTracker(1)
        self.add_updater(lambda dt: phase_traces.set_stroke(opacity=opacity.get_value())) # HACK: animation seems broken for TracedPath

        self.play(Create(stable), Create(unstable), Write(legend), opacity.animate.set_value(0.3))
        self.next_slide()

        # Shoot two rockets just above and below stable manifold.
        t.set_value(0)
        rockets = []
        for H in [0.85, 1.15]:
            v0 = np.sqrt(2 * H - 2 * U(0))
            rockets.append(shoot_rocket(0, v0, t, trace_color=WHITE, add_to_vgroup=False))
        self.play(t.animate.set_value(10), run_time=4, rate_func=linear)
        self.play(*[FadeOut(rocket, run_time=0.2) for rocket in rockets])

        self.interactive_embed()

class Manifolds3Body(Slide):
    scale = 400

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
        scale = self.scale

        # Add L1 point
        l1_dot = Dot(point=(*l1_sun_earth * scale, 0), color=WHITE, radius=0.04)
        l1_label = always_redraw(lambda: MathTex("L_1", font_size=14).next_to(l1_dot, DOWN))
        self.add(l1_dot, l1_label)

        # Center on Earth.
        earth_r = np.array([0, 0])
        earth_dot = Dot(point=(*earth_r * scale, 0), color=GRAY)
        earth_label = Text("Earth", font_size=14).next_to(earth_dot, DOWN)
        self.add(earth_dot, earth_label)

        # Add arrow pointing to the Sun.
        sun_arrow = Vector([-1, 0]).to_edge(LEFT)
        sun_label = Text("Sun", font_size=14).next_to(sun_arrow, DOWN)
        self.add(sun_arrow, sun_label)

        # Add all the unstable manifold ships as parametric functions
        time_steps = unstable_data.shape[0]
        assert stable_data.shape[0] == time_steps, "stable data and unstable data should have the same number of time steps"
        
        num_ships = unstable_data.shape[1]
        assert stable_data.shape[1] == num_ships, "stable data and unstable data should have the same number of ships"

        print("Creating traces of manifolds")
        unstable_traces = VGroup()
        stable_traces = VGroup()
        for i in range(num_ships):
            unstable = ParametricFunction(
                function=lambda t, i=i: (*unstable_data[int(t * (time_steps - 1)), i] * scale, 0), # type: ignore
                t_range=[0, 1],
                color=RED,
            )
            unstable_traces.add(unstable)
            stable = ParametricFunction(
                function=lambda t, i=i: (*stable_data[int(t * (time_steps - 1)), i] * scale, 0), # type: ignore
                t_range=[0, 1],
                color=BLUE,
            )
            stable_traces.add(stable)
        print("Done!")
        
        orbit_time_steps = orbit_data.shape[0]
        orbit_trace = ParametricFunction(
            function=lambda t: (*orbit_data[int(t * (orbit_time_steps - 1)), 0] * scale, 0), # type: ignore
            t_range=[0, 1],
            color=LIMEGREEN,
        ).set_stroke(width=2)
        self.add(orbit_trace) # Start with orbit trace on the slide.

        unstable_traces.set_stroke(width=2, opacity=0.7)
        stable_traces.set_stroke(width=2, opacity=0.7)

        legend = VGroup(
            Text("Unstable", font_size=22, color=RED),
            Text("Stable", font_size=22, color=BLUE),
        )
        legend.arrange(DOWN, buff=1).to_edge(RIGHT)

        self.wait(0.1)
        self.next_slide()

        self.play(FadeIn(unstable_traces), FadeIn(stable_traces), Write(legend))

        self.next_slide(auto_next=True) # Next slide is spinning Earth-Moon frame.

        # Create scaled versions of all the manifolds and transform to these to produce the effect of zooming in.
        scaled = lambda mob: mob.copy().scale(4).move_to(mob.get_center() * 4)
        stable_traces_scaled = scaled(stable_traces)
        unstable_traces_scaled = scaled(unstable_traces)
        orbit_trace_scaled = scaled(orbit_trace)

        self.play(
            l1_dot.animate.move_to(l1_dot.get_center() * 4),
            Transform(unstable_traces, unstable_traces_scaled),
            Transform(stable_traces, stable_traces_scaled),
            Transform(orbit_trace, orbit_trace_scaled),
            run_time=1.5,
        )
        self.play(
            FadeOut(unstable_traces),
            FadeOut(stable_traces),
            FadeOut(orbit_trace),
            run_time=0.5
        )
        self.remove(l1_dot, l1_label)

        self.construct_earth_moon_manifolds()

    def construct_earth_moon_manifolds(self):
        # Add in the Earth-Moon manifolds in the rotating frame.
        # === Earth-Moon manifolds ===
        print("Loading data")
        orbit_data = np.load("data/manifolds_earth_moon_orbit.npy")
        unstable_data = np.load("data/manifolds_earth_moon_unstable.npy")
        stable_data = np.load("data/manifolds_earth_moon_stable.npy")

        mu = 1 * 0.0123 / (1 + 0.0123)

        # Apply scaling so that everything fits on the screen
        sun_earth_scale = 1/378.6
        scale = self.scale * sun_earth_scale * 4 # 4 is from scaling of previous manifolds

        earth_r = np.array([-mu, 0])
        # Transform everything to Earth frame
        orbit_data -= earth_r.reshape((1, 1, 2))
        unstable_data -= earth_r.reshape((1, 1, 2))
        stable_data -= earth_r.reshape((1, 1, 2))

        moon_r = np.array([1, 0])
        moon_dot = Dot(point=(*moon_r * scale, 0), color=GRAY)
        moon_label = always_redraw(lambda: Text("Moon", font_size=14).next_to(moon_dot, DOWN))

        # Add all the unstable manifold ships as parametric functions
        time_steps = unstable_data.shape[0]
        assert stable_data.shape[0] == time_steps, "stable data and unstable data should have the same number of time steps"
        
        num_ships = unstable_data.shape[1]
        assert stable_data.shape[1] == num_ships, "stable data and unstable data should have the same number of ships"

        print("Creating traces of manifolds")
        unstable_traces = VGroup()
        stable_traces = VGroup()
        for i in range(num_ships):
            unstable = ParametricFunction(
                function=lambda t, i=i: (*unstable_data[int(t * (time_steps - 1)), i] * scale, 0), # type: ignore
                t_range=[0, 1],
                color=RED,
            )
            unstable_traces.add(unstable)
            stable = ParametricFunction(
                function=lambda t, i=i: (*stable_data[int(t * (time_steps - 1)), i] * scale, 0), # type: ignore
                t_range=[0, 1],
                color=BLUE,
            )
            stable_traces.add(stable)
        print("Done!")
        
        orbit_time_steps = orbit_data.shape[0]
        orbit_trace = ParametricFunction(
            function=lambda t: (*orbit_data[int(t * (orbit_time_steps - 1)), 0] * scale, 0), # type: ignore
            t_range=[0, 1],
            color=LIMEGREEN,
        ).set_stroke(width=2)

        unstable_traces.set_stroke(width=1, opacity=0.5)
        stable_traces.set_stroke(width=1, opacity=0.5)

        # Whole frame is constantly rotating.
        rate = 1 / 2
        always_rotate(unstable_traces, rate=rate, about_point=ORIGIN)
        always_rotate(stable_traces, rate=rate, about_point=ORIGIN)
        always_rotate(orbit_trace, rate=rate, about_point=ORIGIN)
        always_rotate(moon_dot, rate=rate, about_point=ORIGIN)

        self.add(moon_dot, moon_label)
        self.play(FadeIn(unstable_traces), FadeIn(stable_traces), FadeIn(orbit_trace))
        
        self.next_slide(loop=True)
        self.wait(4 * PI) # Full cycle

        self.interactive_embed()

class BallisticCapture(Slide):
    def construct(self):
        image = OpenGLImageMobject("ballistic_capture.png", width=16, height=9)
        self.add(image)
        self.wait(0.1)

class References(Slide):
    def construct(self):
        vg = VGroup()
        title = Text("References", font_size=24)
        references = Text('\n'.join([
            "[1] braintruffle. (2024, January 25). Master the complexity of spaceflight. YouTube. https://www.youtube.com/watch?v=dhYqflvJMXc",
            "[2] Howell, K. C., Beckman, M., Patterson, C., & Folta, D. (2006). Representations of invariant manifolds for applications in three-body systems.\n\tThe Journal of the Astronautical Sciences, 54(1), 69–93. https://doi.org/10.1007/bf03256477",
            "[3] Topputo, F. (2016). Fast numerical approximation of invariant manifolds in the circular restricted three-body problem. \n\tCommunications in Nonlinear Science and Numerical Simulation, 32, 89–98. https://doi.org/10.1016/j.cnsns.2015.08.004",
            "[4] Lo, Martin. (2002). The InterPlanetary Superhighway and the Origins Program. 7. 7-3543 . 10.1109/AERO.2002.1035332.",
        ]), line_spacing=1, font_size=14)
        vg.add(title, references)
        vg.arrange(DOWN).align_on_border(LEFT)
        self.play(Write(vg), run_time=1.5)

        source_code = Tex(r"Source code: \textit{github.com/lukechu10/interplanetary-transport-network}", font_size=18).to_edge(DL)
        self.play(Write(source_code), run_time=1)

