import pandas as pd
import os
import glob

# 指定目标目录路径
target_dir = '/home/zhaozhiwei/Downloads/美团'
# 修改glob模式，包含完整路径
files = glob.glob(os.path.join(target_dir, '*账户提现记录*.xlsx'))

total_amount = 0
print('美团提现金额统计：')
print('=' * 50)
print(files)

for f in sorted(files):
    df = pd.read_excel(f)
    # 查找提现金额列
    amount_col = None
    for col in df.columns:
        if '提现金额' in col or 'amount' in col.lower():
            amount_col = col
            break
    
    if amount_col:
        amount_sum = df[amount_col].sum()
        total_amount += amount_sum
        print(f'{os.path.basename(f)}: {amount_sum:.2f} 元')
    else:
        print(f'{os.path.basename(f)}: 未找到金额列')

print('=' * 50)
print(f'总计: {total_amount:.2f} 元')
