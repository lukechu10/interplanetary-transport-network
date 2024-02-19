use nalgebra::Vector2;
use ndarray::{s, Array, Array1, Array2, Array3, Axis};

use crate::consts::G;

/// Represents a body that produces a gravitational field.
#[derive(Clone, Copy)]
pub struct Body {
    /// Mass in kg.
    pub mass: f64,
    // Phase space coordinates. Units are SI.
    pub pos: Vector2<f64>,
    pub velocity: Vector2<f64>,
}

/// Trace all the bodies in the simulation and save the results of their positions.
pub struct TraceCelestialBodies {
    /// List of bodies in the simulation. Should start with initial conditons.
    pub bodies: Vec<Body>,
    /// Simulation time step in seconds.
    pub time_step: f64,
    /// Simulation duration in seconds.
    pub simulation_duration: f64,
}

impl TraceCelestialBodies {
    pub fn run(self) -> Array3<f64> {
        let n = self.bodies.len();
        let masses = Array::from_iter(self.bodies.iter().map(|b| b.mass));
        let mut positions = Array::from_shape_fn((n, 2), |(i, j)| self.bodies[i].pos[j]);
        let mut velocities = Array::from_shape_fn((n, 2), |(i, j)| self.bodies[i].velocity[j]);

        let mut time = 0.0;

        let mut positions_at_t = Array3::zeros((0, n, 2));
        while time < self.simulation_duration {
            positions_at_t.push(Axis(0), positions.view()).unwrap();

            let accelerations = self.accelerations(&masses, &positions);
            positions = positions + velocities.clone() * self.time_step;
            velocities = velocities + accelerations * self.time_step;

            time += self.time_step;
        }

        positions_at_t
    }

    fn accelerations(&self, masses: &Array1<f64>, positions: &Array2<f64>) -> Array2<f64> {
        let n = masses.len();
        let mut buf = Array::zeros((n, 2));
        for i in 0..n {
            let mut a = Array1::<f64>::zeros(2);
            for j in 0..n {
                if i != j {
                    let m = masses[j];
                    let r = positions.row(j).to_owned() - positions.row(i);
                    let r_norm_squared = r.map(|x| x * x).sum();
                    assert!(
                        r_norm_squared > 0.0,
                        "bodies cannot be at the same position."
                    );
                    let r_unit = r / r_norm_squared.sqrt();
                    a = a + (r_unit * G * m / r_norm_squared);
                }
            }
            buf.row_mut(i).assign(&a);
        }
        buf
    }
}

pub struct TraceShips {
    pub bodies: Vec<Body>,
    pub positions_at_t: Array3<f64>,
    pub time_step: f64,
    pub simulation_duration: f64,
    pub ship_positions: Array2<f64>,
    pub ship_velocities: Array2<f64>,
}

impl TraceShips {
    pub fn run(mut self) -> Array3<f64> {
        let n = self.ship_positions.len_of(Axis(0));
        let masses = Array::from_iter(self.bodies.iter().map(|b| b.mass));

        let mut ship_positions_at_t = Array3::zeros((0, n, 2));
        let mut time = 0.0;
        let mut i = 0;
        while time < self.simulation_duration {
            ship_positions_at_t
                .push(Axis(0), self.ship_positions.view())
                .unwrap();

            let accelerations = self.accelerations(
                &masses,
                &self.positions_at_t.slice(s![i, .., ..]).to_owned(),
            );
            self.ship_positions =
                self.ship_positions + self.ship_velocities.clone() * self.time_step;
            self.ship_velocities = self.ship_velocities + accelerations * self.time_step;

            time += self.time_step;
            i += 1;
        }

        ship_positions_at_t
    }

    fn accelerations(&self, masses: &Array1<f64>, positions: &Array2<f64>) -> Array2<f64> {
        let ships_len = self.ship_positions.len_of(Axis(0));
        let mut buf = Array::zeros((ships_len, 2));
        for ship_i in 0..ships_len {
            let mut a = Array1::<f64>::zeros(2);
            for mass_j in 0..masses.len() {
                let m = masses[mass_j];
                let r = positions.row(mass_j).to_owned() - self.ship_positions.row(ship_i);
                let r_norm_squared = r.map(|x| x * x).sum();
                assert!(
                    r_norm_squared > 0.0,
                    "bodies cannot be at the same position."
                );
                let r_unit = r / r_norm_squared.sqrt();
                a = a + (r_unit * G * m / r_norm_squared);
            }
            buf.row_mut(ship_i).assign(&a);
        }
        buf
    }
}
