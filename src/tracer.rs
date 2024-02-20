use ndarray::{s, Array, Array1, Array2, Array3, Axis};

/// Trace all the bodies in the simulation and save the results of their positions.
pub struct TracePlanets {
    pub masses: Array1<f64>,
    pub positions: Array2<f64>,
    pub velocities: Array2<f64>,
    pub dt: f64,
    pub time_steps: usize,
}

pub fn trace_planets(opts: TracePlanets) -> Array3<f64> {
    let TracePlanets {
        masses,
        mut positions,
        mut velocities,
        dt,
        time_steps,
    } = opts;
    let n = masses.len();
    assert_eq!(positions.shape(), [n, 2]);
    assert_eq!(velocities.shape(), [n, 2]);

    let mut positions_at_t = Array3::zeros((0, n, 2));
    for _ in 0..time_steps {
        positions_at_t.push(Axis(0), positions.view()).unwrap();

        // Acceleration due to all the other bodies.
        let accelerations = accelerations(&positions, &masses, &positions);
        velocities = velocities + accelerations * dt;
        positions = positions + velocities.clone() * dt;
    }

    positions_at_t
}

pub struct TraceShips {
    pub masses: Array1<f64>,
    pub mass_positions_at_t: Array3<f64>,
    pub ship_positions: Array2<f64>,
    pub ship_velocities: Array2<f64>,
    pub dt: f64,
    pub time_steps: usize,
}

pub fn trace_ships(opts: TraceShips) -> Array3<f64> {
    let TraceShips {
        masses,
        mass_positions_at_t,
        mut ship_positions,
        mut ship_velocities,
        dt,
        time_steps,
    } = opts;
    assert_eq!(mass_positions_at_t.len_of(Axis(1)), masses.len());

    let n = ship_positions.len_of(Axis(0));
    assert_eq!(ship_positions.shape(), [n, 2]);
    assert_eq!(ship_velocities.shape(), [n, 2]);

    let mut ship_positions_at_t = Array3::zeros((0, n, 2));

    for i in 0..time_steps {
        ship_positions_at_t
            .push(Axis(0), ship_positions.view())
            .unwrap();

        // Acceleration due to masses only (not other ships).
        let accelerations = accelerations(
            &ship_positions,
            &masses,
            &mass_positions_at_t.slice(s![i, .., ..]).to_owned(),
        );
        ship_velocities = ship_velocities + accelerations * dt;
        ship_positions = ship_positions + ship_velocities.clone() * dt;
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
        let r = mass_positions - position.to_owned();
        let r_normed_squared = r
            .map(|x| x * x)
            .sum_axis(Axis(1))
            .map(|&x| if x == 0. { 1. } else { x });
        let r_unit = r / r_normed_squared.mapv(f64::sqrt);
        let acceleration = (r_unit * masses / r_normed_squared).sum_axis(Axis(0));
        buf.assign(&acceleration);
    }

    buf
}
