#include "support.h"

volatile int embench_count = 0;
// This file has been modified to run the benchmark 10000 times.

__attribute__((noopt)) int __attribute__((used))
main(int argc __attribute__((unused)), char *argv[] __attribute__((unused))) {
  int i;
  volatile int result;
  int correct;

  initialise_board();
  initialise_benchmark();
  warm_caches(ITERATIONS);

  for (volatile int i = 0; i < ITERATIONS; i++) {
    start_trigger();
    result = benchmark();
    correct = verify_benchmark(result);
    asm volatile("" : : : "memory");
    stop_trigger();
  }

  return (!correct);
}