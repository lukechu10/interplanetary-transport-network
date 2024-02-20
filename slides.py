import numpy as np
from manim import *
from manim_slides.slide import Slide

# Title
class Part0(Slide):
    def construct(self):
        title = Text("Budget-friendly space travel")
        author = Text("Luke Chu").next_to(title, DOWN)
        author.font_size = 18

        date = Text("6 March 2024").to_corner(DR)
        date.font_size = 12

        self.add(title, author, date)
        self.wait()

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
