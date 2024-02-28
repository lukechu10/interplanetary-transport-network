# Budget-friendly space travel

<!-- TODO: figure out a better title -->

> Traveling in space
> Luke Chu
> 6 March 2024

You are currently in a spaceship orbiting around Moon. How do you get back home? After all, there are an infinite number of different trajectories you could take, each one requiring more or less fuel and more or less time. How do we know which one to pick?

The answer should be pretty easy right? First, fire prograde relative to the moon to reduce your speed relative to the Earth. And then, as you approach Earth, fire retrograde again to get into Low Earth Orbit. Finally, land! This is the Hohmann transfer which is supposed to be the most efficient transfer orbit.

But your fuel is running precariously low and you realise that you won't actually have enough fuel to perform the final burn to get into Low Earth Orbit. What can you do instead?

To figure this out, we will need to be able to predict the future. We will start by building a tracer and use many tools such as phase space, Lagrange points, stable and unstable manifolds to find out the most efficient way of getting back home.

## 1. Building a tracer

<!-- TODO: Decide if this section is really necessary -->

### 1.a.

> Building a tracer
> \_Scene with four static masses. Animate changing trajectories while varying initial conditions.

But first, let's build a tracer. What this does is simple. Simulate the trajectories of a spacecraft under influence of some other masses.

However, to find the right path, we must simulate millions and millions of ships to see if anyone gets to our final destination. But simulating millions of bodies all at the same time is clearly intractable. It would take forever for the computation to finish.

### 1.b. The reduced n-body problem

Instead, we use an approximation, and an extremely good one too. We assume that the planets are not affected by the spaceships since they are so much more massive. This allows us to do the simulation in two phases. First phase, we simulate the motion of all the planets and save this somewhere. We can then playback this data while simulating all the spaceships.

Whereas before, we were trying to solve an (n + m) body problem where n is the number of planets and m the number of spaceships, we are now solving an n-body problem and m number times (n + 1)-body problems. Much better!

## 2. Phase space

<!-- TODO: This section goes with the same comment as the previous section -->

### 2.a. Phase space diagram with clouds for probability

### 2.b. Tracing boundaries

## 3. Earth-Moon system - 3 body problem

### 3.a. Simulating trajectories from Earth to Moon. Hohmann transfer. Ballistic capture.

Let's get from Low Earth Orbit to the Moon. How efficient is our Hohmann transfer? We'll, we need to do at least two burns, one to get away from Earth, another to slow down once we get to the Moon. Can we do better?

Here, I am shooting out many spaceships starting from Low Earth Orbit with varying initial velocities. Every time one of these lines intersect with Moon, we get a possible route. As you can see, there are many different possible routes to get to the Moon. But focus in particular on these ones. These trajectories first move away from Moon, but then as they are pulled back by the Earth, they get captured ballistically by Moon. There is no need for a second burn to slow down!

How can we explain this?

## 4. Manifolds

### 4.a. Stable and unstable manifolds in a simple 1D bump potential system.

To answer this question, let us return back to our phase space diagrams. Imagine a simple system with a bump potential. As we fire some spaceships into this potential, we can trace out their paths in phase space.

In particular, we can see that there is a specific point in phase space which is impossible to get to unless we start there. That is, if we stay motionless on the top of the hill. In phase space, this is an equilibrium point. Any object near this point will tend to fall off this point. We can therefore draw unstable manifolds through this point, describing the paths that lead away from this point. Similarly, we can draw stable manifolds that lead toward this point. These are points in phase space that end up at the equilibrium point, although it would take infinite time for it to do so.

### 4.b. Manifolds for Lagrange points.

What does this have to do with our problem of getting to the Moon? Well, we've seen that in a 3 body problem, there are certain points known as Lagrange points which are points of equilibrium. In fact, we can even have halo orbits around these points. So this means we can have stable and unstable manifolds that lead to these halo orbits. This results in stable and unstable manifolds that look like giant tubes floating in space.

### 4.c. Hopping manifolds from Earth to Moon.

For the Sun-Earth 3 body problem, we have these stable and unstable manifolds. Our ballistic trajectory starts out by following the unstable manifold tube out towards the Sun. However, because we have timed it just right, the tube intersects with the stable manifold of the Earth-Moon sub-system. We therefore go from the unstable manifold to the stable manifold which ultimately leads us to Moon.

This provides us a with a general idea of how to navigate efficiently in space. Hopping manifolds. We get on an unstable manifold to leave our initial planet and wait until it intersects with the stable manifold of our destination.

## 5. Interplanetary Transport Network

### 5.a. Hopping manifolds between planets.

### 5.b. The interplanetary transport network.

## Conclusion

## References

See slides.
