"""

    "nacos-mcp": {
      "command": "/home/zhaozhiwei/miniconda3/envs/py_3.12/bin/python",
      "args": [
        "/home/zhaozhiwei/workspace/python/demo/llm/mcp/nacos_mcp_adapter.py"
      ],
      "disabled": false,
      "alwaysAllow": []
    }
"""
from fastmcp import FastMCP
from nacos import NacosClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NacosMCPService:
    def __init__(self):
        self.server = FastMCP("nacos-mcp")
        self.nacos_client = NacosClient("127.0.0.1:8848")

        @self.server.tool()
        async def get_config(data_id: str, group: str = "DEFAULT_GROUP") -> str:
            """获取Nacos配置"""
            return self.nacos_client.get_config(data_id, group)

        @self.server.tool()
        async def watch_config(data_id: str, group: str = "DEFAULT_GROUP"):
            """监听配置变化"""
            def callback(config):
                logger.info(f"Config changed: {config}")
            return self.nacos_client.add_config_watcher(data_id, group, callback)

def run():
    service = NacosMCPService()
    service.server.run(transport='stdio')

if __name__ == "__main__":
    run()