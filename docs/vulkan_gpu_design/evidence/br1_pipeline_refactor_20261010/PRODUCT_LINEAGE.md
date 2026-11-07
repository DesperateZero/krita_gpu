# 产品祖先提交清单（IB0汇总附件）

基点 `e238d170d30a505a92f209874826ead056841566`；从CP3安装收口500fd0702c起共 **66** 个提交，逐一通过Git祖先验证。
祖先关系只证明代码历史纳入，不证明每个优化仍以原形存在或性能已验收。后继覆盖、撤回及研究新实现见[汇总](OPTIMIZATION_ROLLUP.md)。
修改文件的机器索引见[product-lineage.json](../br1_pagestore_equivalent_pipeline_20261010/intermediate-baseline/product-lineage.json)。

| 提交 | 原提交标题 | 最终归类 |
|---|---|---|
| `500fd0702c` | pagestore: eliminate handoff install frees and restore containment | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `840d14ae71` | Converge paid publication preparation and defer activity storage release | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `b8581139d2` | Consume paid metadata transition values without protection-image clones | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `9c707902d6` | Keep synchronous storage accounting on the allocator stack | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `822456732b` | Compute original budget limits once per admission class | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `6d439e0437` | Batch sparse epoch root construction and preserve working storage affinity | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `58b4dfc09c` | Reuse coordinator-owned working results through metadata policy | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `feff9031b1` | Group backing changes in charged batch storage | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `5086aa6ef9` | Build publication authority snapshots in charged arrays | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `84b5d5aad9` | Derive registered backing claims from original physical slots | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `864627f957` | Remove redundant accepted metadata batch identity storage | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `6ffe097909` | perf: coalesce prepared metadata candidate storage | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `57e59e6b0e` | Retain metadata storage once per scope and borrow nested allocators | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `0a00bd3fe3` | Reuse unchanged budget policy for metadata storage admission | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `f0c40a5d19` | Reuse funded storage in recoverable handoff preparation | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `79e1c8d1ef` | perf(pagestore): reject known busy handoff candidates before preparation | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `38834c4e26` | perf(pagestore): defer cold handoff preparation and borrow retained provider | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `128fb32a71` | test(pagestore): cover real archive capacity refusal and recovery | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `2f22452e2d` | Avoid materializing sparse pages for partial default clears | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `f9714b4d31` | Experiment with page-ordered fixed-source CPU writes | 试验；被fb57显式撤回，不加入IB0 |
| `fb57b8b69b` | Revert "Experiment with page-ordered fixed-source CPU writes" | 撤回前项试验；没有保留其加速 |
| `751bceff23` | Fix native tile pin ownership at the last reader unlock | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `a918e45e02` | Reuse the held tile barrier for native pin cleanup | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `6644249a4c` | Optimize CPU projection lifecycle as a measured candidate | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `704d96e81c` | Reuse accepted CPU mutation authority and remove empty lock handoffs | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `d182a34bd0` | Optimize CPU page lifecycle with compact metadata and bounded shard batches | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `c13c442493` | test: cover history creation after empty collection requests | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `8198c36ed7` | perf: fuse independent projection clear and first composite | 已有通用融合；不计作PageStore基础效率证据 |
| `3f2826d464` | refactor: separate PageStore target preparation from mutable exposure | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `4dc89bada3` | refactor: unify prepared overlay acceptance cleanup | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `7c36dceb85` | refactor: consolidate CPU operation delivery and batch termination | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `ccbf0bcb0d` | refactor: deliver final page presence through prepared adapter installation | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `081afa7072` | refactor: unify copy admission and prepared adapter delivery | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `ce903fe3e9` | refactor: commit directly from owned publication delta | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `2363d824b7` | fix: derive restoration and reclamation from actual retained roots | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `0e55a60932` | Use one transaction base for ordered allocated-page enumeration | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `faffef592c` | Prepare complete restore index delivery and semantic tile removal | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `ee8a165fc7` | Unify failed tile import with prepared history cancellation | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `e03742b0ef` | Deliver trim through prepared index reconciliation and remove rebuild path | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `1249396fa8` | Preserve explicit default writes across PageStore history | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `73a9fde6b3` | Establish explicit PageStore presence for public writable tiles | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `75dc8fca5f` | Remove inactive PageStore wiring from legacy clear | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `67ae4a8caa` | Isolate PageStore operation publication and unify raw completion | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `e6fc6d687c` | Close working tile adapters from the original mutation outcome | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `11adac3e3a` | Retain owned transaction cancellation in the original mutation scope | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `f25d3085d0` | Remove redundant region recovery from compatibility writes | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `e9d2048b4c` | Prepare full-clear adapter removal before canonical acceptance | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `c1f4efcf07` | Prepare purge index removal before publication and drop unused tile retention | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `a24062b966` | Deliver history adapters from the prepared segment and remove unused read captures | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `667c8d6516` | Unify PageStore clone around one captured source view | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `e1a26e14d9` | Use the owned mutation lifecycle for tile import | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `2eb9f4236f` | Unify compatibility copy adapter delivery | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `16a4ff59eb` | Remove retired read-cache adapters and refresh pipeline audit | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `cb942b6eff` | Reclaim history only when the last epoch protection ends | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `6f76902d4a` | Notify history collection from accepted read protection changes | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `11c6895ddf` | Transfer completed read records before reclamation and remove redundant retry stages | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `02bccf1d12` | Prototype operation-owned PageStore publication and working capacity | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `d5f71573bb` | Prototype delta installation for private PageStore writes | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `e103b5da0f` | Verify final adoption against private writer lifecycle and late readers | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `bb62f28b7a` | perf(pagestore): adopt completed CPU results and retain finite read ranges | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `ed0f229821` | Unify CPU private results and captured read lifetimes | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `b7565f0f6f` | Unify CPU publication and captured-read minimum paths | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `33132de1ec` | Fix signed shared budget settlement for backing transitions | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `0f526aea1d` | Verify charged retirement continuation without speculative debt quota | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `0b116b04e8` | Preserve charged ownership across canonical metadata detachment | 产品祖先；最终内容以e238为准，非独立性能验收 |
| `e238d170d3` | Fix bounded close progress after retirement debt release | 产品祖先；最终内容以e238为准，非独立性能验收 |
