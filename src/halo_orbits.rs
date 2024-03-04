use crate::tracer::{trace_ships, TraceShips};
use ndarray::array;
use ndarray_npy::write_npy;

pub fn start() {
    // Units are c * secs.
    let total_time = 5.;
    let dt = 0.0001;
    let time_steps = (total_time / dt) as usize;

    log::info!("dt = {dt}, time steps = {time_steps}");

    // Earth-Moon system.
    let m1 = 1.;
    let m2 = 0.0123;

    let masses = array![m1, m2];
    // Reduced mass for Earth-Moon system.
    let mu = m1 * m2 / (m1 + m2);

    // Moon starts on opposite side of Sun from Earth.
    let mass_positions = array![[-mu, 0.], [1. - mu, 0.]];
    let mass_velocities = array![[0., -m2 / (m1 + m2)], [0., m1 / (m1 + m2)]];

    // Moon angular frequency.
    let omega = 1. / mass_velocities[[1, 1]];

    // Use co-rotating frame.
    let mass_positions_at_t = mass_positions.broadcast((time_steps, 2, 2)).unwrap();

    // Assuming that m1 >> m2. L1 distance from Moon.
    let l1_r = (mu / 3. as f64).powf(1. / 3.);
    let l1 = array![mass_positions[[1, 0]] - l1_r, 0.];

    let distance_to_l1 = 0.01;
    let num_ships = 100;

    let ship_positions = array![l1[0] - distance_to_l1, 0.]
        .broadcast((num_ships, 2))
        .unwrap()
        .to_owned();
    let ship_velocities = array![0., 0.].broadcast((num_ships, 2)).unwrap().to_owned();

    let opts = TraceShips {
        masses: masses.view(),
        mass_positions_at_t: mass_positions_at_t.view(),
        dt,
        time_steps,
        ship_positions: ship_positions.view(),
        ship_velocities: ship_velocities.view(),
        fictitious_force: |r, v| {
            // Note: × designates the cross product.
            // omega is out of the 2d plane.

            // a_centrifugal = -omega × (omega × r)
            let omega_squared = omega * omega;
            let a_cf = [-omega_squared * r[0], -omega_squared * r[1]];

            // a_coriollis = -2 × omega × v
            let a_cor = [2. * omega * v[1], -2. * omega * v[0]];

            [a_cf[0] + a_cor[0], a_cf[1] + a_cor[1]]
        },
    };

    log::info!("tracing ships");
    let ship_positions_at_t = trace_ships(opts);

    write_npy("data/leo_to_moon_ships.npy", &ship_positions_at_t).unwrap();
}
