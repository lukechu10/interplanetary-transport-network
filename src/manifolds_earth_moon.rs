use crate::{
    halo_orbits_compute::{fictitious_force_rotating_frame, find_l1_x},
    tracer::{trace_ships, trace_ships_inspect, TraceShips},
};
use ndarray::{array, s, Array2, Array3, ArrayView2, Axis};
use ndarray_npy::write_npy;

pub fn start() {
    let distance_to_l1 = -0.0100;
    let velocity = 0.08934111342264894;

    // Simulate ship to get complete orbit.
    let (orbit_r, orbit_v) = simulate_ships(
        4.,
        array![[distance_to_l1, 0.]].view(),
        array![[0., velocity]].view(),
        false,
    );
    write_npy("data/manifolds_earth_moon_orbit.npy", &orbit_r).unwrap();

    let time_steps = orbit_r.len_of(Axis(0));

    // Now that we have the periodic orbit, we can perturb it at various points to get a rough
    // outline of the unstable manifold.
    //
    // For simplicity, we only perturb velocity.
    let epsilon = 0.001;
    let perturbations = array![[epsilon, 0.], [-epsilon, 0.], [0., epsilon], [0., -epsilon]];
    let perturbations_per_point = perturbations.len_of(Axis(0));
    let perturbation_points_count = 40;

    // Intialize ship positions and velocities.
    let mut ship_positions =
        Array2::zeros((perturbation_points_count * perturbations_per_point, 2));
    let mut ship_velocities = ship_positions.clone();

    for i in 0..perturbation_points_count {
        let t = i as f64 / (perturbation_points_count - 1) as f64 * (time_steps - 1) as f64;
        let t = t as usize;

        for j in 0..perturbations_per_point {
            let perturbation = perturbations.slice(s![j, ..]).into_shape(2).unwrap();
            let position = orbit_r.slice(s![t, 0, ..]).into_shape(2).unwrap();
            let base_v = orbit_v.slice(s![t, 0, ..]).into_shape(2).unwrap();
            let perturbed_velocity = base_v.to_owned() + perturbation;

            ship_positions
                .slice_mut(s![i * perturbations_per_point + j, ..])
                .assign(&position);
            ship_velocities
                .slice_mut(s![i * perturbations_per_point + j, ..])
                .assign(&perturbed_velocity);
        }
    }

    // Now we can simulate the ships.
    let dt = 0.00005;
    let total_time = 4.;
    let time_steps = (total_time / dt) as usize;

    let m1 = 1.;
    let m2 = 0.0123;
    let mu = m1 * m2 / (m1 + m2);
    let omega = (m1 + m2) / m1;
    let masses = array![m1, m2];
    let mass_positions = array![[-mu, 0.], [1. - mu, 0.]];
    let mass_positions_at_t = mass_positions
        .broadcast((time_steps, 2, 2))
        .unwrap()
        .to_owned();

    // Trace unstable manifold.
    let opts = TraceShips {
        masses: masses.view(),
        mass_positions_at_t: mass_positions_at_t.view(),
        dt,
        time_steps,
        ship_positions: ship_positions.view(),
        ship_velocities: ship_velocities.view(),
        fictitious_force: fictitious_force_rotating_frame(omega),
    };
    let unstable_t = trace_ships(opts);
    write_npy("data/manifolds_earth_moon_unstable.npy", &unstable_t).unwrap();

    // Now reverse ship_velocities and omega to trace stable manifold.
    let ship_velocities = -ship_velocities;
    let omega = -omega;
    let opts = TraceShips {
        masses: masses.view(),
        mass_positions_at_t: mass_positions_at_t.view(),
        dt,
        time_steps,
        ship_positions: ship_positions.view(),
        ship_velocities: ship_velocities.view(),
        fictitious_force: fictitious_force_rotating_frame(omega),
    };
    let stable_t = trace_ships(opts);
    write_npy("data/manifolds_earth_moon_stable.npy", &stable_t).unwrap();

    // Save L1 point for reference in animation.
    let m1 = 1.;
    let m2 = 0.0123;
    let l1_x = find_l1_x(m1, m2);
    write_npy("data/manifolds_earth_moon_l1.npy", &array![l1_x, 0.]).unwrap()
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
) -> (Array3<f64>, Array3<f64>) {
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
    trace_ships_inspect(opts, |_| {}, true)
}
