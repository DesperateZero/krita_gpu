# 复核器分组修订

首版 `verify-v0.py` 在 tests-r1 index 2（projection control）报告 workspace runtime changed，退出1；实际运行样本和前后hash没有失败。首版把两个不同语义测试的依赖集合也要求相等，超出了协议所需的同测试两臂比较。工具返回的实际失败为：

```text
AssertionError: ('tests-r1', 2, 'workspace runtime changed')
```

修订只将语义测试按实际 executable 分组；同一个 merger/projection 各自 control/fusion 和跨r0/r1保持相同依赖，matched 所有能力/探索/确认过程仍要求共同依赖。保存首版，不替换样本、加载记录、统计或预测。外部实体库的hash在复核时采集，是事后身份补证；原runner只有workspace输入/实际库的前后hash核验，不能把补证写成全部外部库前后已验。
