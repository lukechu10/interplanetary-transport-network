use crate::tracer::{trace_ships, TraceShips};
use ndarray::array;
use ndarray_npy::write_npy;

pub fn start() {
    // Units are c * secs.
    let total_time = 10.;
    let dt = 0.0001;
    let time_steps = (total_time / dt) as usize;

    log::info!("dt = {dt}, time steps = {time_steps}");

    let mass = array![1., 5., 1., 1.];
    let mass_positions_at_t = array![[-1., 1.], [1., 1.], [1., -1.], [-1., -1.]]
        .broadcast((time_steps, 4, 2))
        .unwrap()
        .to_owned();

    let num_ships = 100;
    let ship_positions = array![-1.1, 1.]
        .broadcast((num_ships, 2))
        .unwrap()
        .to_owned();
    let mut ship_velocities = array![0., 3.162]
        .broadcast((num_ships, 2))
        .unwrap()
        .to_owned();

    // Variate ship initial velocities.
    let variation = 1.0 / num_ships as f64;
    for i in 0..num_ships {
        ship_velocities[[i, 1]] += variation * (i - num_ships / 2) as f64;
    }

    let opts = TraceShips {
        masses: mass.view(),
        mass_positions_at_t: mass_positions_at_t.view(),
        dt,
        time_steps,
        ship_positions: ship_positions.view(),
        ship_velocities: ship_velocities.view(),
    };

    log::info!("tracing ships");
    let ship_positions = trace_ships(opts);

    write_npy("data/part1a_bodies.npy", &mass_positions_at_t).unwrap();
    write_npy("data/part1a_ships.npy", &ship_positions).unwrap();
}
