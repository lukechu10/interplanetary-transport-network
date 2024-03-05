# Build slide to a video with manim with given quality
build-video:
	manim -q$(q) slides.py $(slide) --renderer opengl --write_to_movie

build-video-preview:
	manim -q$(q) slides.py $(slide) --renderer opengl --preview

# Build slide to an image with given quality
build-image:
	manim -q$(q) slides.py $(slide) -s

run-all-simulations:
	cargo build --release
	./target/release/simulation single_planet
	./target/release/simulation multi_planet
	./target/release/simulation leo_to_moon
	./target/release/simulation halo_orbits_earth_moon
	./target/release/simulation halo_orbits_sun_earth
	./target/release/simulation manifolds_earth_moon

build-video-all:
	manim -q$(q) slides.py TitleSlide --renderer opengl --write_to_movie
	manim -q$(q) slides.py RestrictedNBodyProblem --renderer opengl --write_to_movie
	manim -q$(q) slides.py SinglePlanet --renderer opengl --write_to_movie
	manim -q$(q) slides.py MultiPlanet --renderer opengl --write_to_movie
	manim -q$(q) slides.py LeoToMoon --renderer opengl --write_to_movie
	manim -q$(q) slides.py EffectivePotential --renderer opengl --write_to_movie
	manim -q$(q) slides.py HaloOrbits --renderer opengl --write_to_movie
	manim -q$(q) slides.py EarthMoonManifolds --renderer opengl --write_to_movie
	manim -q$(q) slides.py PotentialHill --renderer opengl --write_to_movie
	manim -q$(q) slides.py Manifolds3Body --renderer opengl --write_to_movie
	manim -q$(q) slides.py BallisticCapture --renderer opengl --write_to_movie
	manim -q$(q) slides.py References --renderer opengl --write_to_movie

build-slides-html:
	rm -r docs/index_assets/
	manim-slides convert --use-template template.html \
		TitleSlide \
		RestrictedNBodyProblem \
		SinglePlanet \
		MultiPlanet \
		LeoToMoon \
		EffectivePotential \
		HaloOrbits \
		EarthMoonManifolds \
		PotentialHill \
		Manifolds3Body \
		BallisticCapture \
		References \
		docs/index.html
