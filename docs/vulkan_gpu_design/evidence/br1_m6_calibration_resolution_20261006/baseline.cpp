// Evidence-only same-state fixture. The selector switch lives in a copied TU.
#include <QCoreApplication>
#include <QStandardPaths>
#include <chrono>
#include <cstdlib>
#include <cstring>
#include <dlfcn.h>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <vector>
#include <array>
#include <algorithm>
#include <pthread.h>
#include <pthread/qos.h>
#include <sys/resource.h>
#include "KisPageStore.h"
#include "KisPageStoreDiagnostics_p.h"
#include "KisPageWriteCoordinator_p.h"
#include "KisPageOwnerLedger.h"
#include "KisTiles3PageReplicaProvider.h"
#include "KisCpuResidentBinding_p.h"
#include "KisPageStoreReclamation_p.h"
#include "kis_image_config.h"

static const KisPageAccessRequirement cpu{KisPageAccessDomain::CpuRam, KisPageAccessKind::CpuPointer};
static KisPageKey key(int x) { return {{1}, {x, 0}}; }
static uint64_t now() { return std::chrono::duration_cast<std::chrono::nanoseconds>(
    std::chrono::steady_clock::now().time_since_epoch()).count(); }
using Control = void(*)(int);
static Control control = nullptr;
using CounterReset = void(*)();
using CounterGet = uint64_t(*)(int);
static CounterReset counterReset = nullptr;
static CounterGet counterGet = nullptr;
struct Observation {
    uint64_t wall = 0, setup = 0, close = 0, drain = 0, copied = 0;
    int handoffs = 0;
    KisPageBackingUsage before, after, closed;
};
static bool bytes(const void *p, size_t n, unsigned char value) {
    const auto *v = static_cast<const unsigned char *>(p);
    for (size_t i = 0; i < n; ++i) if (v[i] != value) return false;
    return true;
}
static bool cpuOnly(const KisPageBackingUsage &u) {
    for (const auto &b : u.buckets)
        if (b.live.umaShared || b.live.discreteVram || b.live.ssd || b.reserved.umaShared ||
            b.reserved.discreteVram || b.reserved.ssd) return false;
    return true;
}
static void usage(std::ostream &out, const KisPageBackingUsage &u) {
    out << '[';
    for (size_t i = 0; i < u.buckets.size(); ++i) {
        if (i) out << ',';
        const auto &b = u.buckets[i];
        out << '[' << b.live.cpuRam << ',' << b.reserved.cpuRam << ',' << b.peak.cpuRam << ']';
        if (b.live.umaShared || b.live.discreteVram || b.live.ssd || b.reserved.umaShared ||
            b.reserved.discreteVram || b.reserved.ssd) throw std::runtime_error("unexpected non-CPU domain");
    }
    out << ']';
}
static bool sample(const std::string &scenario, int pages, bool disabled, bool tight, int rounds,
                   Observation *observation = nullptr) {
    const auto start = now();
    constexpr size_t pageBytes = 64 * 64 * 4;
    auto completions = std::make_shared<KisCompletionRegistry>();
    auto provider = std::make_shared<KisTiles3PageReplicaProvider>();
    KisCpuResidentReplicaProviderConfig config;
    config.provider = {190}; config.providerEpoch = {1};
    config.budgetBytes = tight ? 2 * pages * pageBytes : 128 * 1024 * 1024;
    QString error;
    if (!provider->configure(config, completions, &error)) return false;
    KisSurfaceEpochState surface;
    surface.surface = {1}; surface.logicalPageExtent = QSize(64,64);
    surface.contentExtent = QRect(0,0,pages*64,64);
    surface.layoutRevision = surface.rowAlignment = surface.defaultPixelRevision = surface.extentRevision = 1;
    auto &f = surface.format;
    f.formatId = 198; f.colorModelId = "RGBA"; f.colorDepthId = "U8";
    f.profileFingerprint = "m6-opportunity"; f.channelOrder = "RGBA"; f.packing = "interleaved";
    f.defaultPixel = QByteArray(4, char(0x2a)); f.channelCount = 4; f.pixelStride = 4;
    f.pixelAlignment = 1; f.hasAlpha = true; f.alphaSemantic = KisSurfaceAlphaSemantic::Premultiplied;
    f.endianness = KisSurfaceEndianness::NativeEndian; f.codecVersion = 1;
    KisImageEpochSnapshot initial;
    initial.epoch = {1}; initial.surfaces = {surface};
    initial.graphRevision = initial.defaultPixelRevision = initial.extentRevision = initial.propertyRevision = 1;
    for (int x = 0; x < pages; ++x) initial.manifest.append({key(x), {1}});
    auto storeOwner = std::make_unique<KisPageStore>();
    auto &store = *storeOwner;
    if (!store.configure(initial, completions, 4, &error) || !store.registerReplicaProvider(provider)) return false;
    KisPageOwnerLedger ids;
    if (!ids.configure(completions)) return false;
    const auto descriptor = surface.allocationDescriptor();
    for (int x = 0; x < pages; ++x) {
        const KisPageVersion version{key(x), {1}};
        QVector<KisReplicaHandle> replicas;
        for (int i = 0; i < (scenario == "single" ? 1 : 2); ++i) {
            const auto op = provider->prepareWrite(ids.nextOperationId(), version, descriptor, cpu.domain,
                KisPageWriteMode::DiscardContents, KisPagePriority::Normal);
            if (!op.isValid() || op.status != KisPageRequestStatus::Ready) return false;
            auto binding = provider->cpuResidentBinding(op.replica);
            void *p = binding ? binding->acquireWrite(op.replica.allocationIdentity()) : nullptr;
            if (!p) return false;
            std::memset(p, 0x31, pageBytes); binding->releaseWrite(); replicas.append(op.replica);
        }
        if (!store.adoptInitialPage(version, descriptor, replicas[0], replicas.size() == 2 ?
            QVector<KisReplicaHandle>{replicas[1]} : QVector<KisReplicaHandle>{}, &error)) return false;
    }
    if (!store.finalizeInitialization(&error)) return false;
    std::vector<KisCapturedReadView> views;
    std::vector<KisCpuReadGuard> pins;
    std::vector<std::unique_ptr<KisReadLease>> leases;
    std::vector<KisCompletionTicket> tickets;
    views.reserve(rounds); pins.reserve(pages); leases.reserve(pages); tickets.reserve(pages);
    std::ostringstream operations;
    int phases[5] = {};
    std::unique_ptr<KisPageStoreDiagnosticRecorder> diagnostic;
    if (std::getenv("M6_MECHANISM")) {
        diagnostic = std::make_unique<KisPageStoreDiagnosticRecorder>(true, &store);
        diagnostic->setPhaseObserver([&](KisPageStoreDiagnosticPhase phase) {
            if (phase == KisPageStoreDiagnosticPhase::RecoverablePrepare) ++phases[0];
            if (phase == KisPageStoreDiagnosticPhase::RecoverablePrepared) ++phases[1];
            if (phase == KisPageStoreDiagnosticPhase::RecoverableInstall) ++phases[2];
            if (phase == KisPageStoreDiagnosticPhase::RecoverableInstalled) ++phases[3];
            if (phase == KisPageStoreDiagnosticPhase::RecoverableCleanup) ++phases[4];
        });
    }
    uint64_t firstBegin = 0, lastEnd = 0;
    uint64_t ledgerLookups = 0, coldPreparations = 0;
    for (int round = 0; round < rounds; ++round) {
        views.push_back(store.captureReadView());
        std::vector<const void *> addresses;
        for (int x = 0; x < pages; ++x) {
            auto r = views.back().readResidentPage(key(x));
            if (!r.isValid()) return false;
            addresses.push_back(r.data());
            if (scenario == "native-pin") pins.push_back(std::move(r));
            if (scenario == "generic-lease" || scenario == "last-use") {
                auto request = store.acquireRead(key(x), {}, cpu, KisPagePriority::Normal);
                auto lease = std::make_unique<KisReadLease>(store.resolve(request, request.readiness));
                if (!lease->isValid()) return false;
                if (scenario == "last-use") {
                    auto ticket = completions->allocatePending(completions->registerSource(KisCompletionDomain::HostLogical));
                    if (!ticket.isValid()) return false;
                    store.release(std::move(*lease), ticket); tickets.push_back(ticket);
                } else leases.push_back(std::move(lease));
            }
        }
        const auto workBefore = provider->payloadWork();
        const auto before = provider->memoryUsage().committedBytes;
        const auto budgetBefore = store.backingUsage();
        if (control) control(disabled);
        if (counterReset) counterReset();
        int hits = 0;
        const auto begin = now();
        if (!round) firstBegin = begin;
        const auto tx = store.beginCurrentTransaction();
        auto mutation = store.beginMutation(tx, &error);
        bool success = true; // The original beginWrite guard validates the session.
        for (int x = 0; x < pages && success; ++x) {
            auto guard = mutation.beginWrite(key(x), KisPageWriteMode::PreserveContents, &error);
            success = guard.isValid();
            if (success) {
                hits += guard.data() == addresses[x];
                std::memset(guard.data(), 0x73 + round, pageBytes);
            }
        }
        if (success) success = mutation.seal(&error);
        if (success) success = store.commit(tx, store.preparedPages(tx)).isValid();
        const auto end = now(); lastEnd = end;
        if (counterGet) { ledgerLookups += counterGet(0); coldPreparations += counterGet(1); }
        if (control) control(0);
        const auto after = provider->memoryUsage().committedBytes;
        const auto workAfter = provider->payloadWork();
        const auto budgetAfter = store.backingUsage();
        const bool expectedHit = !disabled && scenario == "hit" && round == 0;
        const bool expectedRefusal = tight && scenario != "single" && !expectedHit;
        if (success == expectedRefusal) { std::cerr << "unexpected completion " << error.toStdString(); return false; }
        if (!success && (!mutation.cancel() || !store.abort(tx))) return false;
        const uint64_t copied = workAfter.nativeDuplicateBytes - workBefore.nativeDuplicateBytes;
        if (success) {
            const uint64_t delta = expectedHit ? 0 : pages * pageBytes;
            if (hits != (expectedHit ? pages : 0) || after != before + delta || copied != delta ||
                workAfter.nativeForegroundCopyBytes - workBefore.nativeForegroundCopyBytes != delta ||
                workAfter.defaultInitializedBytes != workBefore.defaultInitializedBytes ||
                workAfter.payloadInitializedBytes != workBefore.payloadInitializedBytes) return false;
        }
        auto current = store.captureReadView();
        for (int x = 0; x < pages; ++x) {
            auto old = views.back().readResidentPage(key(x)); auto next = current.readResidentPage(key(x));
            if (!old.isValid() || !next.isValid() || !bytes(old.data(), pageBytes, round ? 0x72 + round : 0x31) ||
                !bytes(next.data(), pageBytes, success ? 0x73 + round : 0x31)) return false;
        }
        if (observation) {
            if (rounds != 1 || tight || !success) return false;
            observation->wall = end - begin;
            observation->handoffs = hits;
            observation->copied = copied;
            observation->before = budgetBefore;
            observation->after = budgetAfter;
        } else {
        if (round) operations << ',';
        operations << "{\"wall_ns\":" << end-begin << ",\"completed\":" << success
            << ",\"handoffs\":" << hits << ",\"before\":" << before << ",\"after\":" << after
            << ",\"copy_bytes\":" << copied << ",\"budget_before\":";
        usage(operations, budgetBefore); operations << ",\"budget_after\":"; usage(operations, budgetAfter);
        operations << '}';
        }
        if (!success) break;
    }
    diagnostic.reset();
    pins.clear();
    for (auto &lease : leases) store.release(std::move(*lease));
    leases.clear();
    for (auto ticket : tickets) {
        if (!completions->complete(ticket, KisCompletionStatus::Succeeded)) return false;
        store.acknowledgeLastUse(completions->verifyTerminal(ticket));
    }
    if (store.sessionStats().pendingLastUses) return false;
    views.clear();
    if (!store.closeSession(&error) || provider->memoryUsage().committedBytes) return false;
    const auto closedUsage = store.backingUsage();
    for (size_t i = 0; i < closedUsage.buckets.size(); ++i) {
        const auto &b = closedUsage.buckets[i];
        if (b.reserved.cpuRam || (i != size_t(KisBackingBudgetClass::MetadataArena) && b.live.cpuRam)) return false;
    }
    storeOwner.reset(); // Store-owned metadata must be destroyed before the drain endpoint.
    const auto closed = now();
    kisDrainPageStoreReclamation();
    const auto drained = now();
    if (observation) {
        observation->setup = firstBegin - start;
        observation->close = closed - lastEnd;
        observation->drain = drained - closed;
        observation->closed = closedUsage;
        if (!cpuOnly(observation->before) || !cpuOnly(observation->after) || !cpuOnly(observation->closed))
            return false;
        if (counterGet || diagnostic || phases[0] || phases[1] || phases[2] || phases[3] || phases[4])
            return false; // Window measurements must have no enabled mechanism recorder.
        return true;
    }
    std::cout << "{\"case\":\"" << scenario << "\",\"K\":" << pages << ",\"disabled\":" << disabled
        << ",\"tight\":" << tight << ",\"rounds\":" << rounds << ",\"switch_loaded\":" << bool(control)
        << ",\"setup_ns\":" << firstBegin-start << ",\"validation_close_ns\":" << closed-lastEnd
        << ",\"drain_ns\":" << drained-closed << ",\"complete_ns\":" << drained-start
        << ",\"provider_after_close\":0,\"phases\":[" << phases[0] << ',' << phases[1]
        << ',' << phases[2] << ',' << phases[3] << ',' << phases[4] << "],\"closed_budget\":";
    usage(std::cout, closedUsage);
    std::cout << ",\"ledger_lookups\":" << ledgerLookups << ",\"cold_preparations\":" << coldPreparations
        << ",\"counter_loaded\":" << bool(counterGet)
        << ",\"operations\":[" << operations.str() << "]}\n";
    return true;
}
int main(int argc, char **argv) {
    QCoreApplication app(argc, argv);
    app.setApplicationName("codex-m6-opportunity-baseline"); QStandardPaths::setTestModeEnabled(true);
    { KisImageConfig c(false); c.setMemoryHardLimitPercent(20); c.setMemoryPoolLimitPercent(0); }
    control = reinterpret_cast<Control>(dlsym(RTLD_DEFAULT, "m6EvidenceControl"));
    counterReset = reinterpret_cast<CounterReset>(dlsym(RTLD_DEFAULT, "m6EvidenceCounterReset"));
    counterGet = reinterpret_cast<CounterGet>(dlsym(RTLD_DEFAULT, "m6EvidenceCounterGet"));
    qos_class_t priorQos = QOS_CLASS_UNSPECIFIED;
    if (pthread_get_qos_class_np(pthread_self(), &priorQos, nullptr)) return 11;
    const char *requestedQos = std::getenv("M6_DIAGNOSTIC_QOS");
    if (requestedQos && std::strcmp(requestedQos, "user-initiated") == 0) {
        if (pthread_set_qos_class_self_np(QOS_CLASS_USER_INITIATED, 0)) return 11;
    } else if (requestedQos && std::strcmp(requestedQos, "unchanged") != 0) return 13;
    qos_class_t effectiveQos = QOS_CLASS_UNSPECIFIED;
    if (pthread_get_qos_class_np(pthread_self(), &effectiveQos, nullptr)) return 12;
    if (requestedQos && std::strcmp(requestedQos, "user-initiated") == 0
        && effectiveQos != QOS_CLASS_USER_INITIATED) return 12;
    std::cout << "ENV {\"qos_before\":" << int(priorQos)
        << ",\"qos_after\":" << int(effectiveQos)
        << ",\"nice\":" << getpriority(PRIO_PROCESS, 0) << "}\n";
    rusage windowBefore{};
    if (getrusage(RUSAGE_SELF, &windowBefore)) return 14;
    if (argc == 9) {
        const std::string mode = argv[1], scenario = argv[2];
        const int pages = std::stoi(argv[3]), disabled = std::stoi(argv[4]);
        const uint64_t minimumNs = std::stoull(argv[5]);
        const int warmup = std::stoi(argv[6]), order = std::stoi(argv[7]), minimumOperations = std::stoi(argv[8]);
        const bool paired = mode == "paired";
        if ((mode != "fixed" && !paired) || (paired && !control) || (disabled && !control)
            || counterGet || std::getenv("M6_MECHANISM")) return 1;
        struct Arm {
            std::vector<uint64_t> wall;
            uint64_t total = 0, setup = 0, close = 0, drain = 0, copies = 0, handoffs = 0;
            Observation first, last;
            KisPageBackingUsage observed;
            void add(const Observation &o) {
                if (wall.empty()) first = o;
                last = o; wall.push_back(o.wall); total += o.wall;
                setup += o.setup; close += o.close; drain += o.drain;
                copies += o.copied; handoffs += o.handoffs;
                for (size_t i = 0; i < observed.buckets.size(); ++i) {
                    auto &b = observed.buckets[i];
                    for (const auto *u : {&o.before, &o.after, &o.closed}) {
                        b.live.cpuRam = std::max(b.live.cpuRam, u->buckets[i].live.cpuRam);
                        b.reserved.cpuRam = std::max(b.reserved.cpuRam, u->buckets[i].reserved.cpuRam);
                        b.peak.cpuRam = std::max(b.peak.cpuRam, u->buckets[i].peak.cpuRam);
                    }
                }
            }
        };
        std::array<Arm, 2> arms;
        try {
            for (int i = 0; i < warmup; ++i) for (int a = 0; a < (paired ? 2 : 1); ++a) {
                Observation o;
                if (!sample(scenario, pages, paired ? bool(a) : bool(disabled), false, 1, &o)) return 2;
            }
            size_t iteration = 0;
            do {
                for (int a = 0; a < (paired ? 2 : 1); ++a) {
                    const int arm = paired ? ((order + int(iteration) + a) & 1) : disabled;
                    Observation o;
                    if (!sample(scenario, pages, bool(arm), false, 1, &o)) return 2;
                    arms[arm].add(o);
                }
                if (++iteration > 100000) throw std::runtime_error("fixed safety bound reached");
            } while (arms[disabled].total < minimumNs || arms[disabled].wall.size() < size_t(minimumOperations)
                     || (paired && (arms[1-disabled].total < minimumNs
                                    || arms[1-disabled].wall.size() < size_t(minimumOperations))));
            std::cout << "WINDOW {\"paired\":" << paired << ",\"switch_loaded\":" << bool(control)
                << ",\"case\":\"" << scenario << "\",\"K\":" << pages << ",\"minimum_ns\":" << minimumNs
                << ",\"warmup\":" << warmup << ",\"arms\":[";
            bool comma = false;
            for (int a = 0; a < 2; ++a) if (!arms[a].wall.empty()) {
                if (comma) std::cout << ','; comma = true;
                const auto &s = arms[a];
                std::cout << "{\"disabled\":" << a << ",\"completed\":" << s.wall.size()
                    << ",\"wall_ns\":" << s.total << ",\"setup_ns\":" << s.setup
                    << ",\"validation_close_ns\":" << s.close << ",\"drain_ns\":" << s.drain
                    << ",\"copy_bytes\":" << s.copies << ",\"handoffs\":" << s.handoffs
                    << ",\"first_budget_before\":"; usage(std::cout, s.first.before);
                std::cout << ",\"last_budget_after\":"; usage(std::cout, s.last.after);
                std::cout << ",\"last_closed_budget\":"; usage(std::cout, s.last.closed);
                std::cout << ",\"observed_class_maxima\":"; usage(std::cout, s.observed);
                std::cout << ",\"operation_ns\":[";
                for (size_t i = 0; i < s.wall.size(); ++i) { if (i) std::cout << ','; std::cout << s.wall[i]; }
                std::cout << "]}";
            }
            rusage windowAfter{};
            if (getrusage(RUSAGE_SELF, &windowAfter)) return 14;
            std::cout << "]}\nCONTEXT {\"voluntary_switches\":"
                << windowAfter.ru_nvcsw - windowBefore.ru_nvcsw
                << ",\"involuntary_switches\":" << windowAfter.ru_nivcsw - windowBefore.ru_nivcsw
                << ",\"minor_faults\":" << windowAfter.ru_minflt - windowBefore.ru_minflt
                << ",\"major_faults\":" << windowAfter.ru_majflt - windowBefore.ru_majflt
                << "}\nall_checks_passed=1\n";
        } catch (const std::exception &e) { std::cerr << e.what() << '\n'; return 3; }
        return 0;
    }
    if (argc != 7) return 1;
    const std::string scenario = argv[1];
    const int pages = std::stoi(argv[2]), disabled = std::stoi(argv[3]), repeats = std::stoi(argv[4]);
    const bool tight = std::stoi(argv[5]); const int rounds = std::stoi(argv[6]);
    if (disabled && !control) return 1;
    try {
        for (int i = 0; i < repeats; ++i) if (!sample(scenario, pages, disabled, tight, rounds)) {
            std::cerr << "sample_failed=" << i << '\n'; return 2;
        }
    } catch (const std::exception &e) { std::cerr << e.what() << '\n'; return 3; }
    std::cout << "all_checks_passed=1\n";
}
