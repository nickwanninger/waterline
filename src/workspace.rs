use crate::benchmark;
use std::path::*;

pub struct Workspace {
    pub dir: PathBuf,
    pub suites: Vec<Box<dyn benchmark::Suite>>,
}

impl Workspace {
    pub fn new(path: &str) -> Self {
        Self {
            dir: PathBuf::from(path),
            suites: vec![],
        }
    }

    pub fn add_suite<T>(&mut self, suite: T)
    where
        T: benchmark::Suite + 'static,
    {
        self.suites.push(Box::new(suite));
    }
}
