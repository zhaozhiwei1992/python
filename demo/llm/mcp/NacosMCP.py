"""
使用nacos注册的mcp server

    "nacos-mcp-python": {
      "url": "http://localhost:18001/sse",
      "type": "sse",
      "alwaysAllow": [],
      "disabled": false
    },
"""
from nacos_mcp_wrapper.server.nacos_mcp import NacosMCP
from nacos_mcp_wrapper.server.nacos_settings import NacosSettings

# Create an MCP server instance
nacos_settings = NacosSettings()
nacos_settings.SERVER_ADDR = "127.0.0.1:8848" # <nacos_server_addr> e.g. 127.0.0.1:8848
nacos_settings.USERNAME="nacos"
nacos_settings.PASSWORD="nacos"
mcp = NacosMCP("nacos-mcp-python", nacos_settings=nacos_settings, port=18001)

# Register an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers together"""
    return a + b

# Register a subtraction tool
@mcp.tool()
def minus(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b


if __name__ == "__main__":
    try:
        # 服务保持运行
        mcp.run(transport="sse")
        # mcp.run(transport="stdio")
        # mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"Runtime error: {e}")