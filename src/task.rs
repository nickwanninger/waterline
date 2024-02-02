/// A Task in the waterline system. This is effectively a thin wrapper around a simple shell
/// command. A TaskRunner takes in a set of these tasks, and
pub struct Task {
    pub args: Vec<String>,
}

impl Task {
    pub fn new(args: Vec<String>) -> Self {
        Self { args }
    }
}

// just turn task![a, b] into vec![a.into(), b.into()]

#[macro_export]
macro_rules! task {
    ($($arg:expr),* $(,)?) => {
        $crate::task::Task::new(vec![$($arg.into()),*])
    }
}
