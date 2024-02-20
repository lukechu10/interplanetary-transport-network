use crate::tracer::{trace_planets, trace_ships, TracePlanets, TraceShips};
use ndarray::array;
use ndarray_npy::write_npy;

const EARTH_MASS: f64 = 1.;

const MOON_MASS: f64 = 0.0123 * EARTH_MASS;

const MOON_EARTH_DISTANCE: f64 = 1.;

/// v = sqrt(G * M / r) with G = 1.
const MOON_ORBITAL_SPEED: f64 = 1.;

pub fn start() {
    // Units are c * secs.
    const SIM_DURATION: f64 = 10.;
    const TIME_STEP: f64 = 0.01;

    log::info!(
        "time step = {TIME_STEP}, simulation duration = {SIM_DURATION}, total steps = {}",
        SIM_DURATION / TIME_STEP
    );

    let opts = TracePlanets {
        masses: array![EARTH_MASS, MOON_MASS],
        positions: array![[0., 0.], [MOON_EARTH_DISTANCE, 0.]],
        velocities: array![
            [0., -MOON_MASS / EARTH_MASS * MOON_ORBITAL_SPEED],
            [0., MOON_ORBITAL_SPEED],
        ],
        time_step: TIME_STEP,
        // 2 months.
        simulation_duration: SIM_DURATION,
    };

    log::info!("tracing planets");
    let positions = trace_planets(opts);

    let opts = TraceShips {
        masses: array![EARTH_MASS, MOON_MASS],
        mass_positions_at_t: positions.clone(),
        time_step: TIME_STEP,
        simulation_duration: SIM_DURATION,
        ship_positions: array![
            [MOON_EARTH_DISTANCE + 0.1, 0.],
            [MOON_EARTH_DISTANCE + 0.1, 0.],
            [-MOON_EARTH_DISTANCE, 0.],
        ],
        ship_velocities: array![
            [0., MOON_ORBITAL_SPEED + 0.1],
            [0., MOON_ORBITAL_SPEED - 0.1],
            [0., -MOON_ORBITAL_SPEED],
        ],
    };

    log::info!("tracing ships");
    let ship_positions = trace_ships(opts);

    write_npy("data/bodies.npy", &positions).unwrap();
    write_npy("data/ships.npy", &ship_positions).unwrap();
}
