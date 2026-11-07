#include <QCoreApplication>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QStandardPaths>
#include <cstdio>
#include <cstring>
#include <thread>
#include "tiles3/kis_tiled_data_manager.h"
#include "pagestore/KisTiledDataManagerPageStoreBackend.h"
#include "pagestore/KisPageStoreDiagnostics_p.h"
#include "pagestore/KisPageStoreIteratorReadScope_p.h"
#include "KisStrokeJobFailureContext.h"
#include "kis_image_config.h"

// Use the existing test friendship; the probe does not modify product code.
class KisTiledDataManagerTest {
public:
    static auto backend(KisTiledDataManager &dm) { return dm.m_pageStoreBackend; }
};
static int errors = 0, violations = 0, scenarios = 0, observations = 0;
static void check(bool condition, const char *what)
{
    if (!condition) { ++errors; std::fprintf(stderr, "CONTROL FAILED: %s\n", what); }
}
static QJsonArray rect(const QRect &r) { return {r.x(), r.y(), r.width(), r.height()}; }
static void emitRow(QJsonObject row)
{
    ++observations;
    std::puts(QJsonDocument(row).toJson(QJsonDocument::Compact).constData());
}
static int readTile(const KisTileSP &tile)
{
    if (!tile || !tile->lockForRead()) { check(false, "read capability"); return -1; }
    const int result = tile->data()[0];
    tile->unlockForRead();
    return result;
}
static int exact(KisTiledDataManagerPageStoreBackend *backend,
                 const KisCapturedReadView &view, int column = 0)
{
    auto read = view.readResidentPage({backend->surface(), {column, 0}});
    if (!read.isValid()) { check(false, "exact read"); return -1; }
    return *static_cast<const quint8 *>(read.data());
}
static QRect extent(KisTiledDataManagerPageStoreBackend *backend, const KisCapturedReadView &view)
{
    KisSurfaceEpochState state;
    check(view.resolveSurfaceState(backend->surface(), &state), "surface selection");
    return state.contentExtent;
}
static void publicationCase(int bpp, bool packed, bool warm, bool hold)
{
    ++scenarios;
    const QByteArray blank(bpp, 0), old(bpp, char(0x31)), value(bpp, char(0x61));
    KisTiledDataManager dm(bpp, reinterpret_cast<const quint8 *>(blank.constData()));
    if (warm) dm.writeBytes(reinterpret_cast<const quint8 *>(old.constData()), 0, 0, 1, 1);
    auto *backend = KisTiledDataManagerTest::backend(dm);
    const auto before = backend->captureReadView();
    auto retained = dm.getTile(0, 0, false);
    check(retained && retained->lockForRead(), "initial reader");
    const quint8 *oldPointer = retained->data();
    check(*oldPointer == (warm ? 0x31 : 0), "initial pixel");
    if (!hold) { retained->unlockForRead(); oldPointer = nullptr; }
    auto observe = [&](const char *phase, bool published) {
        const auto view = backend->captureReadView();
        const int pixel = exact(backend, view);
        const QRect canonicalExtent = extent(backend, view);
        auto fresh = dm.getTile(0, 0, false);
        bool present = false;
        auto lazy = dm.getReadOnlyTileLazy(0, 0, present);
        const int raw = readTile(fresh), lazyRaw = readTile(lazy);
        const QRect managerExtent = dm.extent();
        check(pixel == (published ? 0x61 : (warm ? 0x31 : 0)), "canonical pixel");
        check(canonicalExtent == (published || warm ? QRect(0, 0, 64, 64) : QRect()), "canonical extent");
        check(exact(backend, before) == (warm ? 0x31 : 0), "old captured pixel");
        if (oldPointer) check(*oldPointer == (warm ? 0x31 : 0), "active old pointer stable");
        const bool coherent = raw == pixel && lazyRaw == pixel && managerExtent == canonicalExtent;
        if (!coherent) ++violations;
        emitRow({{"kind", "publication"}, {"bpp", bpp}, {"packed", packed}, {"warm", warm},
                 {"held_old_reader", hold}, {"phase", phase}, {"exact", pixel}, {"raw", raw},
                 {"lazy_raw", lazyRaw}, {"hash_present", present}, {"same_wrapper", fresh == retained},
                 {"canonical_extent", rect(canonicalExtent)}, {"manager_extent", rect(managerExtent)},
                 {"coherent", coherent}});
    };
    int sealSeen = 0, adapterSeen = 0;
    KisPageStoreDiagnosticRecorder recorder(true, backend->store());
    recorder.setPhaseObserver([&](KisPageStoreDiagnosticPhase phase) {
        using P = KisPageStoreDiagnosticPhase;
        if (phase == P::MutationSealMetadataPrepare) observe("metadata_prepare", false);
        else if (phase == P::MutationSealCleanup) { ++sealSeen; observe("seal_cleanup", true); }
        else if (phase == P::PixelOperationCleanup) observe("operation_cleanup", true);
        else if (phase == P::MutationAdapterInstalled) { ++adapterSeen; observe("adapter_installed", true); }
    });
    if (packed) {
        KisStrokeJobFailureContext failure(true);
        dm.writeBytes(reinterpret_cast<const quint8 *>(value.constData()), 0, 0, 1, 1);
        check(!failure.failed(), "packed write");
    } else {
        check(dm.writePageStoreOperation({QRect(0, 0, 1, 1)}, [&](KisPixelWriteCursor *cursor) {
            cursor->moveTo(0, 0);
            if (!cursor->rawData()) return false;
            std::memcpy(cursor->rawData(), value.constData(), size_t(bpp));
            return true;
        }) == KisPageStoreWriteOperationResult::Succeeded, "cursor write");
    }
    recorder.setPhaseObserver({});
    check(sealSeen == 1 && adapterSeen == 1, "actual publication phases reached");
    // Writer has returned. This is an independent reader on another thread,
    // not a nested lock acquired by the original reader's call stack.
    std::thread freshReader([&] { observe("after_return_other_thread", true); });
    freshReader.join();
    if (hold) retained->unlockForRead();
    check(readTile(dm.getTile(0, 0, false)) == 0x61, "current after last old unlock");
    check(exact(backend, before) == (warm ? 0x31 : 0), "captured view remains fixed");
}
static void pendingCase(int bpp, bool warm)
{
    ++scenarios;
    const QByteArray blank(bpp, 0), old(bpp, char(0x31));
    KisTiledDataManager dm(bpp, reinterpret_cast<const quint8 *>(blank.constData()));
    if (warm) dm.writeBytes(reinterpret_cast<const quint8 *>(old.constData()), 0, 0, 1, 1);
    auto *backend = KisTiledDataManagerTest::backend(dm);
    const auto owner = dm.getMemento();
    check(owner && dm.beginStrokeMutation(owner), "original history owner");
    check(dm.applyStrokePixelOperation(owner, {QRect(128, 0, 1, 1)}, [&](KisPixelWriteCursor *cursor) {
        cursor->moveTo(128, 0);
        if (!cursor->rawData()) return false;
        std::memset(cursor->rawData(), 0x61, size_t(bpp));
        return true;
    }), "pending operation");
    const auto before = backend->captureReadView();
    const QRect pendingExtent = dm.extent();
    check(exact(backend, before, 2) == 0, "external read stays on checkpoint");
    check(extent(backend, before) == (warm ? QRect(0, 0, 64, 64) : QRect()), "checkpoint extent");
    check(pendingExtent == (warm ? QRect(0, 0, 192, 64) : QRect(128, 0, 64, 64)), "pending compatibility extent");
    emitRow({{"kind", "history_pending"}, {"bpp", bpp}, {"warm", warm},
             {"exact", exact(backend, before, 2)}, {"canonical_extent", rect(extent(backend, before))},
             {"manager_extent", rect(pendingExtent)}, {"interpretation", "different selections; not counted as publication violation"}});
    check(dm.checkpointStrokeMutation(owner), "checkpoint");
    const auto after = backend->captureReadView();
    check(exact(backend, after, 2) == 0x61 && extent(backend, after) == pendingExtent, "checkpoint catches up");
    check(exact(backend, before, 2) == 0, "old checkpoint stable");
    check(dm.tryAbort(owner), "abort restores original state");
    check(dm.extent() == (warm ? QRect(0, 0, 64, 64) : QRect()), "abort extent");
}
static void intentCase(int bpp)
{
    ++scenarios;
    const QByteArray blank(bpp, 0);
    KisTiledDataManager dm(bpp, reinterpret_cast<const quint8 *>(blank.constData()));
    auto *backend = KisTiledDataManagerTest::backend(dm);
    auto tile = dm.getTile(2, 0, true);
    check(tile && tile->lockForWrite(), "write intent without mutable exposure");
    tile->unlockForWrite();
    const auto view = backend->captureReadView();
    const auto canonicalExtent = extent(backend, view);
    check(canonicalExtent.isEmpty() && dm.extent() == QRect(128, 0, 64, 64), "intent extent distinction");
    emitRow({{"kind", "write_intent"}, {"bpp", bpp}, {"canonical_extent", rect(canonicalExtent)},
             {"manager_extent", rect(dm.extent())}, {"interpretation", "compatibility intent; not a published pixel"}});
}
int main(int argc, char **argv)
{
    setvbuf(stdout, nullptr, _IONBF, 0);
    QCoreApplication app(argc, argv);
    QStandardPaths::setTestModeEnabled(true);
    { KisImageConfig c(false); c.setMemoryHardLimitPercent(20); c.setMemoryPoolLimitPercent(0); }
    for (int bpp : {1, 4, 8, 16}) {
        for (bool packed : {false, true}) for (bool warm : {false, true}) for (bool hold : {false, true})
            publicationCase(bpp, packed, warm, hold);
        for (bool warm : {false, true}) pendingCase(bpp, warm);
        intentCase(bpp);
    }
    emitRow({{"kind", "summary"}, {"scenarios", scenarios}, {"observations", observations},
             {"control_errors", errors}, {"publication_violations", violations},
             {"scope", "reproduction and compatibility controls; not a fix or performance qualification"}});
    if (errors) return 2;
    return app.arguments().contains("--require-converged") && violations ? 3 : 0;
}
