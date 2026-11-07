仅为provider配置预算拒绝的定向行为检查，3通过。此时原候选12文件已暂存，旧runner用git diff仅冻结了两份追加改动；完整源码差集不在此文件夹，因此不将本批作为最终源/库资格。最终candidate-config-fix及safety-config-fix改用git diff HEAD，覆盖12文件全部差集。此批实际库哈希仍可用于定位，不删除原始结果。
