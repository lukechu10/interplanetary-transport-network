# Budget-friendly space travel

<!-- TODO: figure out a better title -->

> Traveling in space
> Luke Chu
> 6 March 2024

You are currently in a spaceship orbiting around Moon. How do you get back home? After all, there are an infinite number of different trajectories you could take, each one requiring more or less fuel and more or less time. How do we know which one to pick?

The answer should be pretty easy right? First, fire prograde relative to the moon to reduce your speed relative to the Earth. And then, as you approach Earth, fire retrograde again to get into Low Earth Orbit. Finally, land! This is the Hoffmann transfer which is supposed to be the most efficient transfer orbit.

But your fuel is running precariously low and you realise that you won't actually have enough fuel to perform the final burn to get into Low Earth Orbit. What can you do insted?

To figure this out, we will need to be able to predict the future. We will start by building a tracer and use many tools such as phase space, Lagrange points, stable and unsatble manifolds to find out the most efficient way of getting back home.

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
