# AGENTS.md — 给 AI Agent 的工作指引

本文件面向自动化 AI Agent（编码助手、MCP 客户端、知识库机器人）。人类读者请看 [README.md](README.md)。

## 这个仓库是什么

`ubic-governance-mcp` 是一个**只读 MCP 工具包**（stdio 服务器），不是可独立运行的应用。核心资产是 `governance_mcp_server.py`（纯 Python 标准库，零第三方依赖）。它提供 5 个工具：`a3_assess`、`audit_evidence_chain`、`compliance_checklist`、`passport_lookup`、`gov_scan`。

## 可用的工作命令

```bash
# 初始化 + 列出工具
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python governance_mcp_server.py
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | python governance_mcp_server.py

# 文本体检（gov_scan）
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"gov_scan","arguments":{"text":"sample text"}}}' | python governance_mcp_server.py
```

前置依赖：Python ≥ 3.9。无第三方包。

## 约定（Do）

- 修改前先读 `agent.json` 的 AI 卡片，**保持字段兼容**（`name` / `protocol` / `capabilities` / `install` / `visaGate` 等）。
- 新增工具时同步更新 `agent.json`、`README.md`、`README.en.md`、`connector-meta.json` 与 `INTEGRATION.md`。
- 保持**零网络外发**：新增代码不得引入网络请求（`socket` / `requests` / `urllib` 等），除非经维护者明确批准。

## 禁止（Don't）

- 不要改动 `README.md`「权利与归属（Rights & Attribution）」段、`LICENSE` 的版权主体——**权属字段只由维护者变更**。
- 不要在仓库内提交任何密钥、令牌或真实客户数据。
- 不要声称本工具「已认证 / 已商用交付 / 已服务特定客户」——输出是**自评性质，非第三方认证**。
- 不要新增宣传性表述或品牌扩张内容。

## 边界

本工具是**只读**评估工具：输出自评结果，不做第三方认证；法规条款仅供方向性参考，以最新官方文本为准。
