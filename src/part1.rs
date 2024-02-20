use crate::tracer::{Body, TraceCelestialBodies, TraceShips};
use nalgebra::Vector2;
use ndarray::array;
use ndarray_npy::write_npy;

const EARTH_MASS: f64 = 5.972e24;

const MOON_MASS: f64 = 7.348e22;

/// Distance from the Earth to the Moon in metres.
const MOON_EARTH_DISTANCE: f64 = 384_400_000.;

/// Moon orbital speed in metres per second.
const MOON_ORBITAL_SPEED: f64 = 1_023.;

pub fn start() {
    const SIM_DURATION: f64 = 60. * 60. * 24. * 30. * 20.;
    const TIME_STEP: f64 = 20.;

    let bodies = vec![
        Body {
            mass: EARTH_MASS,
            pos: Vector2::zeros(),
            // Set Earth's momentum so that center of mass is at rest.
            velocity: Vector2::new(0., -MOON_MASS / EARTH_MASS * MOON_ORBITAL_SPEED),
        },
        Body {
            mass: MOON_MASS,
            pos: Vector2::new(MOON_EARTH_DISTANCE, 0.),
            velocity: Vector2::new(0., MOON_ORBITAL_SPEED),
        },
    ];
    let tracer = TraceCelestialBodies {
        time_step: TIME_STEP,
        // 2 months.
        simulation_duration: SIM_DURATION,
        bodies: bodies.clone(),
    };

    let positions = tracer.run();

    let trace_ships = TraceShips {
        bodies,
        positions_at_t: positions.clone(),
        time_step: TIME_STEP,
        simulation_duration: SIM_DURATION,
        ship_positions: array![
            [MOON_EARTH_DISTANCE + 1_0000_000., 0.],
            [MOON_EARTH_DISTANCE + 1_0000_000., 0.],
            [-MOON_EARTH_DISTANCE, 0.],
        ],
        ship_velocities: array![
            [0., MOON_ORBITAL_SPEED + 1000.],
            [0., MOON_ORBITAL_SPEED - 1000.],
            [0., -MOON_ORBITAL_SPEED],
        ],
    };

    let ship_positions = trace_ships.run();

    write_npy("data/bodies.npy", &positions).unwrap();
    write_npy("data/ships.npy", &ship_positions).unwrap();
}
