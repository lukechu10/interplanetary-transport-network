from cloup import group
from manim.utils.color.XKCD import LIMEGREEN
import numpy as np

from manim import *
from manim.opengl import *
from manim_slides.slide import Slide, ThreeDSlide

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
        self.next_slide()
        self.play(FadeOut(title), FadeOut(author), FadeOut(date))
        self.wait()

class ReducedNBodyProblem(Slide):
    def construct(self):
        table = Table([
            ["Full n-body problem", "Reduced n-body problem"],
            ["2 planets + 10 ships", "2 planets + 10 ships"],
            ["(12 - 1)! forces", "2 forces + 10 * 2 forces"],
            ["39916800 forces", "22 forces"],
        ]).scale(0.5)
        self.play(Write(table))
        todo = Text("TODO: add animation").next_to(table, DOWN)
        self.play(Write(todo))
        self.wait()

class BuildingATracer(Slide):
    def construct(self):
        title = Text("Building a tracer")
        todo = Text("TODO: add content").next_to(title, DOWN)
        self.play(Write(title), Write(todo))
        self.wait()

class LeoToMoon(Slide):
    def construct(self):
        bodies_data = np.load("data/part1b_bodies.npy")
        ship_data = np.load("data/part1b_ships.npy")
        bodies_count = len(bodies_data[0])

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
        self.U_grav_eqn = MathTex(r"U_{g} = -\frac{G m_E}{r_E} - \frac{G m_M}{r_M}").to_corner(UL)
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
        self.U_centrifugal_eqn = MathTex(r"U_{c} = -\frac{1}{2} \omega^2 r").next_to(self.U_grav_eqn, RIGHT).shift(RIGHT)
        self.add_fixed_in_frame_mobjects(self.U_centrifugal_eqn)

        self.U_centrifugal_surface = OpenGLSurface(
            uv_func=lambda u, v: self.axes.c2p(u, v, self.U_centrifugal(u, v)),
            u_range=[-1.5, 1.5], v_range=[-1.5, 1.5],
            axes=self.axes,
            color=PURPLE,
            resolution=(64, 64),
            opacity=0.5,
        )
        self.play(Uncreate(self.U_grav_surface), Create(self.U_centrifugal_surface), Write(self.U_centrifugal_eqn))
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
        physical_space_text = Text("Physical space").next_to(physical_space, DOWN)
        phase_space_text = Text("Phase space").next_to(phase_space, DOWN)

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

        self.play(Create(physical_space), Create(physical_labels), Write(physical_space_text))
        self.next_slide()

        self.play(Create(u_curve), Create(area))
        self.next_slide()

        self.play(Create(phase_space), Create(phase_space_labels), Write(phase_space_text))

        # Shoot some rockets

        def shoot_rocket(x0: float, v0: float, t: ValueTracker) -> Dot:
            """
            Takes initial position and total energy and launches a rocket.
            Returns the phase space rocket dot.
            """
            physical_rocket = Dot(point=physical_space.c2p(x0, U(x0)))
            phase_space_rocket = Dot(point=phase_space.c2p(x0, v0))
            self.add(physical_rocket, phase_space_rocket)

            phase_trace = TracedPath(phase_space_rocket.get_center, stroke_color=LIMEGREEN, stroke_width=4)
            self.add(phase_trace)

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
        for H in np.arange(0.25, 2, 0.3):
            v0 = np.sqrt(2 * H - 2 * U(0))
            rockets.append(shoot_rocket(0, v0, t))
        self.play(t.animate.set_value(21), run_time=3, rate_func=linear)
        self.play(*[FadeOut(rocket, run_time=0.2) for rocket in rockets])

        # Then from the right.
        rockets = []
        for H in np.arange(0.25, 2, 0.3):
            v0 = -np.sqrt(2 * H - 2 * U(10))
            rockets.append(shoot_rocket(10, v0, t))
        self.play(t.animate.set_value(42), run_time=3, rate_func=linear)
        self.play(*[FadeOut(rocket, run_time=0.2) for rocket in rockets])

        self.next_slide()

        # Equilibrium point
        equilibrium = Dot(point=phase_space.c2p(x0, 0), color=GREEN)
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
        unstable = phase_space.plot(lambda x: -stable_f(x), color=YELLOW)

        self.play(Create(stable), Create(unstable))

        self.interactive_embed()

class References(Slide):
    def construct(self):
        vg = VGroup()
        title = Text("References").scale(0.7)
        references = Text('\n'.join([
            "braintruffle. (2024, January 25). Master the complexity of spaceflight. YouTube. https://www.youtube.com/watch?v=dhYqflvJMXc",
            "Lo, Martin. (2002). The InterPlanetary Superhighway and the Origins Program. 7. 7-3543 . 10.1109/AERO.2002.1035332.",
        ]), line_spacing=1).scale(0.3)
        vg.add(title, references)
        vg.arrange(DOWN).align_on_border(LEFT)
        self.play(Write(vg))
