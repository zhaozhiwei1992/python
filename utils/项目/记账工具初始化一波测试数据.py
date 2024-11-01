import random
from datetime import datetime, timedelta

# 定义科目信息
accounts = {
    '资产': {
        '现金': '001001',
        '银行': '001002',
        '投资': '001003',
        '固定资产': '001004',
        '其他资产': '001005'
    },
    '负债': {
        '贷款': '002001',
        '信用卡': '002002',
        '抵押': '002003',
        '其他负债': '002004'
    },
    '收入': {
        '工资': '003001',
        '投资': '003002',
        '其他收入': '003003'
    },
    '支出': {
        '衣服': '004001',
        '食品': '004002',
        '住房': '004003',
        '交通': '004004',
        '娱乐': '004005',
        '健身': '004006',
        '保险': '004007',
        '学习提升': '004008',
        '日常用品': '004009',
        '其他费用': '004010'
    }
}

# 生成日期范围
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)

# 生成插入语句
insert_statements = []
for i in range(10000):  # 生成100条记录
    account_category = random.choice(list(accounts.keys()))
    account_name = random.choice(list(accounts[account_category].keys()))
    account_code = accounts[account_category][account_name]
    amount = round(random.uniform(10, 5000), 2)  # 随机金额10到5000
    dr_cr = random.choice([-1, 1])  # 随机选择借方或贷方
    voucher_no = f"VOUCHER-{i + 1:06}"  # 生成凭证号
    created_by = "system"
    created_date = (start_date + timedelta(days=random.randint(0, (end_date - start_date).days))).strftime(
        '%Y-%m-%d %H:%M:%S')

    # 构建SQL插入语句
    insert_statement = f"""
INSERT INTO wimm.acct_vou_detail (id, created_by, created_date, last_modified_by, last_modified_date, acct_cls_code, acct_cls_name, amt, dr_cr, remark, voucher_no) 
VALUES ({i + 1}, '{created_by}', '{created_date}', '{created_by}', '{created_date}', '{account_code}', '{account_name}', {amount}, {dr_cr}, NULL, '{voucher_no}');
"""
    insert_statements.append(insert_statement)

# 打印生成的插入语句
# for statement in insert_statements:
#     print(statement)

# 写入到一个文件中
with open('/tmp/data.sql', 'w') as f:
    f.write('\n'.join(insert_statements))