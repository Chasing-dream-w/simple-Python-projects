# 提取游戏简介
import pandas as pd
import requests
from bs4 import BeautifulSoup
from spider_get_game import SteamChinaScraper
import time
import random
scraper = SteamChinaScraper()


games_data = pd.read_excel('./games_data/Games_Info.xlsx')
games_introduction = []

i = 0
for index, row in games_data.iterrows():
    time.sleep(random.uniform(0, 2))
    game_url = row['游戏url']
  
    responser = requests.get(game_url, headers=scraper.headers)
    soup = BeautifulSoup(responser.text, 'html.parser')
    game_description = soup.find('div', class_ = 'game_area_description')
    print(row['游戏名称'], i,)
    i+=1
    if game_description is None:
        game_description = '暂无简介'
    else:
        game_description = game_description.text.strip()
    games_introduction.append(game_description)

games_data['游戏简介'] = games_introduction
games_data.to_excel('./games_data/Games_Info.xlsx', index=False)
print('游戏简介提取完成')