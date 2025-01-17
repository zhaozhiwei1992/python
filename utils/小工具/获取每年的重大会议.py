# 做一个全球会议信息获取的python程序， 通过json形式输出即可， 具体获取的地方可以使用爬虫或者api
# 获取的会议包括： 会议名称, 会议时间, 会议地点, 会议主题, 会议类型, 会议级别, 会议组织者, 会议简介, 会议官网
# 会议类型包括：  政策会议
# 会议级别包括： 国家级, 省级
# 会议组织者包括： 政府, 企业
# 会议简介包括： 会议简介, 会议总结

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

class ConferenceCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.sources = {
            '新华网': 'http://www.xinhuanet.com/politics/',
            '人民网': 'http://politics.people.com.cn/',
            '中国政府网': 'http://www.gov.cn/xinwen/index.htm'
        }

    def crawl_xinhuanet(self):
        conferences = []
        try:
            response = requests.get(self.sources['新华网'], headers=self.headers)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # 查找新闻列表
                news_items = soup.find_all('div', class_='news-item')
                
                for item in news_items:
                    title = item.find('h3')
                    if title and self._is_conference_news(title.text):
                        conference = {
                            "name": title.text.strip(),
                            "time": self._extract_date(item),
                            "location": self._extract_location(item),
                            "topic": self._extract_topic(item),
                            "type": "政策会议",
                            "level": self._determine_level(title.text),
                            "organizer": "政府",
                            "description": item.find('p', class_='summary').text.strip() if item.find('p', class_='summary') else "",
                            "website": item.find('a')['href'] if item.find('a') else ""
                        }
                        conferences.append(conference)
                
                time.sleep(1)  # 添加延迟，避免频繁请求
        except Exception as e:
            print(f"爬取新华网失败: {str(e)}")
        
        return conferences

    def _is_conference_news(self, title):
        # 关键词过滤，判断是否是会议新闻
        keywords = ['会议', '大会', '座谈会', '研讨会', '全会']
        return any(keyword in title for keyword in keywords)

    def _extract_date(self, item):
        # 提取日期
        date_elem = item.find('span', class_='date')
        if date_elem:
            return date_elem.text.strip()
        return datetime.now().strftime("%Y-%m-%d")

    def _extract_location(self, item):
        # 提取地点（这需要根据具体新闻内容分析）
        locations = ['北京', '上海', '广州', '深圳']
        for loc in locations:
            if loc in str(item):
                return loc
        return "待定"

    def _extract_topic(self, item):
        # 提取主题（从新闻标题或内容中提取）
        if item.find('p', class_='summary'):
            return item.find('p', class_='summary').text[:20] + "..."
        return "暂无主题"

    def _determine_level(self, title):
        # 根据标题关键词判断会议级别
        national_keywords = ['全国', '中央', '国家']
        provincial_keywords = ['省', '自治区', '直辖市']
        
        if any(keyword in title for keyword in national_keywords):
            return "国家级"
        elif any(keyword in title for keyword in provincial_keywords):
            return "省级"
        return "其他"

    def save_to_json(self, data, filename="conferences.json"):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    crawler = ConferenceCrawler()
    conferences = crawler.crawl_xinhuanet()
    crawler.save_to_json(conferences)
    print(f"已保存{len(conferences)}个会议信息到conferences.json")

if __name__ == "__main__":
    main()





