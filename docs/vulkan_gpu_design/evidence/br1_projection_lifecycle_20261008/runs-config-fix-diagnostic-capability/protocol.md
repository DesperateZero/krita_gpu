# 初始化压力接续修复后的最终批

沿用PROTOCOL.md所有端点、20个ABBA块、40对、bootstrap/置信、失败/停止规则和固定M5控制，不改变阈值、不筛样。此批原因是发现且修复真实的provider配置拒绝接续缺陷，不是为Undo扩样到通过。原read-fix各80过程、Fresh/H4各320过程及所有结果完整保留，最终结果单列config-fix前缀，不与上一批合并提高显著性。

产品仅在common provider configure补原完成源复用及跨registry拒绝：registerSource成功但Ready记录拒绝后，原completionSource/completions字段承担重试，不新增状态；预算恢复沿原未发票源继续，避免遗弃注册。新增真实预算容量测试，精确容纳源却不容纳ready，验证重复拒绝、registry身份及恢复。正常操作热路径无新分支；仍重新冻结最终库、跑双架安全、机制和无插桩/受保护控制，最后结论对应最终源码。
