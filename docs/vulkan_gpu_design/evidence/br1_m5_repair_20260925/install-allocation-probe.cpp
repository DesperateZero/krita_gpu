#include <QCoreApplication>
#include <QStandardPaths>
#include <QHash>
#include <iostream>
#include <new>
#include "KisPageMetadataArena_p.h"
#include "KisPageMetadataIndex_p.h"
#include "KisTiledDataManagerPageStoreBackend.h"
#include "KisPageStoreDiagnostics_p.h"
#include "KisPageStoreIteratorReadScope_p.h"
#include "kis_image_config.h"
struct Counts { size_t allocations, bytes, frees; };
extern "C" void auditStart();
extern "C" Counts auditStop();
extern "C" void auditStack();
static bool failedAllocation;
void *operator new(size_t n) {
    if (failedAllocation) { failedAllocation = false; throw std::bad_alloc(); }
    if (void *p = malloc(n ? n : 1)) return p;
    throw std::bad_alloc();
}
void *operator new[](size_t n) { return ::operator new(n); }
void operator delete(void *p) noexcept { free(p); }
void operator delete[](void *p) noexcept { free(p); }
static bool report(const char *label, Counts c) {
    std::cout << label << " allocations=" << c.allocations << " bytes=" << c.bytes
              << " frees=" << c.frees << std::endl;
    if (c.allocations) auditStack();
    return c.allocations == 0 && c.frees == 0;
}
// Reuse the production coordinator's existing reference-test friend boundary.
class KisPageStoreReferenceTest { public: static int run(int argc, char **argv); };
int KisPageStoreReferenceTest::run(int argc, char **argv) {
    QCoreApplication app(argc, argv);
    app.setApplicationName("codex-br1-m5-repaired-install-probe");
    QStandardPaths::setTestModeEnabled(true);
    { KisImageConfig c(false); c.setMemoryHardLimitPercent(20); c.setMemoryPoolLimitPercent(0); }
    // Positive control in shared Qt code verifies the interposer is active.
    QHash<quint64,quint64> positive;
    auditStart(); positive.reserve(64); for (quint64 i=0;i<64;++i) positive.insert(i,i);
    auto control = auditStop();
    std::cout << "positive_control_allocations=" << control.allocations << std::endl;
    if (!control.allocations) return 2;
    using Index=KisShardSlotIndex<KisPageVersion,KisVersionSlotId>;
    Index index;
    for (int batch : {1,63,64,65,127,128,129,511,512,513}) {
        if (!index.prepareCapacity(index.requiredCapacity(batch))) return 3;
        auto token=index.reserveInsertions(batch);
        const int start=int(index.size());
        auditStart();
        bool ok=true;
        for (int i=0;i<batch;++i) ok &= index.insertReserved(&token, {{{1},{start+i,0}},{1}}, {quint32(start+i+1),1});
        auto c=auditStop();
        if (!ok || !report("exact_index_insert",c)) return 4;
    }
    const auto before=index.statistics();
    failedAllocation=true;
    if (index.prepareCapacity(index.requiredCapacity(qsizetype(before.capacity))) || failedAllocation) return 5;
    if (index.statistics().capacity!=before.capacity || index.size()!=qsizetype(before.entries)) return 6;
    for (quint32 i=0;i<before.entries;++i) if (!index.findExact({{{1},{qint32(i),0}},{1}})) return 7;
    std::cout << "prepare_bad_alloc_preserves_index=1" << std::endl;

    KisShardSlotIndex<KisReplicaPhysicalSlotIdentity,KisReplicaSlotId> physical;
    if (!physical.prepareCapacity(1024)) return 8;
    auto physicalToken=physical.reserveInsertions(1024);
    auditStart();
    bool physicalOk=true;
    for (quint32 i=0;i<1024;++i)
        physicalOk &= physical.insertReserved(&physicalToken,{{1},{1},i+1},{i+1,1});
    for (quint32 i=0;i<1024;i+=2)
        physicalOk &= physical.eraseExact({{1},{1},i+1},{i+1,1});
    auto physicalCounts=auditStop();
    if (!physicalOk || !report("physical_index_insert_erase",physicalCounts)) return 9;

    for (int pages : {1,64,65,129}) {
        KisTiledDataManagerPageStoreBackend backend;
        quint8 pixel=0;
        QString error;
        if (!backend.configure(1,&pixel,&error)) return 10;
        // Register real default pages, so default commits install descriptors
        // and new metadata index entries rather than only a surface header.
        for (int i=0;i<pages;++i) {
            KisPageStoreReadPage read(backend.store(),backend.captureReadView(),{backend.surface(),{i,0}},&error);
            if (!read.data()) return 11;
        }
        bool ok=true; int observed=0; Counts total{};
        KisPageStoreDiagnosticRecorder recorder(true,backend.store());
        recorder.setPhaseObserver([&](KisPageStoreDiagnosticPhase phase) {
            if (phase==KisPageStoreDiagnosticPhase::CommitMetadataApply) auditStart();
            else if (phase==KisPageStoreDiagnosticPhase::CommitRootPublication) {
                auto c=auditStop(); ++observed;
                total.allocations+=c.allocations; total.bytes+=c.bytes; total.frees+=c.frees;
                ok &= report("root_metadata_descriptor_install",c);
            } else if (phase==KisPageStoreDiagnosticPhase::CommitCleanup) auditStop();
        });
        for (int revision=1;revision<=4;++revision)
            if (!backend.setDefaultPixel(QByteArray(1,char(revision)),&error)) return 12;
        recorder.setPhaseObserver({});
        std::cout << "pages="<<pages<<" observed_installs="<<observed<<std::endl;
        if (!ok || observed!=4 || total.allocations) return 13;
    }
    // Restore additions also consume reserved storage; defer candidate
    // destruction exactly as the production publication owner does.
    KisPageMetadataCoordinator metadata;
    if (!metadata.configure(1)) return 20;
    QVector<KisPageTransition> restores;
    for (int i=0;i<129;++i) {
        KisPageVersion v{{{1},{i,0}},{1},1};
        KisPageStateSnapshot s;
        s.key=v.key;s.publishedEpoch={1};s.publishedGeneration={1};s.publishedDefaultPixelRevision=1;s.nextGeneration={2};
        KisPageVersionStateSnapshot r;r.version=v;r.publication=KisPagePublicationState::Published;s.versions.append(r);
        if (!metadata.registerPage(s)) return 21;
        KisPageTransition t;t.kind=KisPageTransitionKind::RestoreCommittedVersion;t.version={v.key,{1},2};t.imageEpoch={2};restores.append(t);
    }
    auto cancelled=metadata.prepareRestoration({2},restores); if (!cancelled.isValid()) return 22;
    auto prepared=metadata.prepareRestoration({2},restores); if (!prepared.isValid()) return 23;
    cancelled={};
    KisPageMetadataCoordinator::DeferredPublicationCleanup cleanup;
    auditStart();
    const bool restored=metadata.installPublication(std::move(prepared),{},{2},nullptr,nullptr,&cleanup);
    auto c=auditStop();
    if (!restored || !report("restore_additions_install",c)) return 24;
    if (metadata.footprint().exactVersionIndex.outstandingReservations) return 25;
    while (!cleanup.isEmpty()) cleanup.clearBatch(32);
    std::cout << "all_checks_passed=1" << std::endl;
    return 0;
}

int main(int argc, char **argv) { return KisPageStoreReferenceTest::run(argc,argv); }
