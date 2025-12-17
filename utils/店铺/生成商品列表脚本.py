# 处理数据并生成SQL
def generate_sku_sql_from_excel(df):
    """
    从Excel数据生成SKU SQL
    """
    sql_statements = []

    # 遍历每一行数据
    for index, row in df.iterrows():
        # 跳过空行或无效数据
        if pd.isna(row['店内码/货号']) or pd.isna(row['价格']):
            continue

        # 处理各个字段
        sku_id = int(row['店内码/货号']) if not pd.isna(row['店内码/货号']) else index + 1000
        name = str(row['商品名称']) if not pd.isna(row['商品名称']) else ''
        name = name.replace("'", "''")
        price = int(float(row['价格']) * 100) if not pd.isna(row['价格']) else 0  # 转换为分
        market_price = int(price * 1.3)  # 市场价设为售价的1.3倍
        cost_price = int(price * 0.6)    # 成本价设为售价的0.6倍
        stock = int(row['库存']) if not pd.isna(row['库存']) else 0
        weight = float(row['重量']) if not pd.isna(row['重量']) else 0.1
        purchase_code = str(row['货架码/位置码']) if not pd.isna(row['货架码/位置码']) else ''
        description = str(row['类目属性']) if not pd.isna(row['类目属性']) else ''
        description = description.replace("'", "''")

        # 处理重量单位转换为kg
        weight_unit = str(row['重量单位']) if not pd.isna(row['重量单位']) else '克(g)'
        if '克' in weight_unit or 'g' in weight_unit:
            weight = weight / 1000  # 克转换为千克
        elif 'kg' in weight_unit or '千克' in weight_unit:
            weight = weight  # 已经是千克单位
        else:
            weight = weight / 1000  # 默认转换为千克

        # 体积估算（简单按重量估算）
        volume = round(weight * 0.001, 6)

        # 佣金计算（简单按价格比例）
        first_brokerage = int(price * 0.05)  # 一级佣金5%
        second_brokerage = int(price * 0.02)  # 二级佣金2%

        # 销量默认为0
        sales_count = 0

        # 属性处理（简化处理）
        properties = '[]'  # 简化处理，实际可以根据类目属性生成

        # 构建SQL语句
        sql = f"({sku_id}, '{name}', '', '', '{description}', 0, 0, '', '[]', 0, 1, 0, {price}, {market_price}, {cost_price}, "
        sql += f"{stock}, '', 0, 0, 0, 0,0,0,"
        sql += f"NOW(), NOW(), 'system', 1, 0, 1, '{purchase_code}')"

        sql_statements.append(sql)

    # 构建完整SQL
    if sql_statements:
        sql_header = """-- 插入商品SKU数据（从Excel生成）
-- 注意：店内码/货号作为id，货架码/位置码存储在purchase_code字段
INSERT INTO product_spu
(id, name, keyword, introduction, description, category_id, brand_id, pic_url, slider_pic_urls, sort, status, spec_type, price, market_price, cost_price, stock, delivery_types, delivery_template_id, give_integral, sub_commission_type, sales_count, virtual_sales_count, browse_count, create_time, update_time, creator, updater, deleted, tenant_id, purchase_code)
VALUES
"""
        return sql_header + ',\n'.join(sql_statements) + ';'
    else:
        return "-- 没有有效的数据生成SQL"

import pandas as pd

# 读取Excel文件
file_path = '/home/zhaozhiwei/Downloads/982d8878-8c98-49cc-9f4d-907721373401.xlsx'
df = pd.read_excel(file_path)

# 显示前几行数据以了解结构
print("Excel文件的列名:")
print(df.columns.tolist())
# print("\n前5行数据:")
# print(df.head())
# print("\n数据形状:", df.shape)

# 跳过第一行说明行，从第二行开始读取实际数据
df_actual = df.iloc[1:].reset_index(drop=True)

# 查看实际数据的前几行
print("实际数据的前5行:")
print(df_actual.head())
# print("\n实际数据形状:", df_actual.shape)

# 检查关键列是否有空值
# print("\n关键列空值检查:")
# print("店内码/货号空值数量:", df_actual['店内码/货号'].isnull().sum())
# print("价格空值数量:", df_actual['价格'].isnull().sum())
# print("库存空值数量:", df_actual['库存'].isnull().sum())

# 生成SQL
sql_result = generate_sku_sql_from_excel(df_actual)
print("生成的SQL前1000个字符:")
print(sql_result[:1000])
print("...")
print(f"总共生成了 {len(sql_result.split('),'))} 条记录的SQL")

# 保存完整的SQL到文件
sql_filename = 'product_sku_insert.sql'
with open(sql_filename, 'w', encoding='utf-8') as f:
    f.write(sql_result)

print(f"SQL脚本已保存到 {sql_filename}")