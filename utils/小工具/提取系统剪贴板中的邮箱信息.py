import pyperclip, re

"""
#将需要搜索的内容放入剪贴板
#读取剪贴板内容

指标集成申请 

发件人：赵志伟 <zhaozhiwei@szlongtu.com>	
时   间：2018年7月6日(星期五) 中午1:01	
收件人： 
zhuyan <zhuyan@szlongtu.com>; 胡鑫 <huxin@szlongtu.com>
抄   送：
刘洪昌 <liuhongchang@szlongtu.com>; 欧炫 <ouxuan@szlongtu.com>; 王栋 <wangdong@szlongtu.com>; 陈占涛 <chenzhantao@szlongtu.com>; 苑颖 <yuanying@szlongtu.com>; yinyuanfang <yinyuanfang@szlongtu.com>; renchunxin <renchunxin@szlongtu.com>

#手机号匹配正则表达式 ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9]+.[A-Za-z]{2,4}
"""
text = pyperclip.paste()
# 手机号匹配正则表达式
emailRegex = re.compile(r"""
([a-zA-Z0-9._%+-]+@[a-zA-Z0-9]+.[A-Za-z]{2,4}) 
""", re.VERBOSE)
result = emailRegex.findall(text)
if len(result) < 1:
    print("请将要匹配的数据复制到系统剪贴板")
    exit(0)
print(result)
# 结果写出到剪贴板
pyperclip.copy("\n".join(result))
print("数据已写入到系统剪贴板。。。。, 找个地儿粘贴")
