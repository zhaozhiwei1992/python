"""
加法计算的一个MCP Server

    "demo": {
      "command": "/home/zhaozhiwei/miniconda3/envs/py_3.12/bin/fastmcp",
      "args": [
        "run",
        "/home/zhaozhiwei/workspace/python/demo/llm/mcp/SumMCP.py"
      ],
      "disabled": false,
      "alwaysAllow": []
    },
"""
# server.py
from fastmcp import FastMCP
import os

mcp = FastMCP("Demo", log_level="ERROR")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print("add", a, b)
    return a + b

@mcp.tool()
def listdir(path: str) -> list[str]:
    """show user dir list 显示用户文件列表"""
    return os.listdir(path)

if __name__ == "__main__":
    # mcp.run()
    # mcp.run(transport="sse", port=9123)
    mcp.run(transport='stdio')