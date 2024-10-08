use std::f64::consts::PI;

use crate::tracer::{trace_ships_inspect, TraceShips};
use ndarray::{array, Array1, Array2};

/// Numerically find the L1 point for the 3-body problem with `m1` and `m2` masses. Assumes that we
/// are in the co-rotating COM frame. Returns the x-coordinate of the L1 point.
///
/// This is done by numerically iterating over the x-axis to find the point where the net force is
/// 0.
pub fn find_l1_x(m1: f64, m2: f64) -> f64 {
    let mu = m1 * m2 / (m1 + m2);
    // Assume m1 is situated at -mu and m2 is situated at 1 - mu.
    let x1 = -mu;
    let x2 = 1. - mu;

    // Angular frequency of frame.
    let omega = (m1 + m2) / m1;

    let epsilon = 1e-8;
    let search_start = 1e-4;
    // Initial search range. We need to make sure we are between the two masses.
    let mut low = x1 + search_start;
    let mut high = x2 - search_start;

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
pub fn fictitious_force_rotating_frame(omega: f64) -> impl Fn([f64; 2], [f64; 2]) -> [f64; 2] {
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

pub fn start_earth_moon() {
    let distances_and_guesses = [
        // (0.0002, (0.0, 0.005), 1e-6),
        // (0.0004, (0.002, 0.004), 1e-6),
        // (0.0006, (0.002, 0.006), 1e-6),
        // (0.0008, (0.004, 0.008), 1e-6),
        // (0.0010, (0.006, 0.009), 1e-6),
        // (0.0012, (0.008, 0.012), 1e-6),
        // (0.0014, (0.010, 0.014), 1e-6),
        // (0.0016, (0.012, 0.016), 1e-6),
        // (0.0018, (0.013, 0.016), 1e-6),
        // (0.0020, (0.013, 0.020), 1e-6),
        // (0.0030, (0.020, 0.040), 1e-6),
        // (0.0040, (0.020, 0.1), 1e-6),
        // (0.0050, (0.040, 0.1), 1e-6),
        // (0.0060, (0.040, 0.1), 1e-6),
        // (0.0070, (0.040, 0.1), 1e-6),
        // (0.0080, (0.040, 0.1), 1e-6),
        // (0.0090, (0.040, 0.1), 1e-6),
        (0.0100, (0.040, 0.1), 1e-6),
        (0.0150, (0.100, 0.4), 1e-6),
        (0.0200, (0.100, 0.4), 1e-6),
        (0.0250, (0.100, 0.4), 1e-5),
        (0.0300, (0.100, 0.4), 1e-5),
        (0.0350, (0.100, 0.4), 1e-5),
        (0.0400, (0.100, 0.4), 1e-5),
    ];
    // Earth-Moon system.
    let m1 = 1.;
    let m2 = 0.0123;
    let mut velocities = Vec::new();
    for (d, (low_v, high_v), epsilon) in distances_and_guesses {
        let v =
            find_velocity_for_distance_to_l1(m1, m2, 3., 0.00005, d, low_v, high_v, 50, epsilon);
        log::info!("=> d = {d}, v = {v}");
        velocities.push(v);
    }

    log::info!("=== Final results ===");
    for ((d, _, _), v) in distances_and_guesses.iter().zip(velocities.iter()) {
        log::info!("d = {d}, v = {v}");
    }
}

pub fn start_sun_earth() {
    let distances_and_guesses = [
        // (0.0005, (0.025, 0.03), 1e-5),
        (0.001, (0.007, 0.010), 1e-7),
        (0.0015, (0.007, 0.020), 1e-7),
        (0.002, (0.01, 0.02), 1e-7),
    ];
    // Earth-Sun system. Note that to compare this with the Earth-Moon system, we need to scale
    // everything by 387.6.
    let m1 = 1.;
    let m2 = 1. / 333000.;
    let mut velocities = Vec::new();
    for (d, (low_v, high_v), epsilon) in distances_and_guesses {
        let v =
            find_velocity_for_distance_to_l1(m1, m2, 3., 0.00005, d, low_v, high_v, 50, epsilon);
        log::info!("=> d = {d}, v = {v}");
        velocities.push(v);
    }

    log::info!("=== Final results ===");
    for ((d, _, _), v) in distances_and_guesses.iter().zip(velocities.iter()) {
        log::info!("d = {d}, v = {v}");
    }
}

/// Iterate to find best starting velocity to achieve periodic orbit around Earth-Moon L1.
///
/// Should provide `low_v` and `high_v` as initial guesses for the velocity.
/// `num_ships` determines the number of ships to use in the search. Fewer ships increases speed
/// but may miss the solution if the initial guesses are too far off.
pub fn find_velocity_for_distance_to_l1(
    m1: f64,
    m2: f64,
    total_time: f64,
    dt: f64,
    distance_to_l1: f64,
    mut low_v: f64,
    mut high_v: f64,
    num_ships: usize,
    epsilon: f64,
) -> f64 {
    let time_steps = (total_time / dt) as usize;
    log::info!("dt = {dt}, time steps = {time_steps}");

    let masses = array![m1, m2];
    // Reduced mass for Earth-Moon system.
    let mu = m1 * m2 / (m1 + m2);

    // Use COM co-rotating frame.
    let mass_positions = array![[-mu, 0.], [1. - mu, 0.]];
    let mass_positions_at_t = mass_positions.broadcast((time_steps, 2, 2)).unwrap();

    // Orbit angular frequency.
    let omega = (m1 + m2) / m1;

    let l1_x = find_l1_x(m1, m2);
    let l1 = array![l1_x, 0.];
    log::info!("Computed L1 to be at x = {l1_x}");

    let ship_positions = array![l1[0] - distance_to_l1, 0.]
        .broadcast((num_ships, 2))
        .unwrap()
        .to_owned();

    log::info!(
        "Iterating to find ship velocity at distance {distance_to_l1} from L1 for periodic orbit"
    );
    // Best angle relative to x-axis. Want this value to be close to PI/2.
    let mut best_angle = 0.0;

    while (best_angle - PI / 2.).abs() > epsilon {
        let ship_velocities = Array2::from_shape_fn((num_ships, 2), |(i, j)| {
            let velocity = low_v + (high_v - low_v) * i as f64 / (num_ships as f64 - 1.0);
            if j == 0 {
                0.
            } else {
                velocity
            }
        });

        let opts = TraceShips {
            masses: masses.view(),
            mass_positions_at_t: mass_positions_at_t.view(),
            dt,
            time_steps,
            ship_positions: ship_positions.view(),
            ship_velocities: ship_velocities.view(),
            fictitious_force: fictitious_force_rotating_frame(omega),
        };

        // Angles of the ships when they cross x=0.
        let mut ship_angles = Array1::from_elem(num_ships, 0.);

        log::info!("tracing {num_ships} ships");
        trace_ships_inspect(
            opts,
            |ship| {
                // Check if we just crossed the x-axis in this time step.
                if ship.prev_r[1] > 0. && ship.r[1] < 0. {
                    // Calculate the angle of the ship relative to the x-axis.
                    let dx = ship.r[0] - ship.prev_r[0];
                    let dy = ship.r[1] - ship.prev_r[1];
                    assert!(dy < 0.);
                    let theta = if dx > 0. {
                        // We crossed the x-axis with a rightward velocity.
                        PI + (dy / dx).atan()
                    } else {
                        // We crossed the x-axis with a leftward velocity.
                        (dy / dx).atan()
                    };
                    ship_angles[ship.i] = theta;
                }
            },
            false,
        );

        // Go through all the angles and find the best ones.
        // The biggest angle smaller than PI/2 becomes the corresponding new low_v.
        // The smallest angle bigger than PI/2 becomes the corresponding new high_v.
        let mut best_smaller = -f64::INFINITY;
        let mut best_bigger = f64::INFINITY;
        let mut best_smaller_i = 0;
        let mut best_bigger_i = 0;
        for (i, &angle) in ship_angles.iter().enumerate() {
            if angle < PI / 2. && angle > best_smaller {
                best_smaller = angle;
                best_smaller_i = i;
            }
            if angle > PI / 2. && angle < best_bigger {
                best_bigger = angle;
                best_bigger_i = i;
            }
        }

        log::trace!("v range: ({low_v}, {high_v}), angle range: ({best_smaller}, {best_bigger}), angle delta: {}", best_smaller - PI/2.);

        // Set best_angle to best_smaller (we could also set it to best_bigger, this is arbitrary).
        best_angle = best_smaller;
        // Set low_v and high_v.
        let new_low_v = ship_velocities[[best_smaller_i, 1]];
        let new_high_v = ship_velocities[[best_bigger_i, 1]];
        if best_smaller == -f64::INFINITY {
            log::error!("No angle between 0 and PI/2 found.");
            break;
        }
        if best_bigger == f64::INFINITY {
            log::error!("No angle between PI/2 and PI found.");
            break;
        }
        if low_v > high_v {
            log::error!("low_v > high_v. Stuck.");
            break;
        }
        if new_low_v == low_v && new_high_v == high_v {
            log::error!("No change in low_v and high_v. Stuck.");
            break;
        }
        low_v = new_low_v;
        high_v = new_high_v;
    }

    low_v
}
