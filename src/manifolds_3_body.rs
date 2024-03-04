use crate::{
    halo_orbits_compute::{fictitious_force_rotating_frame, find_l1_x},
    tracer::{trace_ships, TraceShips},
};
use ndarray::{array, Array3, ArrayView2, Axis};
use ndarray_npy::write_npy;

pub fn start() {
    let distance_to_l1 = -0.001;
    let ship_velocity = array![[0.0, 0.008350417993613309]];
    let mut perturbations = array![
        [0., 0.],
        [0.0001, 0.],
        [0., 0.0001],
        [-0.0001, 0.],
        [0., -0.0001],
    ];
    perturbations
        .append(Axis(0), (perturbations.clone() * 2.).view())
        .unwrap();
    let ships_num = perturbations.len_of(Axis(0));

    let ship_positions = array![[distance_to_l1, 0.]]
        .broadcast((ships_num, 2))
        .unwrap()
        .to_owned();
    let ship_velocities = perturbations + ship_velocity;

    let ship_positions_at_t =
        simulate_ships(5., ship_positions.view(), ship_velocities.view(), false);
    write_npy("data/manifolds_3_body.npy", &ship_positions_at_t).unwrap();

    let m1 = 1.;
    let m2 = 0.0123;
    let l1_x = find_l1_x(m1, m2);
    write_npy("data/manifolds_3_body_earth_moon_l1.npy", &array![l1_x, 0.]).unwrap()
}

/// Simulate ships around the L1 point of the Earth-Moon system.
///
/// If `write_l1` is `true`, writes the value of L1 to `data/halo_orbits_l1.npy`.
///
/// `ship_positions` should be relative to the L1 point and `ship_velocities` are in the
/// co-rotating COM frame.
pub fn simulate_ships<'a>(
    total_time: f64,
    ship_positions: ArrayView2<'a, f64>,
    ship_velocities: ArrayView2<'a, f64>,
    write_l1: bool,
) -> Array3<f64> {
    let dt = 0.00005;
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

    // Moon angular frequency.
    let omega = (m1 + m2) / m1;

    // Use co-rotating frame.
    let mass_positions_at_t = mass_positions.broadcast((time_steps, 2, 2)).unwrap();

    let l1_x = find_l1_x(m1, m2);
    let l1 = array![l1_x, 0.];
    log::info!("Computed L1 to be at x = {l1_x}");
    if write_l1 {
        write_npy("data/halo_orbits_l1.npy", &l1).unwrap();
    }

    // Offset ship positions by L1.
    let ship_positions = ship_positions.to_owned() + l1.into_shape((1, 2)).unwrap();

    let opts = TraceShips {
        masses: masses.view(),
        mass_positions_at_t: mass_positions_at_t.view(),
        dt,
        time_steps,
        ship_positions: ship_positions.view(),
        ship_velocities: ship_velocities.view(),
        fictitious_force: fictitious_force_rotating_frame(omega),
    };

    log::info!("tracing ships");
    trace_ships(opts)
}
