import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import random

# 用于将游戏数据爬至excel文件中，200个游戏
class SteamChinaScraper:
    '''steam中国'''
    def __init__(self):
        self.url = "https://store.steamchina.com/search/"
        self.headers = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0"
    }


    def _extract_review_info(self, review_row) -> dict:
        """提取评价信息"""
        review_elem = review_row.find('span', itemprop = 'description')
        if not review_elem:
            return {'score': '无评价', 'text': '', }
        else :
            review_text = review_elem.text.strip()
            score = review_row.find('span', class_="nonresponsive_hidden responsive_reviewdesc").text.strip()
            match = re.search(r'(\d+)%', score)
            if match:
                score = match.group(1) + '%'
            else:
                score = '无评价'
            return {'score': score, 'text': review_text }
       
    def _extract_price_info(self, price_row):
            """提取价格信息"""
            # 查找价格元素
            price_elem = price_row.find('div', class_='discount_final_price')
            
            if not price_elem:
                return {'price': '未知', 'currency': '', 'is_free': False}
            
            price_text = price_elem.text.strip()
            
            # 检查是否免费
            is_free = '免费' in price_text or 'Free' in price_text
            
            # 尝试提取货币和金额
            currency = ''
            price_value = ''
            
            if not is_free:
                # 尝试匹配价格模式，如 "¥ 103"
                price_match = re.search(r'([¥$€£])\s*([\d,.]+)', price_text)
                if price_match:
                    currency = price_match.group(1)
                    price_value = price_match.group(2)
            
            return {
                'price': price_text,
                'currency': currency,
                'price_value': price_value,
                'is_free': is_free
            }


    def _extract_game_info(self, row) ->list:
        '''提取数据'''
        # 游戏ID
        app_id = row.get('data-ds-appid', '')
        # 游戏名称
        app_name = row.find('span', class_='title')
        # 价格提取
        price_info = self._extract_price_info(row)
        # 游戏图片
        game_img = row.find('img','')['src']
        # 游戏url
        game_url = row.get('href','')
        # 评价提取
        page = requests.get(game_url, headers=self.headers)
        soup = BeautifulSoup(page.text, 'html.parser')
       
        review_info = self._extract_review_info(soup)
        
        return [app_id, app_name.text, review_info, price_info, game_img, game_url]

    def parse_html(self, url=None, headers=None) -> list:
        '''抓取搜索栏游戏数据'''
        games_data = []
        page_number = 0
        while len(games_data) < 500:
            # 构建分页URL
            time.sleep(random.uniform(1, 5))
            page_url = f"{self.url}?page={page_number}"
            resp = requests.get(page_url, headers=headers)
            page = BeautifulSoup(resp.text, 'html.parser')
            game_rows = page.find_all('a', class_="search_result_row", limit=50)
            print(f"正在抓取第 {page_number} 页数据")
            print(f"当前页面游戏条目数：{len(game_rows)}")
            if not game_rows:
                break  # 如果没有找到游戏条目，退出循环
            for row in game_rows:
                game_info = self._extract_game_info(row)  # 解析数据
                if game_info not in games_data:
                    games_data.append(game_info)
            page_number += 1
            print(f"已抓取 {len(games_data)} / 500 个游戏数据")
        return games_data[:500]  # 确保返回最多500个游戏数据

if __name__ == '__main__':
    scraper = SteamChinaScraper()
    data = scraper.parse_html()
    print(1)
    row = ["游戏ID", "游戏名称", "评价信息", "价格信息", "游戏图片", "游戏url"]
    df = pd.DataFrame(data, columns=row)
    df.to_excel("Games_Info.xlsx", index=False)