use std::collections::HashMap;

pub struct CompileConfiguration {
    pub name: String,
    map: HashMap<String, String>,
}

impl CompileConfiguration {
    pub fn new(name: &str) -> Self {
        Self {
            name: name.into(),
            map: HashMap::new(),
        }
    }

    pub fn set<T: Into<String>>(&mut self, key: T, value: T) {
        self.map.insert(key.into(), value.into());
    }

    pub fn get<T: Into<String>>(&self, key: T) -> Option<String> {
        match self.map.get(&key.into()) {
            Some(v) => Some(v.clone()),
            None => None,
        }
    }
}
