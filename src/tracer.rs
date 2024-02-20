use ndarray::{s, Array, Array1, Array2, Array3, Axis};

/// Trace all the bodies in the simulation and save the results of their positions.
pub struct TracePlanets {
    pub masses: Array1<f64>,
    pub positions: Array2<f64>,
    pub velocities: Array2<f64>,
    pub time_step: f64,
    pub simulation_duration: f64,
}

pub fn trace_planets(opts: TracePlanets) -> Array3<f64> {
    let TracePlanets {
        masses,
        mut positions,
        mut velocities,
        time_step,
        simulation_duration,
    } = opts;
    let n = masses.len();
    assert_eq!(positions.shape(), [n, 2]);
    assert_eq!(velocities.shape(), [n, 2]);

    let mut time = 0.0;

    let mut positions_at_t = Array3::zeros((0, n, 2));
    while time < simulation_duration {
        positions_at_t.push(Axis(0), positions.view()).unwrap();

        positions = positions + velocities.clone() * time_step;

        // Acceleration due to all the other bodies.
        let accelerations = accelerations(&positions, &masses, &positions);
        velocities = velocities + accelerations * time_step;

        time += time_step;
    }

    positions_at_t
}

pub struct TraceShips {
    pub masses: Array1<f64>,
    pub mass_positions_at_t: Array3<f64>,
    pub ship_positions: Array2<f64>,
    pub ship_velocities: Array2<f64>,
    pub time_step: f64,
    pub simulation_duration: f64,
}

pub fn trace_ships(opts: TraceShips) -> Array3<f64> {
    let TraceShips {
        masses,
        mass_positions_at_t,
        mut ship_positions,
        mut ship_velocities,
        time_step,
        simulation_duration,
    } = opts;
    assert_eq!(mass_positions_at_t.len_of(Axis(1)), masses.len());

    let n = ship_positions.len_of(Axis(0));
    assert_eq!(ship_positions.shape(), [n, 2]);
    assert_eq!(ship_velocities.shape(), [n, 2]);

    let mut ship_positions_at_t = Array3::zeros((0, n, 2));
    let mut time = 0.0;
    // Iteration counter.
    let mut i = 0;

    while time < simulation_duration {
        ship_positions_at_t
            .push(Axis(0), ship_positions.view())
            .unwrap();

        ship_positions = ship_positions + ship_velocities.clone() * time_step;

        // Acceleration due to masses only (not other ships).
        let accelerations = accelerations(
            &ship_positions,
            &masses,
            &mass_positions_at_t.slice(s![i, .., ..]).to_owned(),
        );
        ship_velocities = ship_velocities + accelerations * time_step;

        time += time_step;
        i += 1;
    }

    ship_positions_at_t
}

/// Calculate the accelerations at every position due to the gravitational field of the bodies each
/// with mass from `masses` and positions from `mass_positions`.
pub fn accelerations(
    positions: &Array2<f64>,
    masses: &Array1<f64>,
    mass_positions: &Array2<f64>,
) -> Array2<f64> {
    let n = positions.len_of(Axis(0));
    assert_eq!(positions.shape(), [n, 2]);
    assert_eq!(mass_positions.shape(), [masses.len(), 2]);

    let mut buf = Array::zeros((n, 2));

    for (mut buf, position) in buf.rows_mut().into_iter().zip(positions.rows().into_iter()) {
        let mut acceleration = Array1::<f64>::zeros(2);
        let r = mass_positions - position.to_owned();
        for (&mass, r) in masses.iter().zip(r.rows().into_iter()) {
            let r_norm_squared = r.map(|x| x * x).sum();
            if r_norm_squared == 0.0 {
                // Skip if the bodies are at the same position.
                continue;
            }
            let r_unit = r.to_owned() / r_norm_squared.sqrt();
            // Note, we are setting G = 1.
            acceleration = acceleration + (r_unit * mass / r_norm_squared);
        }
        buf.assign(&acceleration);
    }

    buf
}
