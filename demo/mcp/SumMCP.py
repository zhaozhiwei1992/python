"""
加法计算的一个MCP Server
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
    # mcp.run(transport="sse", port=9123)  # 网页6推荐SSE协议
    mcp.run(transport='stdio')