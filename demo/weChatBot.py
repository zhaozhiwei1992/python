"""
https://wxpy.readthedocs.io/zh/latest/bot.html
https://www.cnblogs.com/sui776265233/p/10590628.html
"""
# 将登录信息保存下来，就不用每次都扫二维码
# bot = Bot(cache_path=True) # 必须先登录过一次以后才可以使用缓存

from wxpy import *

bot = Bot()


def test():
    # 机器人账号自身
    myself = bot.self

    # 向文件传输助手发送消息
    bot.file_helper.send('Hello from wxpy!')


def girlAndBoyProportion():
    from pyecharts.charts import Pie
    import webbrowser

    friends = bot.friends()
    # 拿到所有朋友对象，放到列表里
    attr = ['男朋友', '女朋友', '未知性别']
    value = [0, 0, 0]
    for friend in friends:
        if friend.sex == 1:  # 等于1代表男性
            value[0] += 1
        elif friend.sex == 2:  # 等于2代表女性
            value[1] += 1
        else:
            value[2] += 1

    pie = Pie("朋友男女比例")
    pie.add("", attr, value, is_label_show=True)
    # 图表名称str，属性名称list，属性所对应的值list，is_label_show是否现在标签
    pie.render('sex.html')  # 生成html页面
    # 打开浏览器
    webbrowser.open("sex.html")


if __name__ == '__main__':
    test()
    # girlAndBoyProportion()
