use nalgebra::Vector3;
use npy_derive::Serializable;
use tracer::{Body, TracerStep1};

pub mod consts;
pub mod tracer;

/// Earth radius in metres.
const EARTH_RADIUS: f64 = 6_371_000.;
const EARTH_MASS: f64 = 5.972e24;

/// Moon radius in metres.
const MOON_RADIUS: f64 = 1_737_000.;
const MOON_MASS: f64 = 7.348e22;

/// Distance from the Earth to the Moon in metres.
const MOON_EARTH_DISTANCE: f64 = 384_400_000.;

/// Moon orbital speed in metres per second.
const MOON_ORBITAL_SPEED: f64 = 1_023.;

fn main() {
    let tracer = TracerStep1 {
        time_step: 10.,
        // 1 month.
        simulation_duration: 60. * 60. * 24. * 30. * 100.,
        bodies: vec![
            Body {
                mass: EARTH_MASS,
                radius: EARTH_RADIUS,
                pos: Vector3::zeros(),
                // Set Earth's momentum so that center of mass is at rest.
                momentum: Vector3::new(0., -MOON_MASS * MOON_ORBITAL_SPEED, 0.),
            },
            Body {
                mass: MOON_MASS,
                radius: MOON_RADIUS,
                pos: Vector3::new(MOON_EARTH_DISTANCE, 0., 0.),
                momentum: Vector3::new(0., MOON_MASS * MOON_ORBITAL_SPEED, 0.),
            },
        ],
    };

    let positions = tracer.run();

    // Map to serializable data-structure.
    #[derive(Serializable)]
    struct Position {
        earth: [f64; 3],
        moon: [f64; 3],
    }
    let positions = positions
        .into_iter()
        .map(|v| Position {
            earth: [v[0].x, v[0].y, v[0].z],
            moon: [v[1].x, v[1].y, v[1].z],
        })
        .collect::<Vec<_>>();
    npy::to_file("../data/earth_moon_positions.npy", positions).unwrap();
}
