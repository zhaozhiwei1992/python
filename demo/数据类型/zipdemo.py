# -*- coding:utf-8 -*-

# users=[
#     {'name':'zhangsan', 'age':18},
#     {'name':'lisi', 'age':16},
#     {'name':'wangwu', 'age':14},
#     {'name':'zhaoliu', 'age':13},
#     {'name':'maqi', 'age':10}
# ]

if __name__ == "__main__":
    prices={'apple': 8, 'orige':6, 'banana': 18}
    print(prices)

    cheap_fruit = min(zip(prices.values(), prices.keys()))
    # print(min_fruit[1])
    # print(min_fruit[0])
    print('最便宜的是: %s,价格是 %d' %(cheap_fruit[1],cheap_fruit[0]))

    expensive_fruit = max(zip(prices.values(), prices.keys()))
    print('最贵的是: %s,价格是 %d' %(expensive_fruit[1],expensive_fruit[0]))

    # 通过原生实现比较
    cheap_fruit2 = min(prices, key=lambda k: prices[k])
    # print(cheap_fruit2) orige
    #  如果需要获取value还需要在这个基础上 prise["orige"]   得到6, 不如zip方便
