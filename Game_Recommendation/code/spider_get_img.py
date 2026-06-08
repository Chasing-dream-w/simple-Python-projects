# 下载游戏图片，价格转化，评分转化，导出游戏类型
import pandas as pd
import requests
import os
import time
import random
import ast
from bs4 import BeautifulSoup
from spider_get_game import SteamChinaScraper
import re

scarper = SteamChinaScraper()

class GamesDisposer:
    def __init__(self, path):
        self.path = path

    def downloda_image(self, url, path, game_id):
        if not os.path.exists(path):
            os.makedirs(path)
        response = requests.get(url)
    # 检查请求是否成功
        if response.status_code == 200:
            with open(os.path.join(path, str(game_id) + '.jpg'), 'wb') as f:
                f.write(response.content)


    # 获取游戏类型
    def get_game_type(self, game_url):  
        headers = scarper.headers
        response = requests.get(game_url, headers=headers)
        page = BeautifulSoup(response.text, 'html.parser')
        game_types = page.find_all('a', class_='app_tag')
        game_type_name = [game_type.text.strip() for game_type in game_types]
        if len(game_type_name) > 10:
            return game_type_name[:10]
        else:
            return game_type_name
    
    # 获取游戏标签
    def get_game_tag(self, game_url):
        headers = scarper.headers
        response = requests.get(game_url, headers=headers)
        page = BeautifulSoup(response.text, 'html.parser')
        elements = page.find_all('a', href=re.compile(r'https://store.steamchina.com/genre/'))
        if len(elements) < 3:
            return '非游戏本体'
        return elements[2].text.strip()
    # 价格转化

    def modify_price(self, price):
        if price['price'] == '免费':
            return '0'
        elif price['price'] == '未知':
            return '0'
        else:
            return price['price'][1:]


    def modify_coment(self, comment):
        score = comment['score'][:2]
        level = comment['text']
        return score, level


games_info = pd.read_excel('./games_data/Games_Info.xlsx')
data_path = './games_data'

if __name__ == '__main__':
    
    disposer = GamesDisposer(data_path)
    for index, row in games_info.iterrows():
        url = row['游戏图片']
        game_id = row['游戏ID']
        path = './img'
        if os.path.exists(os.path.join(path, str(game_id) + '.jpg')):
            continue
        disposer.downloda_image(url, path, game_id)
    print('图片 下载完成')
    games_type = []

    """下载游戏类型"""
    if '游戏类型' not in games_info.columns:
        for index, row in games_info.iterrows():
            url = row['游戏url']
            time_wait = 3*random.random()
            time.sleep(time_wait)
            print("等待时间：", time_wait, "正在下载:", row['游戏名称'])
            type = disposer.get_game_type(url)
            print(type)
            games_type.append(type)
        games_info['游戏类型'] = games_type
        games_info.to_excel('./games_data/Games_Info.xlsx', index=False)
        print('游戏类型 下载完成')
    games_info = pd.read_excel('./games_data/Games_Info.xlsx')
    if games_info['评分'].isnull().all():
        """价格,评分 转化"""
        price_ex = []
        comment_ex = []
        level_ex = []
        for index, row in games_info.iterrows():
            price = row['价格信息']
            price = ast.literal_eval(price)
            modified_price = disposer.modify_price(price)
            game_text = row['评价信息']
            game_text = ast.literal_eval(game_text)
            score, level = disposer.modify_coment(game_text)
            price_ex.append(modified_price)
            comment_ex.append(score)
            level_ex.append(level)
        games_info['价格'] = price_ex
        games_info['评分'] = comment_ex
        games_info['评价(中文)'] = level_ex
        games_info.to_excel('./games_data/Games_Info.xlsx', index=False)
        print('价格,评分 转化完成')
    
    if '游戏标签' not in games_info.columns:
        """下载游戏标签"""
        games_tag = []
        for index, row in games_info.iterrows():
            url = row['游戏url']
            time.sleep(random.uniform(2,5))
            print("正在下载:", row['游戏名称'])
            tag = disposer.get_game_tag(url)
            print(tag)
            games_tag.append(tag)
        games_info['游戏标签'] = games_tag
        games_info.to_excel('./games_data/Games_Info.xlsx', index=False)
        print('游戏标签 下载完成')
        # games_tag正则化
        games_info = pd.read_excel('./games_data/Games_Info.xlsx')
        for index, row in games_info.iterrows():
            games_tag = row['游戏标签']
            cleaned = re.sub(r'[\u200b\u200c\u200d\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2060\u2061\u2062\u2063\u2064\ufeff]', '', games_tag)
            games_info.loc[index, '游戏标签'] = cleaned
        games_info.to_excel('./games_data/Games_Info.xlsx', index=False)
        print('游戏标签 正则化完成')