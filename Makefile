# Build slide to a video with manim with given quality
build-video:
	manim -q$(q) slides.py $(slide) --renderer opengl --write_to_movie

build-video-preview:
	manim -q$(q) slides.py $(slide) --renderer opengl --preview

# Build slide to an image with given quality
build-image:
	manim -q$(q) slides.py $(slide) -s

build-slides-html:
	manim-slides convert --use-template template.html \
		TitleSlide \
		BuildingATracer \
		SinglePlanet \
		MultiPlanet \
		ReducedNBodyProblem \
		LeoToMoon \
		EffectivePotential \
		PotentialHill \
		LagrangePoints \
		Manifolds3Body \
		InterplanetaryTransportNetwork \
		References \
		dist/index.html
