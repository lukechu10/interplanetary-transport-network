# Budget-friendly space travel

> Traveling in space
> Luke Chu
> 6 March 2024

You are stuck in a spaceship orbiting around the moon and you wish to come back home. But fuel is running low and you realise that you do not have enough to make a transfer burn back to Earth. What do you do? Perhaps making a transfer burn is not the only way to get back.

To find an answer, we must be able to predict the future. Given an initial condition, where will we end up?

To predict the future, we will need many tools. We will start by building a tracer and later on, we will use many tools such as phase space, Lagrange points, stable and unstable manifolds, so that we can eventually find a way to get back home, and to get to any other part of the solar system.

## 1. Building a tracer

### 1.a.

> Building a tracer
> \_Scene with four static masses. Animate changing trajectories while varying initial conditions.

But first, let's build a tracer. What this does is simple. Simulate the tracjectories of a spacecraft under influence of some other masses.

However, to find the right path, we must simulate millions and millions of ships to see if anyone gets to our final destination. But simulating millions of bodies all at the same time is clearly intractable. It would take forever for the computation to finish.

### 1.b. The reduced n-body problem

Instead, we use an approximation, and an extremely good one too. We assume that the planets are not affected by the spaceships since they are so much more massive. This allows us to do the simulation in two phases. First phase, we simulate the motion of all the planets and save this somewhere. We can then playback this data while simulating all the spaceships.

Whereas before, we were trying to solve an (n + m) body problem where n is the number of planets and m the number of spaceships, we are now solving an n-body problem and m number times (n + 1)-body problems. Much better!

<!-- TODO: reword above paragraph -->

### 1.c. Simulation Resolution - Building a probability tracer

> \_Slide with an animation of shooting a packet swinging-by a planet. Show that out going packet no longer has an uniform distribution.

So it sounds pretty simple right? Fire off a bunch of spaceships and see which one gets to our destination. However, this approach comes with a problem. Resolution. TODO

## 2. Phase space

### 2.a. Phase space diagram with clouds for probability

### 2.b. Tracing boundaries

## 3. Earth-Moon system - 3 body problem

### 3.a. Simulating trajectories from Earth to Moon. Hohhman transfer. Ballistic capture.

### 3.b. Inertial and non-inertial frames.

### 3.c. Co-rotating frame. Fictitious forces. Effective potential.

### 3.d. Lagrange points. In particular, L1 and L2.

## 4. Manifolds

### 4.a. Stable and unstable manifolds in a simple 1D bump potential system.

### 4.b. Manifolds for Lagrange points.

### 4.c. Hopping manifolds from Earth to Moon.

## 5. Interplanetary Transport Network

### 5.a. Hopping manifolds between planets.

### 5.b. The interplanetary transport network.

## Conclusion
