import numpy as np
from manim import *
from manim_slides.slide import Slide

class EarthMoonPositions(Slide):
    def construct(self):
        data = np.load("../data/earth_moon_positions.npy")
        moon_initial = data[0][1]
        scale = np.linalg.norm(moon_initial) / 4

        axes = Axes([-1, 1], [-1, 1])
        self.add(axes)

        earth = Dot(color=BLUE).set_x(data[0][0][0] / scale).set_y(data[0][0][1] / scale)
        moon = Dot(color=GRAY).set_x(data[0][1][0] / scale).set_y(data[0][1][1] / scale)

        self.play(Create(earth), Create(moon))
        
        earth_trace = TracedPath(earth.get_center, stroke_color=BLUE)
        moon_trace = TracedPath(moon.get_center, stroke_color=GRAY)
        self.add(earth_trace, moon_trace)

        self.next_slide()

        time_step = ValueTracker(0)
        earth.add_updater(lambda m: m.move_to((data[int((len(data) - 1) * time_step.get_value())][0] / scale)))
        moon.add_updater(lambda m: m.move_to((data[int((len(data) - 1) * time_step.get_value())][1] / scale)))

        self.play(time_step.animate.set_value(1), run_time=10, rate_func=linear)
