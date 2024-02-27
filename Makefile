# Build slide to a video with manim with given quality
build-video:
	manim -q$(q) slides.py $(slide) --renderer opengl --write_to_movie

build-video-preview:
	manim -q$(q) slides.py $(slide) --renderer opengl --preview

# Build slide to an image with given quality
build-image:
	manim -q$(q) slides.py $(slide) -s

build-slides-html:
	manim-slides convert \
		TitleSlide \
		BuildingATracer \
		ReducedNBodyProblem \
		EffectivePotential \
		PartN \
		References \
		dist/index.html
