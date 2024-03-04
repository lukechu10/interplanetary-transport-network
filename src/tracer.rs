use ndarray::{s, Array, Array2, Array3, ArrayView1, ArrayView2, ArrayView3, Axis};

/// Trace all the bodies in the simulation and save the results of their positions.
pub struct TracePlanets<'a> {
    pub masses: ArrayView1<'a, f64>,
    pub positions: ArrayView2<'a, f64>,
    pub velocities: ArrayView2<'a, f64>,
    pub dt: f64,
    pub time_steps: usize,
}

pub fn trace_planets(opts: TracePlanets) -> Array3<f64> {
    let TracePlanets {
        masses,
        positions,
        velocities,
        dt,
        time_steps,
    } = opts;
    let n = masses.len();
    assert_eq!(positions.shape(), [n, 2]);
    assert_eq!(velocities.shape(), [n, 2]);

    let mut positions = positions.to_owned();
    let mut velocities = velocities.to_owned();

    let mut positions_at_t = Array3::zeros((0, n, 2));
    for _ in 0..time_steps {
        positions_at_t.push(Axis(0), positions.view()).unwrap();

        // Acceleration due to all the other bodies.
        let accelerations = accelerations(positions.view(), masses.view(), positions.view());
        velocities = velocities + accelerations * dt;
        positions = positions + velocities.clone() * dt;
    }

    positions_at_t
}

pub struct TraceShips<'a, F>
where
    F: Fn([f64; 2], [f64; 2]) -> [f64; 2],
{
    pub masses: ArrayView1<'a, f64>,
    pub mass_positions_at_t: ArrayView3<'a, f64>,
    pub ship_positions: ArrayView2<'a, f64>,
    pub ship_velocities: ArrayView2<'a, f64>,
    pub dt: f64,
    pub time_steps: usize,
    pub fictitious_force: F,
}

pub fn trace_ships<F>(opts: TraceShips<F>) -> Array3<f64>
where
    F: Fn([f64; 2], [f64; 2]) -> [f64; 2],
{
    trace_ships_inspect(opts, |_| {})
}

/// Parameter passed to the inspect function in [`trace_ships_inspect`].
pub struct InspectData {
    /// Value of x in the previous time step.
    pub prev_r: [f64; 2],
    /// Value of x in the current time step.
    pub r: [f64; 2],
    /// Index of the ship that is being inspected.
    pub i: usize,
}

pub fn trace_ships_inspect<F, G>(opts: TraceShips<F>, mut inspect: G) -> Array3<f64>
where
    F: Fn([f64; 2], [f64; 2]) -> [f64; 2],
    G: FnMut(InspectData),
{
    let TraceShips {
        masses,
        mass_positions_at_t,
        ship_positions,
        ship_velocities,
        dt,
        time_steps,
        fictitious_force,
    } = opts;
    assert_eq!(mass_positions_at_t.len_of(Axis(1)), masses.len());

    let n = ship_positions.len_of(Axis(0));
    assert_eq!(ship_positions.shape(), [n, 2]);
    assert_eq!(ship_velocities.shape(), [n, 2]);

    log::info!("tracing {n} ships for {time_steps} time steps");

    let mut ship_positions = ship_positions.to_owned();
    let mut ship_velocities = ship_velocities.to_owned();
    let mut ship_positions_at_t = Array3::zeros((0, n, 2));

    for i in 0..time_steps {
        ship_positions_at_t
            .push(Axis(0), ship_positions.view())
            .unwrap();

        // Acceleration due to masses only (not other ships).
        let mut accelerations = accelerations(
            ship_positions.view(),
            masses.view(),
            mass_positions_at_t.slice(s![i, .., ..]),
        );
        // Accelerations due to fictitious forces.
        for (mut acceleration, (ship_position, ship_velocity)) in
            accelerations.axis_iter_mut(Axis(0)).zip(
                ship_positions
                    .axis_iter(Axis(0))
                    .zip(ship_velocities.axis_iter(Axis(0))),
            )
        {
            let ship_position = ship_position.as_slice().unwrap().try_into().unwrap();
            let ship_velocity = ship_velocity.as_slice().unwrap().try_into().unwrap();
            let fictitious_force = fictitious_force(ship_position, ship_velocity);
            acceleration[0] += fictitious_force[0];
            acceleration[1] += fictitious_force[1];
        }

        ship_velocities = ship_velocities + accelerations * dt;
        for (ship_i, (mut ship_position, ship_velocity)) in ship_positions
            .axis_iter_mut(Axis(0))
            .zip(ship_velocities.axis_iter(Axis(0)))
            .enumerate()
        {
            let new_position = [
                ship_position[0] + ship_velocity[0] * dt,
                ship_position[1] + ship_velocity[1] * dt,
            ];
            inspect(InspectData {
                prev_r: [ship_position[0], ship_position[1]],
                r: [new_position[0], new_position[1]],
                i: ship_i,
            });
            ship_position[0] = new_position[0];
            ship_position[1] = new_position[1];
        }
    }

    ship_positions_at_t
}

/// Calculate the accelerations at every position due to the gravitational field of the bodies each
/// with mass from `masses` and positions from `mass_positions`.
pub fn accelerations(
    positions: ArrayView2<f64>,
    masses: ArrayView1<f64>,
    mass_positions: ArrayView2<f64>,
) -> Array2<f64> {
    let n = positions.len_of(Axis(0));
    assert_eq!(positions.shape(), [n, 2]);
    assert_eq!(mass_positions.shape(), [masses.len(), 2]);

    let mut buf = Array::zeros((n, 2));

    for (mut buf, position) in buf.rows_mut().into_iter().zip(positions.rows().into_iter()) {
        let r = mass_positions.to_owned() - position;
        let r_normed_squared =
            r.map(|x| x * x)
                .sum_axis(Axis(1))
                .map(|&x| if x == 0. { 1. } else { x.sqrt() });

        let masses = masses.into_shape([masses.len(), 1]).unwrap();
        let r_cubed = r_normed_squared
            .map(|&x| x.powi(3))
            .into_shape([masses.len(), 1])
            .unwrap();
        let accelerations = r * masses / r_cubed;
        buf.assign(&accelerations.sum_axis(Axis(0)));
    }

    buf
}
