use std::path::*;


pub struct Workspace {
    pub dir: PathBuf,
}


impl Workspace {
    pub fn new(path: &str) -> Self {
        Self {
            dir: PathBuf::from(path),
        }
    }

}
