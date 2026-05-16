#include <algorithm>
#include <chrono>
#include <cstdlib>
#include <iostream>
#include <random>
#include <sys/mman.h>
#include <unistd.h>
#include <vector>
using namespace std;

void *allocate_memory(size_t bytes, bool use_hugepages) {
  int flags = MAP_ANONYMOUS | MAP_PRIVATE;

  if (use_hugepages) {
    // Align size to 2MB
    size_t huge_size = 2 * 1024 * 1024;
    bytes = ((bytes + huge_size - 1) / huge_size) * huge_size;
  }

  void *ptr = mmap(nullptr, bytes, PROT_READ | PROT_WRITE, flags, -1, 0);
  if (ptr == MAP_FAILED) {
    perror("mmap failed");
    exit(EXIT_FAILURE);
  }

  if (use_hugepages) {
    // Use madvise to inform THP to promote this mapping, rather than forcing
    // hardware HugeTLBfs
#ifdef __linux__
    if (madvise(ptr, bytes, MADV_HUGEPAGE) != 0) {
      perror("madvise MADV_HUGEPAGE failed");
    }
#else
    cerr << "Warning: HugePages (MADV_HUGEPAGE) are only supported on Linux.\n";
#endif
  }
  return ptr;
}

void execute_workload(size_t total_mb, bool is_random, bool use_hugepages) {
  size_t bytes = total_mb * 1024 * 1024;
  char *buffer = static_cast<char *>(allocate_memory(bytes, use_hugepages));

  // Determine stride: standard page vs huge page
  size_t stride = use_hugepages ? (2 * 1024 * 1024) : 4096;
  size_t num_touches = bytes / stride;

  // Generate page offsets
  vector<size_t> offsets(num_touches);
  for (size_t i = 0; i < num_touches; ++i)
    offsets[i] = i * stride;

  if (is_random) {
    shuffle(offsets.begin(), offsets.end(), mt19937{random_device{}()});
  }

  auto start = chrono::high_resolution_clock::now();
  for (size_t offset : offsets) {
    buffer[offset] = 'A'; // Trigger the page fault
  }
  auto end = chrono::high_resolution_clock::now();
  chrono::duration<double> elapsed = end - start;

  cout << "Workload complete: " << total_mb << " MB, "
       << (is_random ? "Random" : "Sequential") << ", "
       << (use_hugepages ? "HugePages" : "Normal") << "\n";
  cout << "Elapsed time: " << elapsed.count() << " seconds\n";

  if (munmap(buffer, bytes) != 0) {
    perror("munmap failed");
    exit(EXIT_FAILURE);
  }
}

int main(int argc, char **argv) {
  if (argc < 4) {
    cerr << "Usage: ./workload <MB> <random(0/1)> <hugepages(0/1)>\n";
    return EXIT_FAILURE;
  }

  size_t mb = stoull(argv[1]);
  bool is_random = stoi(argv[2]) == 1;
  bool use_hugepages = stoi(argv[3]) == 1;

  execute_workload(mb, is_random, use_hugepages);
  return EXIT_SUCCESS;
}
