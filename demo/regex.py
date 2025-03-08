import re
regex = re.compile(r"(\d\d\d)-(\d\d\d\d)")
mc = regex.search("my phone 666-6688")
print(mc.group())
print("第一组匹配: " + mc.group(1))
print(mc.groups())

"""贪心匹配， 非贪心匹配"""
greedyRegex = re.compile(r"(Hello){3,5}")
greedyRegexMc = greedyRegex.search("HelloHelloHelloHelloHelloHello")
print(greedyRegexMc.group())

nogreedyRegex = re.compile(r"(Hello){3,5}?")
nogreedyRegexMc = nogreedyRegex.search("HelloHelloHelloHelloHelloHello")
print(nogreedyRegexMc.group())

regex = re.compile(r"\(\)|\[\]|\{\}|""") 
mc = regex.search('"([]"')
print(mc != None)

text=(" <think>\n今天，我遇到了一个用户请求：“查询已支付数据”。他们可能需要了解在某个数据库中如何获取已支付的信息。首先，我要确认上下文中的相关信息，特别是表名和字段描述。\n\n查看了提供的表格结构，发现用户提到了“pay_voucher_bill”这个表，里面有支付凭证的数据。每个字段都有对应的类型信息，比如“fund_type_code”是资金性质的代码，“billcode”是凭证号等等。\n\n接下来，我需要理解“已支付数据”的具体含义。通常这意味着有特定凭证记录了支付情况，可能包括金额、支出功能和支付日期等。根据上下文中的描述，“支付明细”字段可以提供详细的支付信息，而“xpaydate”字段则是支付的日期。\n\n然后，我会考虑如何在SQL中表达这一点。首先，需要选择正确的表名“pay_voucher_bill”。接下来，确定查询字段：金额（amt）、支出功能分类（exp_func_code）和支付日期（xpaydate）。用户可能希望获取这些字段的数据范围，所以我会添加条件：金额不为空且支付日期不为空。\n\n最后，我会编写一个SQL语句，确保输出格式正确，只返回一条结果，并且字段名称准确对应上下文中的描述。这样，用户就可以在数据库中轻松找到已支付的凭证数据了。\n</think>\n\n查询已支付数据\n\n{sql: \"SELECT amt, exp_func_code, xpaydate FROM pay_voucher_bill WHERE amt <> * AND xpaydate <> *\"}\n\n其中：\n- `amt`：金额\n- `exp_func_code`：支出功能分类代码\n- `xpaydate`：支付日期")
sql_pattern = r"```sql.*```"
sql_match = re.search(sql_pattern, text, re.DOTALL)
sql_content = sql_match.group(0).strip()  # 获取匹配的内容并去除多余空格
print("提取的 SQL 语句：")
print(sql_content.replace("```sql", "").replace("```", "").strip())