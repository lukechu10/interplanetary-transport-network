use std::f64;

use crate::tracer::{trace_planets, trace_ships, TracePlanets, TraceShips};
use ndarray::{array, s, Array2, Axis};
use ndarray_npy::write_npy;

pub fn start() {
    // Units are c * secs.
    let total_time = 20.;
    let dt = 0.0004;
    let time_steps = (total_time / dt) as usize;

    log::info!("dt = {dt}, time steps = {time_steps}");

    // Sun-Earth-Moon system.
    let m0 = 333000.0;
    let m1 = 1.;
    let m2 = 0.0123;
    // Sun-Earth distance in units of Earth-Moon distance.
    let r1 = 385.5;
    // Earth velocity relative to Sun.
    let v1 = (m0 as f64 / r1).sqrt();

    let masses = array![m0, m1, m2];
    // Reduced mass for Earth-Moon system.
    let mu = m1 * m2 / (m1 + m2);

    // Moon starts on opposite side of Sun from Earth.
    let mass_positions = array![[0., 0.], [r1 - mu, 0.], [r1 + 1. - mu, 0.]];
    let mass_velocities = array![
        [0., 0.],
        [0., v1 - m2 / (m1 + m2)],
        [0., v1 + m1 / (m1 + m2)]
    ];

    let opts = TracePlanets {
        masses: masses.view(),
        positions: mass_positions.view(),
        velocities: mass_velocities.view(),
        dt,
        time_steps,
    };
    let mass_positions_at_t = trace_planets(opts);

    let num_ships_per_velocity = 200;
    let num_velocity_groups = 20;
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
            leo_r * theta.cos() + mass_positions[[1, 0]]
        } else {
            leo_r * theta.sin() + mass_positions[[1, 1]]
        }
    });
    let leo_v = (m1 / leo_r).sqrt();
    // FIXME: The values below are actually incorrect because of numerical rounding errors.
    // However, they give the correct qualitative behaviour. To fix this, we should introduce
    // variable time-stepping and simulate with smaller time step at the start.
    let min_v = leo_v * 1.405;
    // let max_v = leo_v * 1.41;
    let max_v = leo_v * 1.435;

    let ship_velocities = Array2::from_shape_fn((num_ships, 2), |(i, j)| {
        let velocity_group = i / num_ships_per_velocity;
        assert!(velocity_group < num_velocity_groups);
        let velocity_multiplier = velocity_group as f64 / num_velocity_groups as f64;
        assert!(0. <= velocity_multiplier && velocity_multiplier < 1.);

        let theta = 2. * std::f64::consts::PI * i as f64 / num_ships_per_velocity as f64;
        let velocity = min_v + (max_v - min_v) * velocity_multiplier;

        if j == 0 {
            -velocity * theta.sin() + mass_velocities[[1, 0]]
        } else {
            velocity * theta.cos() + mass_velocities[[1, 1]]
        }
    });

    let opts = TraceShips {
        masses: masses.view(),
        mass_positions_at_t: mass_positions_at_t.view(),
        dt,
        time_steps,
        ship_positions: ship_positions.view(),
        ship_velocities: ship_velocities.view(),
        fictitious_force: |_, _| [0., 0.],
    };

    log::info!("tracing ships");
    let ship_positions_at_t = trace_ships(opts);

    // Compute ship status at every time step.
    log::info!("computing ship with smallest relative velocity to Moon");

    // Moon SOI.
    let r2_zone = 0.167;

    // Time until something happens.
    let start_time = 0.4;
    let first_time_step = (start_time / dt) as usize;

    let mut smallest_rel_v = f64::MAX;
    let mut smallest_rel_v_i = 0;
    let mut smallest_rel_v_time = 0.0;
    let mut smallest_rel_v_esc = 0.0;
    for t in first_time_step..time_steps {
        for i in 0..num_ships {
            let prev_pos = [
                ship_positions_at_t[[t - 1, i, 0]],
                ship_positions_at_t[[t - 1, i, 1]],
            ];
            let pos = [
                ship_positions_at_t[[t, i, 0]],
                ship_positions_at_t[[t, i, 1]],
            ];
            let dx = [pos[0] - prev_pos[0], pos[1] - prev_pos[1]];
            let v = [dx[0] / dt, dx[1] / dt];

            let mass_prev_pos = mass_positions_at_t.index_axis(Axis(0), t - 1);
            let mass_pos = mass_positions_at_t.index_axis(Axis(0), t);

            let moon_pos = mass_pos.index_axis(Axis(0), 2);

            let d2 = ((pos[0] - moon_pos[0]).powi(2) + (pos[1] - moon_pos[1]).powi(2)).sqrt();

            if d2 < r2_zone {
                // Check relative velocity to moon and see if its smaller than moon's escape
                // velocity at that distance.
                let esc_v = (2. * m2 / d2).sqrt();
                let moon_prev_pos = mass_prev_pos.index_axis(Axis(0), 2);
                let moon_v = [
                    moon_pos[0] - moon_prev_pos[0],
                    moon_pos[1] - moon_prev_pos[1],
                ];
                let v_rel = ((v[0] - moon_v[0]).powi(2) + (v[1] - moon_v[1]).powi(2)).sqrt();

                if v_rel < esc_v {
                    // More or less captured by Moon.
                    log::info!("ship {i} ballistically captured by Moon");
                    log::info!(
                        "x_i = ({}, {}), v_i = ({}, {})",
                        ship_positions[[i, 0]],
                        ship_positions[[i, 1]],
                        ship_velocities[[i, 0]],
                        ship_velocities[[i, 1]]
                    );
                }

                if v_rel < smallest_rel_v {
                    smallest_rel_v = v_rel;
                    smallest_rel_v_i = i;
                    smallest_rel_v_time = t as f64 * dt;
                    smallest_rel_v_esc = esc_v;
                }
            }
        }
    }

    log::info!("smallest rel v = {smallest_rel_v}, i = {smallest_rel_v_i}, after {smallest_rel_v_time} time");
    log::info!(
        "x_i = ({}, {}), v_i = ({}, {})",
        ship_positions[[smallest_rel_v_i, 0]],
        ship_positions[[smallest_rel_v_i, 1]],
        ship_velocities[[smallest_rel_v_i, 0]],
        ship_velocities[[smallest_rel_v_i, 1]]
    );
    log::info!(
        "|v_i| = {}",
        (ship_velocities[[smallest_rel_v_i, 0]].powi(2)
            + ship_velocities[[smallest_rel_v_i, 1]].powi(2))
        .sqrt()
    );
    log::info!("escape v for best result: {smallest_rel_v_esc}");

    write_npy("data/leo_to_moon_compute_bodies.npy", &mass_positions_at_t).unwrap();
    write_npy(
        "data/leo_to_moon_compute_ships.npy",
        &ship_positions_at_t.slice(s![.., smallest_rel_v_i, ..]),
    )
    .unwrap();
}
