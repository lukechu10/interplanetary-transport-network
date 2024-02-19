import numpy as np
from manim import *
from manim_slides.slide import Slide

class EarthMoonPositions(Slide):
    def construct(self):
        bodies_data = np.load("../data/bodies.npy")
        ships_data = np.load("../data/ships.npy")
        bodies_count = len(bodies_data[0])
        ships_count = len(ships_data[0])

        # Apply scaling so that everything fits on the screen
        moon_earth_radius = 384400000
        scale = moon_earth_radius

        colors = [BLUE, GRAY, RED, YELLOW, PURPLE]
        dots = []
        for i in range(bodies_count):
            color = colors[i % len(colors)]
            dots.append(Dot(color=color).set_x(bodies_data[0][i][0] / scale).set_y(bodies_data[0][i][1] / scale))

        traces = []
        for i in range(bodies_count):
            color = colors[i % len(colors)]
            traces.append(TracedPath(dots[i].get_center, stroke_color=color))

        self.play(*list(map(lambda x: Create(x), dots)))
        self.add(*traces)

        self.next_slide()

        # Add ships
        ship_dots = []
        for i in range(ships_count):
            ship_dots.append(Dot(color=GREEN).set_x(ships_data[0][i][0] / scale).set_y(ships_data[0][i][1] / scale))
        ship_traces = []
        for i in range(bodies_count):
            ship_traces.append(TracedPath(ship_dots[i].get_center, stroke_color=GREEN))
        self.play(*list(map(lambda x: Create(x), ship_dots)))
        self.add(*ship_traces)

        self.next_slide()

        time_step = ValueTracker(0)
        def update(data, n):
            def f(mob):
                coords = data[int((len(data) - 1) * time_step.get_value())][n] / scale
                mob.move_to((coords[0], coords[1], 0))
            return f
        for i in range(bodies_count):
            dots[i].add_updater(update(bodies_data, i))
            ship_dots[i].add_updater(update(ships_data, i))


        self.play(time_step.animate.set_value(1), run_time=10, rate_func=linear)
