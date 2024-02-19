import numpy as np
from manim import *
from manim_slides.slide import Slide

class EarthMoonPositions(Slide):
    def construct(self):
        data = np.load("../data/earth_moon_positions.npy")
        bodies_count = len(data[0])
        print(bodies_count)

        # Apply scaling so that everything fits on the screen
        moon_earth_radius = 384400000
        scale = moon_earth_radius / 2

        axes = Axes(x_range=[-1, 1, 1], y_range=[-1, 1, 1])
        self.add(axes)

        colors = [BLUE, GRAY, RED, YELLOW, PURPLE]
        dots = []
        for i in range(bodies_count):
            color = colors[i % len(colors)]
            dots.append(Dot(color=color).set_x(data[0][i][0] / scale).set_y(data[0][i][1] / scale))

        self.play(*list(map(lambda x: Create(x), dots)))

        traces = []
        for i in range(bodies_count):
            color = colors[i % len(colors)]
            traces.append(TracedPath(dots[i].get_center, stroke_color=color))
        
        self.add(*traces)

        self.next_slide()

        time_step = ValueTracker(0)
        def update(n):
            return lambda mob: mob.move_to(data[int((len(data) - 1) * time_step.get_value())][n] / scale)
        for i in range(bodies_count):
            dots[i].add_updater(update(i))

        self.play(time_step.animate.set_value(1), run_time=10, rate_func=linear)
