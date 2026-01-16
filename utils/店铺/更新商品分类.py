"""
# 文档格式
店内分类	店内码/货号
"商家设置的店内分类，即顾客在购买时看到的商品所属分类。
一级分类与二级分类之间用“>”隔开，商品属于多个店内分类时，用“”隔开"	自行定义的商品店内编码
猫条餐包	217
勺/奶瓶/喂药	731
猫条餐包	215
零食冻干	185
猫条餐包	218

"""
# 处理数据并生成SQL
def generate_sku_sql_from_excel(df):
    """
    从Excel数据生成SKU SQL
    """
    sql_statements = []

    # 遍历每一行数据
    for index, row in df.iterrows():
        # 处理各个字段
        sku_id = int(row['店内码/货号']) if not pd.isna(row['店内码/货号']) else index + 1000
        category = str(row['店内分类']) if not pd.isna(row['店内分类']) else ''

        # 构建SQL语句
        sql = f"update product_spu set category_id = (select max(id) from product_category where name = '{category}') where id = '{sku_id}';"

        sql_statements.append(sql)

    # 构建完整SQL
    if sql_statements:
        return '\n'.join(sql_statements)
    else:
        return "-- 没有有效的数据生成SQL"

import pandas as pd

# 读取Excel文件
file_path = '/home/zhaozhiwei/Downloads/11.xlsx'
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

# 生成SQL
sql_result = generate_sku_sql_from_excel(df_actual)
print("生成的SQL前1000个字符:")
print(sql_result[:1000])
print("...")
print(f"总共生成了 {len(sql_result.split('),'))} 条记录的SQL")

# 保存完整的SQL到文件
sql_filename = 'product_sku_update_category.sql'
with open(sql_filename, 'w', encoding='utf-8') as f:
    f.write(sql_result)

print(f"SQL脚本已保存到 {sql_filename}")