# Low-energy transfers in space

See the original presentation [here](https://lukechu10.github.io/interplanetary-transport-network/).

I have since re-adapted this material into an [interactive blog post](https://lukechu10.github.io/posts/low-energy-transfers) on my website.

## Build instructions

**Dependencies**:

- Up to date installation of [Rust](https://www.rust-lang.org/).
- Up to date installation of Python.
- [Manim Community Edition](https://github.com/ManimCommunity/manim) v0.18 and [manim-slides](https://github.com/jeertmans/manim-slides) v5.1
- Make

Run all the simulations first by running `make run-all-simulations`.
Then render all the videos by running `make build-video-all q=h`. (Beware, this will take some time!)

This will generate videos into a `media/` folder. To build the slides, run `make build-slides-html` which will generate the final slides into the `docs/` folder.

## Blog animations

The animations for the blog are in the `slides_blog.py` file. You can build them by using the analogeous `Makefile-blog` file by passing it via the `-f` flag to `make`.
