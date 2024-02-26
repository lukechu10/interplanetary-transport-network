use log::{error, info};
use simple_logger::SimpleLogger;

pub mod part1;
pub mod part1a;
pub mod part1b;
pub mod tracer;

fn main() {
    SimpleLogger::new().init().unwrap();

    let Some(arg) = std::env::args().nth(1) else {
        error!("missing argument. Usage: cargo run (--release) <simulation>");
        return;
    };

    info!("running simulation `{arg}`");

    match arg.as_str() {
        "part1" => part1::start(),
        "part1a" => part1a::start(),
        "part1b" => part1b::start(),
        _ => panic!("unknown argument"),
    }
}
