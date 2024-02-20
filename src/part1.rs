use crate::tracer::{trace_ships, TraceShips};
use ndarray::{array, Array2, Array3};
use ndarray_npy::write_npy;

pub fn start() {
    // Units are c * secs.
    let total_time = 4000.;
    let dt = 0.01;
    let time_steps = (total_time / dt) as usize;

    log::info!("dt = {dt}, time steps = {time_steps}");

    let mass = array![1.];
    let mass_positions_at_t = Array3::zeros((time_steps, 1, 2));

    let num_ships = 12;

    let opts = TraceShips {
        masses: mass,
        mass_positions_at_t: mass_positions_at_t.clone(),
        dt,
        time_steps,
        ship_positions: array![1., -1.]
            .broadcast((num_ships, 2))
            .unwrap()
            .to_owned(),
        ship_velocities: array![0., 0.5]
            .broadcast((num_ships, 2))
            .unwrap()
            .to_owned()
            + Array2::from_shape_fn(
                (num_ships, 2),
                |(i, j)| if j == 1 { 0.01 * i as f64 } else { 0. },
            ),
    };

    log::info!("tracing ships");
    let ship_positions = trace_ships(opts);

    write_npy("data/bodies.npy", &mass_positions_at_t).unwrap();
    write_npy("data/ships.npy", &ship_positions).unwrap();
}
