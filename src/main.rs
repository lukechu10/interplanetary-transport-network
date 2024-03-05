use log::{error, info};
use simple_logger::SimpleLogger;

pub mod halo_orbits;
pub mod halo_orbits_compute;
pub mod leo_to_moon;
pub mod leo_to_moon_compute;
pub mod leo_to_moon_no_sun;
pub mod leo_to_moon_test;
pub mod manifolds_earth_moon;
pub mod manifolds_sun_earth;
pub mod multi_planet;
pub mod single_planet;
pub mod tracer;

fn main() {
    SimpleLogger::new().init().unwrap();

    let Some(arg) = std::env::args().nth(1) else {
        error!("missing argument. Usage: cargo run (--release) <simulation>");
        return;
    };

    info!("running simulation `{arg}`");

    match arg.as_str() {
        "single_planet" => single_planet::start(),
        "multi_planet" => multi_planet::start(),
        "leo_to_moon" => leo_to_moon::start(),
        "leo_to_moon_test" => leo_to_moon_test::start(),
        "leo_to_moon_compute" => leo_to_moon_compute::start(),
        "leo_to_moon_no_sun" => leo_to_moon_no_sun::start(),
        "halo_orbits_earth_moon" => halo_orbits::start_earth_moon(),
        "halo_orbits_sun_earth" => halo_orbits::start_sun_earth(),
        "halo_orbits_compute_earth_moon" => halo_orbits_compute::start_earth_moon(),
        "halo_orbits_compute_sun_earth" => halo_orbits_compute::start_sun_earth(),
        "manifolds_earth_moon" => manifolds_earth_moon::start(),
        "manifolds_sun_earth" => manifolds_sun_earth::start(),
        _ => panic!("unknown argument"),
    }
}
