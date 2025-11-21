"""
| 年度 | 单位编码 | 单位名称 | 项目编码 | 项目名称 | 预算金额(万元) | 支付金额(万元) | 执行率(%) |
|------|----------|----------|----------|----------|---------------|---------------|-----------|
| 2023 | 622001 | 中国农工民主党CC省委员会 | 330000200100622001005 | 参政议政工作专项-课题调研 | 22.35 | 21.25 | 95.1 |
| 2024 | 622001 | 中国农工民主党CC省委员会 | 330000200100622001005 | 参政议政工作专项-课题调研 | 23.61 | 17.32 | 73.37 |
"""

import json
from typing import List, Dict


def json_to_markdown(json_data: List[Dict]) -> str:
    """
    将JSON数据转换为Markdown表格格式

    Args:
        json_data: JSON数据列表，每个元素是一个字典代表一行数据

    Returns:
        Markdown表格字符串
    """
    if not json_data:
        return "无数据"

    # 获取表头（使用第一个字典的键）
    headers = list(json_data[0].keys())
    # 生成表头行
    header_row = "| " + " | ".join(headers) + " |"
    # 生成分隔线
    separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"

    # 生成数据行
    data_rows = []
    for item in json_data:
        # 处理每个单元格的值，确保是字符串且转义特殊字符
        row_cells = []
        for header in headers:
            value = item.get(header, "")
            # 转义Markdown中的特殊字符，主要是管道符
            if isinstance(value, str):
                value = value.replace('|', '\\|')
            row_cells.append(str(value))
        data_rows.append("| " + " | ".join(row_cells) + " |")

    # 组合完整的Markdown表格
    markdown_table = "\n".join([header_row, separator_row] + data_rows)

    return markdown_table


sample_data = [
    {
        "年度": 2023,
        "单位编码": "622001",
        "单位名称": "中国农工民主党CC省委员会",
        "项目编码": "330000200100622001005",
        "项目名称": "参政议政工作专项-课题调研",
        "预算金额(万元)": 22.35,
        "支付金额(万元)": 21.25,
        "执行率(%)": 95.1
    },
    {
        "年度": 2024,
        "单位编码": "622001",
        "单位名称": "中国农工民主党CC省委员会",
        "项目编码": "330000200100622001005",
        "项目名称": "参政议政工作专项-课题调研",
        "预算金额(万元)": 23.61,
        "支付金额(万元)": 17.32,
        "执行率(%)": 73.37
    }
]

sample_data2 = '''
[
    [
        "2023",
        "622001",
        "中国农工民主党CC省委员会",
        "330000200100622001005",
        "参政议政工作专项-课题调研",
        "22.35",
        "21.25",
        "95.1"
    ],
    [
        "2024",
        "622001",
        "中国农工民主党CC省委员会",
        "330000200100622001005",
        "参政议政工作专项-课题调研",
        "23.61",
        "17.32",
        "73.37"
    ]
]
'''

import ast
def json_to_markdown2(json_data: str) -> str:
    """
    将JSON数据转换为Markdown表格格式

    Args:
        json_data: JSON数据列表，每个元素是一个字典代表一行数据

    Returns:
        Markdown表格字符串
    """
    title = '## 六、项年执行率'
    markdown_table = "| 年度 | 单位编码 | 单位名称 | 项目编码 | 项目名称 | 预算金额(万元) | 支付金额(万元) | 执行率(%) | \n"

    # 添加表格分隔符行（必需）
    markdown_table += "|------|----------|----------|----------|----------|---------------|---------------|-----------| \n"

    # 生成数据行
    data_rows = []
    for item in json.loads(json_data):
        # 处理每个单元格的值，确保是字符串且转义特殊字符
        row_cells = [str(cell) for cell in item]
        data_rows.append("| " + " | ".join(row_cells) + " |")

    # 组合完整的Markdown表格（包含分隔符）
    markdown_table += "\n".join(data_rows)

    return markdown_table

# 使用示例
if __name__ == "__main__":
    # 示例1：使用样板数据
    print("=== Markdown表格输出 ===")
    # result = json_to_markdown(sample_data)
    result = json_to_markdown2(sample_data2)
    print(result)
