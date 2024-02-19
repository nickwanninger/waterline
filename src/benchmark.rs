use async_trait::async_trait;

pub trait Benchmark {}

#[async_trait]
pub trait Suite {
    async fn acquire(&self);
}

pub struct Polybench;



#[async_trait]
impl Suite for Polybench {
    async fn acquire(&self) {}
}
