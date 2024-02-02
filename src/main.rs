use waterline::benchmark;

fn main() {
    let mut ws = waterline::Workspace::new("bench");

    ws.add_suite(benchmark::Polybench {});
}
