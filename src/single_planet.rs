use crate::tracer::{trace_ships, TraceShips};
use ndarray::{array, Array2, Array3};
use ndarray_npy::write_npy;

pub fn start() {
    // Units are c * secs.
    let total_time = 40.;
    let dt = 0.005;
    let time_steps = (total_time / dt) as usize;

    log::info!("dt = {dt}, time steps = {time_steps}");

    let mass = array![1.];
    let mass_positions_at_t = Array3::zeros((time_steps, 1, 2));

    let num_ships = 100;

    let ship_positions = array![1., 0.].broadcast((num_ships, 2)).unwrap().to_owned();

    let min_v = 1.0;
    let max_v = 1.5;
    let ship_velocites = Array2::from_shape_fn((num_ships, 2), |(i, j)| {
        let velocity = min_v + (max_v - min_v) * i as f64 / (num_ships as f64 - 1.0);
        if j == 0 {
            0.
        } else {
            velocity
        }
    });
    let opts = TraceShips {
        masses: mass.view(),
        mass_positions_at_t: mass_positions_at_t.view(),
        dt,
        time_steps,
        ship_positions: ship_positions.view(),
        ship_velocities: ship_velocites.view(),
    };

    log::info!("tracing ships");
    let ship_positions = trace_ships(opts);

    write_npy("data/single_planet_bodies.npy", &mass_positions_at_t).unwrap();
    write_npy("data/single_planet_ships.npy", &ship_positions).unwrap();
    write_npy(
        "data/single_planet_ship_initial_velocities.npy",
        &ship_velocites,
    )
    .unwrap();
}
