use nalgebra::Vector3;

use crate::consts::G;

/// Represents a body that produces a gravitational field.
pub struct Body {
    /// Mass in kg.
    pub mass: f64,
    // Phase space coordinates. Units are SI.
    pub pos: Vector3<f64>,
    pub momentum: Vector3<f64>,
}

/// Trace all the bodies in the simulation and save the results of their positions.
pub struct TracerStep1 {
    /// List of bodies in the simulation. Should start with initial conditons.
    pub bodies: Vec<Body>,
    /// Simulation time step in seconds.
    pub time_step: f64,
    /// Simulation duration in seconds.
    pub simulation_duration: f64,
}

impl TracerStep1 {
    pub fn run(self) -> Vec<Vec<Vector3<f64>>> {
        let mut time = 0.0;
        let mut positions = self.bodies.iter().map(|b| b.pos).collect::<Vec<_>>();
        let mut momenta = self.bodies.iter().map(|b| b.momentum).collect::<Vec<_>>();
        // Temporary buffer for storing the previous position.
        let mut prev_positions = positions.clone();

        // Buffer for storing the positions of the bodies at each time step.
        let mut positions_buf = vec![positions.clone()];

        while time < self.simulation_duration {
            self.update_newton(&prev_positions, &mut positions, &mut momenta);
            prev_positions = positions.clone();
            positions_buf.push(positions.clone());
            time += self.time_step;
        }

        positions_buf
    }

    /// Preform one time step of simulation. Uses Newton's laws.
    pub fn update_newton(
        &self,
        prev_positions: &[Vector3<f64>],
        positions: &mut Vec<Vector3<f64>>,
        momenta: &mut Vec<Vector3<f64>>,
    ) {
        for n in 0..self.bodies.len() {
            let mass = self.bodies[n].mass;
            // Calculate the gravitational field at the position of body n.
            let mut field = Vector3::zeros();
            for m in 0..self.bodies.len() {
                if n != m {
                    let m_mass = self.bodies[m].mass;
                    let r = prev_positions[m] - prev_positions[n];
                    let r_norm = r.norm();
                    assert!(r_norm > 0.0, "Bodies cannot be at the same position.");
                    let r_unit = r.normalize();
                    field += r_unit * G * m_mass / r_norm.powi(2);
                }
            }
            let force = field * mass;
            let dx = momenta[n] / mass * self.time_step;
            let dp = force * self.time_step;
            // Update the position and momentum of body n.
            positions[n] = prev_positions[n] + dx;
            momenta[n] += dp;
        }
    }
}
