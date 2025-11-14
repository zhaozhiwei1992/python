import logging

from neo4j import GraphDatabase

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jDataImporter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def clear_database(self):
        """清空现有数据"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("已清空数据库")

    def create_business_scenario(self, scenario_data):
        """创建业务场景节点"""
        with self.driver.session() as session:
            query = """
            CREATE (bs:BusinessScenario {
                name: $name,
                description: $description,
                keyword_triggers: $keyword_triggers
            })
            """
            session.run(query,
                        name=scenario_data["name"],
                        description=scenario_data["description"],
                        keyword_triggers=scenario_data["keyword_triggers"])

            # 直接关联表节点（移除实体中间层）
            for table_name in scenario_data["direct_tables"]:
                session.run("""
                           MATCH (bs:BusinessScenario {name: $scenario_name})
                           MATCH (t:Table {name: $table_name})
                           CREATE (bs)-[:DIRECTLY_USES {
                               relationship_type: 'direct_mapping',
                               created_at: timestamp()
                           }]->(t)
                       """, scenario_name=scenario_data["name"], table_name=table_name)

    def create_table_node(self, table_data):
        """创建表节点"""
        with self.driver.session() as session:
            # 创建表节点
            query = """
            CREATE (t:Table {
                name: $name,
                comment: $comment,
                business_context: $business_context
            })
            """
            session.run(query,
                        name=table_data["name"],
                        comment=table_data["comment"],
                        business_context="")

            # 创建字段节点并建立关系
            for field in table_data["fields"]:
                field_query = """
                MATCH (t:Table {name: $table_name})
                CREATE (f:Field {
                    name: $field_name,
                    comment: $field_comment,
                    is_primary: $is_primary,
                    is_foreign: $is_foreign,
                    business_meaning: $business_meaning
                })
                CREATE (t)-[:HAS_FIELD]->(f)
                """
                session.run(field_query,
                            table_name=table_data["name"],
                            field_name=field["name"],
                            field_comment=field.get("comment", ""),
                            is_primary=field.get("is_primary", False),
                            is_foreign=field.get("is_foreign", False),
                            business_meaning=field.get("business_meaning", ""))

    def create_relationship(self, rel_data):
        """创建表间关系（修复版）"""
        with self.driver.session() as session:
            # 创建表间关系
            query = """
            MATCH (from_table:Table {name: $from_table})
            MATCH (to_table:Table {name: $to_table})
            CREATE (from_table)-[r:TABLE_RELATIONSHIP {
                name: $name,
                join_type: $join_type,
                from_field: $from_field,
                to_field: $to_field
            }]->(to_table)
            """
            session.run(query,
                        from_table=rel_data["from_table"],
                        to_table=rel_data["to_table"],
                        name=rel_data["name"],
                        join_type=rel_data["join_type"],
                        from_field=rel_data["from_field"],
                        to_field=rel_data["to_field"])

    def import_data(self, json_data):
        """主导入方法"""
        logger.info("开始导入数据到Neo4j...")

        # 清空数据库（可选，根据需求决定）
        # self.clear_database()

        # 导入表结构
        for table in json_data["tables"]:
            self.create_table_node(table)
            logger.info(f"创建表: {table['name']}")

        # 导入业务场景
        for scenario in json_data["business_scenarios"]:
            self.create_business_scenario(scenario)
            logger.info(f"创建业务场景: {scenario['name']}")

        # 导入表关系
        for relationship in json_data["relationships"]:
            self.create_relationship(relationship)
            logger.info(f"创建关系: {relationship['name']}")

        logger.info("数据导入完成！")


class ExpenditureQueryService:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def keyword_to_schema_direct(self, user_keyword):
        """修复版本：使用WITH子句分层处理聚合"""
        try:
            with self.driver.session() as session:
                query = """
                    MATCH (bs:BusinessScenario)
                    WHERE any(trigger IN bs.keyword_triggers WHERE toLower(trigger) CONTAINS toLower($keyword))

                    MATCH (bs)-[:DIRECTLY_USES]->(table:Table)

                    // 先收集所有相关表，再匹配关系
                    WITH bs, collect(DISTINCT table) as tables
                    UNWIND tables as table

                    // 匹配与这些表相关的所有关系
                    OPTIONAL MATCH (table)-[rel:TABLE_RELATIONSHIP]-(other:Table)
                    WHERE other IN tables  // 只匹配业务场景内的表关系

                    RETURN 
                        bs.name as scenario_name,
                        bs.description as scenario_description,
                        collect(DISTINCT {
                            table_name: table.name,
                            table_comment: table.comment,
                            fields: [(table)-[:HAS_FIELD]->(field:Field) | {
                                field_name: field.name,
                                field_comment: field.comment
                            }]
                        }) as related_tables,
                        collect(DISTINCT {
                            relationship_name: rel.name,
                            from_table: startNode(rel).name,
                            to_table: endNode(rel).name,
                            join_type: rel.join_type,
                            from_field: rel.from_field,
                            to_field: rel.to_field
                        }) as table_relationships
                  """

                result = session.run(query, keyword=user_keyword)
                return result.single()

        except Exception as e:
            logger.error(f"查询出错: {e}")
            return {"error": f"查询执行失败: {str(e)}"}


# Neo4j连接配置
NEO4J_URI = "bolt://10.10.115.10:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password123"  # 替换为你的密码


def create():
    # 你的JSON数据
    # json_data = json.loads(open("./data/表及业务信息/支付信息查询.json", "r").read())
    json_data = {
  "business_scenarios": [
    {
      "name": "支付信息查询",
      "description": "查询指定单位的支付凭证及明细信息，支持按不同口径汇总支出",
      "keyword_triggers": ["支付情况", "支付信息", "支付凭证", "支出查询"],
      "direct_tables": ["pay_voucher_bill", "pay_voucher_billsub"]
    }
  ],
  "tables": [
    {
      "name": "pay_voucher_bill",
      "comment": "支付凭证表",
      "business_context": "记录支付凭证的核心信息，如单位、总额、日期等，是'支付信息查询'业务的核心",
      "fields": [
        {
          "name": "AGENCY_CODE",
          "comment": "单位代码"
        },
        {
          "name": "AGENCY_NAME",
          "comment": "单位名称"
        },
          {
              "name": "GUID",
              "comment": "唯一标识"
          }
      ]
    },
      {
          "name": "pay_voucher_billsub",
          "comment": "支付凭证子表",
          "business_context": "记录支付凭证的详细明细项目，如具体的支出内容、收款方信息、单项金额等",
          "fields": [
              {
                  "name": "GUID",
                  "comment": "明细项唯一标识"
              },
              {
                  "name": "MAINGUID",
                  "comment": "所属主凭证GUID"
              }
          ]
      }
  ],
        "relationships": [
            {
                "name": "VOUCHER_HAS_ITEMS",
                "from_table": "pay_voucher_bill",
                "to_table": "pay_voucher_billsub",
                "from_field": "GUID",
                "to_field": "MAINGUID",
                "join_type": "LEFT_JOIN"
            }
        ]
    }

    try:
        # 导入数据
        importer = Neo4jDataImporter(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        # importer.clear_database()
        importer.import_data(json_data)
        importer.close()
    except Exception as e:
        print(f"执行过程中出错: {e}")

def query():
    try:
        # 查询测试
        query_service = ExpenditureQueryService(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

        print("=== 支出进度查询业务相关信息 ===")
        result = query_service.keyword_to_schema_direct("支付信息")
        if result:
            print(f"业务场景: {result['scenario_name']}")
            print(f"描述: {result['scenario_description']}")
            print("\n相关表信息:")
            for table in result['related_tables']:
                print(f"- 表名: {table['table_name']}")
                print(f"  注释: {table['table_comment']}")
                print("  字段:")
                for field in table['fields']:
                    print(f"    * {field['field_name']}: {field['field_comment']}")

        print("\n=== 详细表关系 ===")
        for rel in result['table_relationships']:
            print(f"- {rel['from_table']} --[{rel['relationship_name']}]--> {rel['to_table']}")
            print(f"  类型: {rel['join_type']}")

        query_service.close()
    except Exception as e:
        print(f"执行过程中出错: {e}")


if __name__ == "__main__":
    # 删
    # clear()
    # 增
    # create()
    # 查
    query()
