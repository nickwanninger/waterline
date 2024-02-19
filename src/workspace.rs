use crate::{benchmark, CompileConfiguration};
use std::path::*;

pub struct Workspace {
    pub dir: PathBuf,
    pub suites: Vec<Box<dyn benchmark::Suite>>,
    pub compile_configs: Vec<CompileConfiguration>,
}

impl Workspace {
    pub fn new(path: &str) -> Self {
        Self {
            dir: PathBuf::from(path),
            suites: vec![],
            compile_configs: vec![],
        }
    }

    pub fn add_suite<T>(&mut self, suite: T)
    where
        T: benchmark::Suite + 'static,
    {
        self.suites.push(Box::new(suite));
    }

    /// Instruct all suites to acquire their source code
    pub async fn acquire(&mut self) {
        for suite in &mut self.suites {
            suite.acquire().await;
        }
    }

    /// Iterate over every suite, and instruct it to configure a compilation.
    /// This will in turn add benchmarks
    pub async fn add_config(&mut self, _config: CompileConfiguration) {}
}
