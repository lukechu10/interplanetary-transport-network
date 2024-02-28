use crate::tracer::{trace_planets, trace_ships, TracePlanets, TraceShips};
use ndarray::{array, Array2};
use ndarray_npy::write_npy;

pub fn start() {
    // Units are c * secs.
    let total_time = 20.;
    let dt = 0.0004;
    let time_steps = (total_time / dt) as usize;

    log::info!("dt = {dt}, time steps = {time_steps}");

    // Earth-Moon system.
    let m1 = 1.;
    let m2 = 0.0123;
    let masses = array![m1, m2];
    let mu = m1 * m2 / (m1 + m2);
    let mass_positions = array![[-mu, 0.], [1. - mu, 0.]];
    let mass_velocities = array![[0., -m2 / (m1 + m2)], [0., m1 / (m1 + m2)]];

    let opts = TracePlanets {
        masses: masses.view(),
        positions: mass_positions.view(),
        velocities: mass_velocities.view(),
        dt,
        time_steps,
    };
    let mass_positions_at_t = trace_planets(opts);

    let num_ships_per_velocity = 200;
    let num_velocity_groups = 6;
    let num_ships = num_ships_per_velocity * num_velocity_groups;

    // Ships start all around LEO.
    //
    // Radius of LEO is 6728km.
    // Radius of Moon orbit is 384467km.
    // Normalise LEO radius so that Moon orbit is 1.
    let leo_r = 0.0174995;
    let ship_positions = Array2::from_shape_fn((num_ships, 2), |(i, j)| {
        let theta = 2. * std::f64::consts::PI * i as f64 / num_ships_per_velocity as f64;
        if j == 0 {
            leo_r * theta.cos() + mass_positions[[0, 0]]
        } else {
            leo_r * theta.sin() + mass_positions[[0, 1]]
        }
    });
    let leo_v = (m1 / leo_r).sqrt();
    // FIXME: The values below are actually incorrect because of numerical rounding errors.
    // However, they give the correct qualitative behaviour. To fix this, we should introduce
    // variable time-stepping and simulate with smaller time step at the start.
    let min_v = leo_v * 1.395;
    // let max_v = leo_v * 1.41;
    let max_v = leo_v * 1.405;

    let ship_velocities = Array2::from_shape_fn((num_ships, 2), |(i, j)| {
        let velocity_group = i / num_ships_per_velocity;
        assert!(velocity_group < num_velocity_groups);
        let velocity_multiplier = velocity_group as f64 / num_velocity_groups as f64;
        assert!(0. <= velocity_multiplier && velocity_multiplier < 1.);

        let theta = 2. * std::f64::consts::PI * i as f64 / num_ships_per_velocity as f64;
        let velocity = min_v + (max_v - min_v) * velocity_multiplier;

        if j == 0 {
            -velocity * theta.sin() + mass_velocities[[0, 0]]
        } else {
            velocity * theta.cos() + mass_velocities[[0, 1]]
        }
    });

    let opts = TraceShips {
        masses: masses.view(),
        mass_positions_at_t: mass_positions_at_t.view(),
        dt,
        time_steps,
        ship_positions: ship_positions.view(),
        ship_velocities: ship_velocities.view(),
    };

    log::info!("tracing ships");
    let ship_positions = trace_ships(opts);

    write_npy("data/part1b_bodies.npy", &mass_positions_at_t).unwrap();
    write_npy("data/part1b_ships.npy", &ship_positions).unwrap();
}
