#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""源文件入口（保留原命令行用法）：

    python governance_mcp_server.py     # stdio MCP server

实现在 `ubic_governance` 包内（ubic_governance/server.py），PyPI 分发版与源码树
跑的是同一份代码；本文件只做转发。
"""
import sys

from ubic_governance.server import main

if __name__ == "__main__":
    sys.exit(main())
