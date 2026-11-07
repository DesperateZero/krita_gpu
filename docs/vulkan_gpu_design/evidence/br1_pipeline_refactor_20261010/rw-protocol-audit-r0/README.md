# bb62 读写责任价格与统一协议审查

**后续必要性拆分：** [53.451M／3.374ms分类与138过程证据](NECESSITY_RESULT.md)补出768次零delta交接、128次真实补债务额度、1024次无dirty的domain探查，以及1984个无Retiring的版本访问。ledger交接准备/提交暴露约6.050M/0.401ms；completion总验证仅约0.035ms。以下192过程为前批冻结证据，不与新批相加成精确机制账；A/B/C精确额外金额和净可回收价仍未证明。

产品仍为 **bb62f28b7a9806043ae92a91f58b8856b59bca5a**。本轮只生成隔离观察器、运行原公共夹具并深化原蓝图；产品/测试源码增删均为0。上轮生产净+847不是本轮增量。当前唯一设计见[原蓝图§19.22](../../br1_pagestore_equivalent_pipeline_20261010/PIPELINE_PLAN.md#rw-single-protocol-audit)，本页是冻结测量证据。

## 结论与价格口径

上轮联合候选的净收益成立，但尚未形成最简的一套CPU读写表达。CPU final使用原entry内native reservation，mutable/真实recoverable/generic仍用原writer状态；两者汇入相同publication，却有native事实重新投影成通用snapshot、重复proof查询和按页调用全局准入的适配成本。它不是所有写都串行跑两次完整协议，也不是两个独立transaction owner。必要producer差异与可删表示往返必须分开。

同批调用量确认：主格64次写/1024页，1024次base选择、1024次operation ID、1024次writer token、1024次CPU proof封印；**proof归属3968次 = 2×(1024个新proof+960个被替换proof)**，分别位于publication准备与接受。completion验证1152次，不能都称同一个Host票据；1024次封印以外还含实际provider完成。896次handoff prepare/commit；1024次预算reserve与domain同步。noop仍有1024次base选择、两类ID各1024次、64次seal，且没有新write reservation/proof。这些是新隔离census，不是由代码猜出的时间比例。

### 三批有限诊断及观察器费用

1. [第一批协议](PROTOCOL.md)：plain/off/count/full/sample五条件，4块镜像40过程。主格write普通56.259M/3.291ms，关闭派生57.216M/3.446ms；全计时156.639M/11.337ms，根1/4采样87.966M/5.861ms。指令扰动178.4%/56.4%，全量CPU扰动244.5%。**所有内部细分时间否决为产品价格**，只保留调用数和嵌套守恒检查。不能因为全量与抽样细分看似一致就接受两者共同的观察偏差。
2. [第二批协议](SPARSE_PROTOCOL.md)：一次只观察一个函数，调用1/8随机采样；每case在计价端点前测256个相同空counter/clock窗口。12条件，4块镜像96过程。保留原始窗口价格与扣除实测空窗口后的探索估计；没有比例缩放产品时间。全局布局/调用扰动仍可能存在。主格write各目标的指令扰动2.15%–3.78%、CPU点扰动1.14%–8.54%。部分CPU扰动区间超过10%，不能宣称已证明观察器等价。
3. [最后拆分协议](DETAIL_PROTOCOL.md)：7条件，4块镜像56过程，仅细分最大的input责任；write指令扰动2.74%–4.05%，CPU点扰动−1.64%–4.16%。本轮到此停止取样，不将两个批次拼成精确互斥账。

合计192过程，原13格共2496次语义/身份/退出检查通过；这是诊断执行覆盖，不是新增2496个独立安全用例。只测arm64；未改写上轮双架10834测试的身份、控制失败或M6资格。每批以4个block为统计单位；下列95%区间为4块经验bootstrap探索区间，未覆盖系统性观察偏差，不是同时置信或合法替代净收益。

### 第二批：当前前台责任暴露

单位指令M、线程CPU ms。均为inclusive：父子不能相加。数字为减去同case实测空窗口的探索估计，原始值完整保存在`sparse-analysis.json`。

| 责任 | 指令M | CPU ms [探索95%区间] | 归属与限制 |
|---|---:|---:|---|
| final_input | 29.230 | 1.876 [1.811,1.956] | 输入比较、目标准备、物理计划及完成；包含下方base/handoff |
| seal | 19.463 | 1.145 [1.052,1.280] | 包含proof、delta、metadata及接受/清理 |
| base_select | 2.532 | 0.282 [0.243,0.333] | base/descriptor/ID等，包含必要选择 |
| handoff_prepare | 4.376 | 0.271 [0.249,0.292] | ledger/domain/admission/claim存储；不包含全部physical plan |
| proof_seal | 2.551 | 0.182 [0.167,0.193] | 完成验证、provider验证、stamp及native proof安装 |
| delta_prepare | 4.230 | 0.236 [0.191,0.266] | changes/节点准备及第一次proof归属查询 |
| metadata_prepare | 2.786 | 0.177 [0.161,0.198] | 原metadata联合准备 |
| metadata_install | 2.933 | 0.188 [0.153,0.219] | 原联合claims/安装/清理移交 |
| range_capture（read） | 2.087 | 0.220 [0.171,0.269] | CPU扰动区间宽至约22%，仅方向性报价 |
| resident_read（read） | 0.912 | 0.176 [0.131,0.222] | **指令/CPU扰动11.68%/16.94%，不接受为普通产品价** |
| capture_release（read） | 0.420 | 0.029 [0.028,0.030] | 整范围释放责任，非必要成本下界 |

例如handoff_prepare原始采样估计0.604ms，实测空窗口扣除后0.271ms；proof_seal从0.516ms到0.182ms。这个差异说明即使稀疏观察的总扰动较低，小函数本身仍有明显窗口税。校准后的价格只支持规模排序，不能作为毫秒级精确可删承诺。

### 第三批：输入准备内部

| 责任 | 指令M | CPU ms [探索95%区间] | 包含关系 |
|---|---:|---:|---|
| final_input桥接观察 | 30.470 | 1.937 [1.782,2.093] | 与第二批量级一致；不是独立优化收益 |
| target_prepare | 18.963 | 1.099 [0.953,1.244] | 包含physical_plan及冷Fresh准备 |
| physical_plan | 12.909 | 0.778 [0.743,0.818] | eligibility、spare/before、物理claim、ledger交接、descriptor及退出 |
| fresh_provider | 2.481 | 0.161 [0.139,0.189] | 真实Fresh provider，不含全部前后owner成本 |
| backing_reserve | 1.340 | 0.065 [0.058,0.071] | Fresh费用及退休存储准备 |
| backing_register | 0.544 | 0.040 [0.037,0.044] | 新物理backing登记 |

**排名修正：完整physical_plan与seal是下一协议责任；不能将handoff_prepare或completion验证单独称为榜首。** handoff_prepare和proof_seal的当前点暴露合计约0.45ms，即使假设它们免费，也不足以支持原0.75ms整包收益目标；这不是严格上界，更不是可以实际全部删除的预算。final_input扣去target_prepare的同批点差约0.839ms，含base选择、比较、pin/copy/完成及观察差；没有exclusive证据，保留为混合余项，不改名为锁或memcpy。

此处价格是当前责任成本，**不是相对upstream额外成本，也不是合法替代净可回收成本**。原同批upstream残差继续为write50.218M/2.953ms、read3.234M/0.421ms。尚无定量证明其中某笔是不可约必要额外成本；重写之后才能给出合法净价。跨批数字不相减来声称账本闭合。

## 复现、身份与失败

`build.py`生成7个隔离TU，复用同一当前编译数据库和未修改对象；`run.py`、`build_sparse.py/run_sparse.py`、`build_detail.py/run_detail.py`对应三批。三个分析器复算各自原数据，禁止向现有runs目录追加。派生源码差异、命令、原始日志、普通/派生库和实际加载依赖hash保存在`raw-texts.tar.gz`及`evidence-manifest.json`；二进制仅本机保存。`source-consumers.json`绑定当前源码、符号及实际生产/测试consumer，索引不是第二份实现。

首次builder引用不存在的prepareRecoverableBacking，断言在编译前停止；该待观察点改由真实prepareWritePlanLocked在最后一批覆盖。观察器random与系统random同名导致编译失败，改名后仅重编observer/链接；原失败日志保留。sparse链接命令归档曾保存替换前列表，执行使用正确命令；在任何sparse测量前修正归档及hash，未换库或样本。所有计价过程通过；没有删除坏样。产品源码、普通库均保持原身份。
