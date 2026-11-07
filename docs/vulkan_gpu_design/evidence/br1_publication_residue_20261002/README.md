# BR1 publication 与 detach 残余清理（2026-10-02）

产品提交`31dabb9789400c697851f553342f9051e4664c99`，父提交`e08545e5f2e77d1d8598032b8546f70eb93e932d`；文档父提交`6fb29d37f017112b7b48dfbaae22ed8e21445b1c`。[Git身份](git-round-identity.json)、[47份源码](source-sha256.txt)、[15份运行物](runtime-sha256.txt)和[5份构建依赖](build-environment.json)绑定最终结果。未读archive、未改上层生产/API、未push，普通编辑为显式apply_patch。

publication各合法准备种类没有退休效果：commit/default replacement/restore保留旧replica为history，detach只改publication/preparedBy，recoverable write转交backing。删除PreparedPublication效果容器/getter/install输出，以及PreparedMutationCommit对应字段和commit空packet搬运。真正的abort/cancel/discard/GC效果、Ledger class reservation和foreground queue pump继续。detach准备、activity复验、安装共用原record isPreparedBy，两个完整版本/protection快照删除；合法身份/writer/claim拒绝和晚保护不变。

[生产差集](production-incremental.diff)3文件 **+14/-33，净-19**；[测试差集](tests_and_model-incremental.diff)2文件 **+31/-44，净-13**；生成审计2文件+3569/-3652单列，ownership无改。[统计](source-metrics.json)按完整产品父提交计算。没有新增业务保证、持久阶段或队列；不能从净删行推导性能。测试原数据行不增，空效果接口测试改为full oracle的expected.effects为空，完整版本/replica/保护对照及实际退休回归保留。

一个universal build writer完成[构建](build.log)后运行[编排](run_results.py)：offscreen、seed12345、原prefix/plugin，core为0，Qt crash handler关闭。两架构每架Registry87、CPU1297、Reference661、Physical381、Resident221、Foundation28、Freehand压力/取消两方法4；[最终结果](qualified-results.json)合计 **5358 passed / 0 failed / 0 skipped**，14进程退出0，含init/cleanup。publication原子拒绝、并发reader、default/restore full oracle、prepared recoverable write、detach late lease/pin/last-use/capture/handoff、deferred cleanup晚销毁及真实abort/retirement全部由原测试覆盖。没有本轮产品构建或测试失败。

构建结束后才生成[callgraph](callgraph.log)：87 TUs、1956 APIs、21840 edges、21 callbacks。首次[结构检查](architecture-stale.log)只报告5份已改源码checkpoint过时，核对后门限不变[刷新](architecture-refresh.log)，[独立检查](architecture-final.log)通过21 manifest/25 ownership/16 census/19 intrusion。[前](baseline-before.json)/[后](baseline-after.json)快照保留。初次身份脚本误要求ownership生成物必须改变；实际ownership未改，收紧为本轮2个实际生成差集后冻结成功，没有将未改文件计作收益。

[12项删除/保留检查](deletion-checks.json)及[脚本](check_deletions.py)核对全部原caller与真实效果消费者。静态删除检查不替代行为验证；剩余read/capture进度、Pending/subscription/Delay/Debt、公开ticket拒绝、generic effects及proof/Qt准备失败均列实际consumer和删除条件。generic metadata/overlay真实Qt容量、bootstrap/固定成本及完整永久压力最后handle等CP1差集没有被本轮简化关闭。

当前裁决见[92 §16.48](../../92_br1_m6_m8_execution_baseline.md#publication-residue-delivery)，[代码](../../br1_modification_guide/CODE_INDEX.md#publication-residue-code-index)与[API](../../br1_modification_guide/API_CONVERGENCE_MAP.md#publication-residue-api-delivery)同步。本轮清理完成，**完整CP1仍开放，M6/M7/M8正式资格0/3、默认关闭**；未取得性能、TSAN、公平或原job自动接续资格。
