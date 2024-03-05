use crate::{
    halo_orbits_compute::{fictitious_force_rotating_frame, find_l1_x},
    tracer::{trace_ships, TraceShips},
};
use ndarray::{array, Array2, Array3, ArrayView2};
use ndarray_npy::write_npy;

pub fn start_earth_moon() {
    // Earth-Moon system.
    let m1 = 1.;
    let m2 = 0.0123;

    // Part 1 ---- Search for halo orbit with distance 0.001
    let distance_to_l1 = 0.0200;
    let num_ships = 10;

    let ship_positions = array![-distance_to_l1, 0.]
        .broadcast((num_ships, 2))
        .unwrap()
        .to_owned();
    let min_v = 0.175;
    let max_v = 0.210;
    let ship_velocities = Array2::from_shape_fn((num_ships, 2), |(i, j)| {
        // Make the first ship the best ship.
        // Other ships are merely for visualisation when we apply small perturbation.
        if i == 0 {
            if j == 0 {
                0.
            } else {
                0.19227550269368912
            }
        } else {
            let velocity = min_v + (max_v - min_v) * i as f64 / (num_ships as f64 - 2.0);
            if j == 0 {
                0.
            } else {
                velocity
            }
        }
    });

    let ship_positions_at_t = simulate_ships(
        2.,
        m1,
        m2,
        ship_positions.view(),
        ship_velocities.view(),
        true,
    );
    write_npy("data/halo_orbits_search.npy", &ship_positions_at_t).unwrap();

    // Part 2 ---- Show orbits with various different distances.
    // We exclude the ship with distance 0.0010 since it is already included in the previous
    // simulation.
    //
    // Data for velocities are found by running `crate::halo_orbits_compute`.
    let ship_positions = array![
        // [-0.0002, 0.],
        // [-0.0004, 0.],
        // [-0.0006, 0.],
        // [-0.0008, 0.],
        // // [-0.0010, 0.],
        // [-0.0012, 0.],
        // [-0.0014, 0.],
        // [-0.0016, 0.],
        // [-0.0018, 0.],
        // [-0.0020, 0.],
        // // Increase spacing.
        // [-0.0030, 0.],
        // [-0.0040, 0.],
        // [-0.0050, 0.],
        // [-0.0060, 0.],
        // [-0.0070, 0.],
        // [-0.0080, 0.],
        // [-0.0090, 0.],
        [-0.0100, 0.],
        [-0.0150, 0.],
        [-0.0200, 0.],
        [-0.0250, 0.],
        [-0.0300, 0.],
        [-0.0350, 0.],
        [-0.0400, 0.],
    ];
    let ship_velocities = array![
        // [0., 0.0016606407345798996],
        // [0., 0.003325998590411014],
        // [0., 0.00499605554467535],
        // [0., 0.006670864094007755],
        // // [0., 0.008350417993613309],
        // [0., 0.010034790099432749],
        // [0., 0.011723989431725399],
        // [0., 0.013418082601637073],
        // [0., 0.015117025028270708],
        // [0., 0.016820927383269603],
        // // Increase spacing.
        // [0., 0.02541529881083493],
        // [0., 0.03413726892581658],
        // [0., 0.04299069218627364],
        // [0., 0.05197897929811189],
        // [0., 0.0611055021673775],
        // [0., 0.07037314040919743],
        // [0., 0.07978444355668131],
        [0., 0.08934111342264894],
        [0., 0.1392916602048911],
        [0., 0.19227550269368912],
        [0., 0.24582022866010467],
        [0., 0.2952922746162443],
        [0., 0.33682369955181457],
        [0., 0.3700428861291137],
    ];
    let ship_positions_at_t = simulate_ships(
        4.,
        m1,
        m2,
        ship_positions.view(),
        ship_velocities.view(),
        false,
    );
    write_npy("data/halo_orbits.npy", &ship_positions_at_t).unwrap();
}

pub fn start_sun_earth() {
    // Sun-Earth system.
    let m1 = 1.;
    let m2 = 1. / 333000.;

    // Part 1 ---- Search for halo orbit with distance 0.001
    let distance_to_l1 = 0.002;
    let num_ships = 10;

    let ship_positions = array![-distance_to_l1, 0.]
        .broadcast((num_ships, 2))
        .unwrap()
        .to_owned();
    let min_v = 0.016;
    let max_v = 0.018;
    let ship_velocities = Array2::from_shape_fn((num_ships, 2), |(i, j)| {
        let velocity = min_v + (max_v - min_v) * i as f64 / (num_ships as f64 - 2.0);
        if j == 0 {
            0.
        } else {
            velocity
        }
    });

    let ship_positions_at_t = simulate_ships(
        2.,
        m1,
        m2,
        ship_positions.view(),
        ship_velocities.view(),
        false,
    );
    write_npy(
        "data/halo_orbits_sun_earth_search.npy",
        &ship_positions_at_t,
    )
    .unwrap();
}

/// Simulate ships around the L1 point of the Earth-Moon system.
///
/// If `write_l1` is `true`, writes the value of L1 to `data/halo_orbits_l1.npy`.
///
/// `ship_positions` should be relative to the L1 point and `ship_velocities` are in the
/// co-rotating COM frame.
pub fn simulate_ships<'a>(
    total_time: f64,
    m1: f64,
    m2: f64,
    ship_positions: ArrayView2<'a, f64>,
    ship_velocities: ArrayView2<'a, f64>,
    write_l1: bool,
) -> Array3<f64> {
    let dt = 0.00005;
    let time_steps = (total_time / dt) as usize;

    log::info!("dt = {dt}, time steps = {time_steps}");

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
