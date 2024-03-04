use crate::tracer::{trace_ships, TraceShips};
use ndarray::{array, Array2, Array3, ArrayView2};
use ndarray_npy::write_npy;

/// Numerically find the L1 point for the 3-body problem with `m1` and `m2` masses. Assumes that we
/// are in the co-rotating COM frame. Returns the x-coordinate of the L1 point.
///
/// This is done by numerically iterating over the x-axis to find the point where the net force is
/// 0.
fn find_l1_x(m1: f64, m2: f64) -> f64 {
    let mu = m1 * m2 / (m1 + m2);
    // Assume m1 is situated at -mu and m2 is situated at 1 - mu.
    let x1 = -mu;
    let x2 = 1. - mu;

    // Angular frequency of frame.
    let omega = (m1 + m2) / m1;

    let epsilon = 1e-6;
    // Initial search range. We need to make sure we are between the two masses.
    let mut low = -mu + epsilon;
    let mut high = 1. - mu - epsilon;

    let mut a = f64::INFINITY;
    let mut x = 0.0;
    while a.abs() > epsilon {
        // Pick the mid-point of the range.
        x = (low + high) / 2.;

        // Calculate the force at x.
        let f1 = -m1 / (x - x1).powi(2);
        let f2 = m2 / (x - x2).powi(2);
        let f_c = omega * omega * x;

        a = f1 + f2 + f_c;
        if a > 0. {
            // Pulling towards m2. Move higher bound closer.
            high = x;
        } else {
            // Pulling towards m1. Move lower bound closer.
            low = x;
        }
    }

    x
}

/// Returns a closure giving the fictitious force in a rotating reference frame with constant
/// angular velocity `omega`.
fn fictitious_force_rotating_frame(omega: f64) -> impl Fn([f64; 2], [f64; 2]) -> [f64; 2] {
    move |r, v| {
        // Note: × designates the cross product.
        // omega is out of the 2d plane.

        // a_centrifugal = -omega × (omega × r)
        let omega_squared = omega * omega;
        let a_cf = [omega_squared * r[0], omega_squared * r[1]];

        // a_coriollis = -2 × omega × v
        let a_cor = [2. * omega * v[1], -2. * omega * v[0]];

        [a_cf[0] + a_cor[0], a_cf[1] + a_cor[1]]
    }
}

pub fn start() {
    // Part 1 ---- Search for halo orbit with distance 0.001
    let distance_to_l1 = 0.001;
    let num_ships = 10;

    let ship_positions = array![-distance_to_l1, 0.]
        .broadcast((num_ships, 2))
        .unwrap()
        .to_owned();
    let min_v = 0.0080;
    let max_v = 0.0087;
    let ship_velocities = Array2::from_shape_fn((num_ships, 2), |(i, j)| {
        // Make the first ship the best ship.
        // Other ships are merely for visualisation when we apply small perturbation.
        if i == 0 {
            if j == 0 {
                0.
            } else {
                0.00835041
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

    let ship_positions_at_t =
        simulate_ships(1.5, ship_positions.view(), ship_velocities.view(), true);
    write_npy("data/halo_orbits_search.npy", &ship_positions_at_t).unwrap();

    // Part 2 ---- Show orbits with various different distances.
    // We include the ship with distance 0.0010 since it is already included in the previous
    // simulation.
    let ship_positions = array![
        [-0.0002, 0.],
        [-0.0004, 0.],
        [-0.0006, 0.],
        [-0.0008, 0.],
        // [-0.0010, 0.],
        [-0.0012, 0.]
    ];
    let ship_velocities = array![
        [0., 0.0016606407345798996],
        [0., 0.003325998590411014],
        [0., 0.00499605554467535],
        [0., 0.006670864094007755],
        // [0., 0.008350417993613309],
        [0., 0.010034790099432749],
    ];
    let ship_positions_at_t =
        simulate_ships(3., ship_positions.view(), ship_velocities.view(), false);
    write_npy("data/halo_orbits.npy", &ship_positions_at_t).unwrap();
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
