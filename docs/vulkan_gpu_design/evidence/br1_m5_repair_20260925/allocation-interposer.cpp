// Audit-only macOS allocator interposition; no production instrumentation.
#include <cstdlib>
#include <cstddef>
#include <execinfo.h>
struct Counts { size_t allocations, bytes, frees; };
static thread_local bool active;
static thread_local Counts counts;
static thread_local void *firstStack[32];
static thread_local int stackSize;
extern "C" void auditStart() { counts = {}; stackSize = 0; active = true; }
extern "C" Counts auditStop() { active = false; return counts; }
extern "C" void auditStack() { backtrace_symbols_fd(firstStack, stackSize, 2); }
static void allocated(size_t bytes) {
    if (!active) return;
    ++counts.allocations; counts.bytes += bytes;
    if (!stackSize) { active = false; stackSize = backtrace(firstStack, 32); active = true; }
}
static void *trackedMalloc(size_t n) { allocated(n); return malloc(n); }
static void *trackedCalloc(size_t n, size_t s) { allocated(n*s); return calloc(n,s); }
static void *trackedRealloc(void *p, size_t n) { allocated(n); return realloc(p,n); }
static int trackedMemalign(void **p, size_t a, size_t n) { allocated(n); return posix_memalign(p,a,n); }
static void *trackedAligned(size_t a, size_t n) { allocated(n); return aligned_alloc(a,n); }
static void trackedFree(void *p) { if (active && p) ++counts.frees; free(p); }
#define INTERPOSE(replacement, original) \
__attribute__((used)) static const struct { const void *r; const void *o; } pair_##original \
__attribute__((section("__DATA,__interpose"))) = {(const void *)&replacement, (const void *)&original};
INTERPOSE(trackedMalloc, malloc)
INTERPOSE(trackedCalloc, calloc)
INTERPOSE(trackedRealloc, realloc)
INTERPOSE(trackedMemalign, posix_memalign)
INTERPOSE(trackedAligned, aligned_alloc)
INTERPOSE(trackedFree, free)
