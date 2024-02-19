#[tokio::main]
async fn main() {
    let mut ws = waterline::Workspace::new("bench");

    ws.add_suite(waterline::Polybench {});

    ws.acquire().await;
}
