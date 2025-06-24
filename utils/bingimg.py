#!/usr/bin/python
import urllib.request
import requests
import re
import time
import os
import json


def save_img(img_url, dirname):
    # 保存图片到磁盘文件夹dirname
    try:
        if not os.path.exists(dirname):
            print('文件夹', dirname, '不存在，重新建立')
            # os.mkdir(dirname)
            os.makedirs(dirname)
        # 获得图片文件名，包括后缀
        regex = re.compile('\?[^&]*')
        timestr = time.strftime('%Y%m%d', time.localtime(time.time()))
        basename = str(regex.search(img_url).group()).replace("?id=", "_")
        basename = timestr + basename
        # basename = os.path.basename(img_url)
        # 拼接目录与文件名，得到图片路径
        filepath = os.path.join(dirname, basename)
        if (os.path.exists(filepath)):
            print("文件已经存在")
            return
        # print(filepath)
        # 下载图片，并保存到文件夹中
        urllib.request.urlretrieve(img_url, filepath)
    except IOError as e:
        print('文件操作失败', e)
    except Exception as e:
        print('错误 ：', e)
    print("Save", filepath, "successfully!")

    return filepath


# 请求网页，跳转到最终 img 地址, 默认sinaapp的地址提示网站故障
def get_img_url(raw_img_url="https://area.sinaapp.com/bingImg/"):
    """
    也可以 访问https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US
    自己解析json, 凭借成为真实url
    {

    "images": [
        {
            "startdate": "20210204",
            "fullstartdate": "202102041600",
            "enddate": "20210205",
            "url": "/th?id=OHR.TheWave_ZH-CN4856809836_1920x1080.jpg&rf=LaDigue_1920x1080.jpg&pid=hp",
            "urlbase": "/th?id=OHR.TheWave_ZH-CN4856809836",
            "copyright": "波浪谷中的砂岩层和积水，亚利桑那州朱红悬崖国家纪念碑 (© Dennis Frates/Alamy)",
            "copyrightlink": "https://www.bing.com/search?q=%E6%9C%B1%E7%BA%A2%E6%82%AC%E5%B4%96%E5%9B%BD%E5%AE%B6%E7%BA%AA%E5%BF%B5%E7%A2%91&form=hpcapt&mkt=zh-cn",
            "title": "",
            "quiz": "/search?q=Bing+homepage+quiz&filters=WQOskey:%22HPQuiz_20210204_TheWave%22&FORM=HPQUIZ",
            "wp": true,
            "hsh": "ea6d5982b00ab676dd7a365a9e614e45",
            "drk": 1,
            "top": 1,
            "bot": 1,
            "hs": [ ]
        }
    ],
    "tooltips": {
        "loading": "Loading...",
        "previous": "Previous image",
        "next": "Next image",
        "walle": "This image is not available to download as wallpaper.",
        "walls": "Download this image. Use of this image is restricted to wallpaper only."
    }

}
    """
    response = requests.get(raw_img_url)
    responseObj = json.loads(response.text)
    img_url = 'https://cn.bing.com' + responseObj['images'][0]['url']
    # 高清图/th?id=OHR.DelicateArch_ZH-CN8971667580_UHD.jpg&rf=LaDigue_UHD.jpg&pid=hp将返回url中的1920x1080替换为UHD即可，按需打开。
    # img_url = img_url.replace('1920x1080', 'UHD')
    # img_url = response.url  # 得到图片文件的网址
    # print('img_url:', img_url)
    return img_url


# 设置图片绝对路径 filepath 所指向的图片为壁纸
def set_img_as_wallpaper(filepath):
    pass
    # ctypes.windll.user32.SystemParametersInfoW(20, 0, filepath, 0)


if __name__ == "__main__":
    dirname = os.environ['HOME'] + "/Pictures/bingImg"  # 图片要被保存在的位置
    img_url = get_img_url('https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN')
    filepath = save_img(img_url, dirname)  # 图片文件的的路径
