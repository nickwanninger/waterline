#![allow(unused_macros)]

pub mod workspace;

pub mod suites;
pub mod benchmark;
pub mod task;


// Re-export important parts of the waterline library.
pub use workspace::Workspace;
pub use benchmark::Suite;
pub use benchmark::Benchmark;
pub use task::*;
