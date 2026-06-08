# 初始化数据库
import pandas as pd
from data_base import Database


# 删除数据库
def drop_database(my_db):
    my_db.cur.execute("drop games if exists games;")
    my_db.conn.commit()


def init_games_info(my_db):
    # 创建Games表
    my_db.cur.execute("create table if not exists Games(" \
                      " game_id int primary key," \
                      " game_name varchar(255) unique," \
                      " game_type varchar(255)," \
                      " game_price float," \
                      " game_score int, " \
                      " game_comment varchar(255)," \
                      " game_tag varchar(255),"
                      " game_introduction text);")
    """游戏ID 游戏名称 游戏类型 游戏价格 游戏评分 游戏评论 游戏标签 游戏简介"""
    my_db.conn.commit()

def init_players_info(my_db):
    # 创建Players表
    my_db.cur.execute("create table if not exists Players(" \
                      " player_id int primary key," \
                      " user_name varchar(255)," \
                      " user_account varchar(255)," \
                      " user_password varchar(255)," \
                      " user_email varchar(255)," \
                      " user_games_list varchar(255)," \
                      " user_total_play_time int," \
                      " user_total_value float);")
    """用户ID 用户名 用户账号 用户密码 用户邮箱 游戏列表 游戏总时长 游戏总价值"""
    my_db.conn.commit()


def init_players_and_games_info(my_db):
    # 创建Players_And_Games表
    my_db.cur.execute("create table if not exists Players_And_Games(" \
                      " player_id int," \
                      " game_id int, " \
                      " achievement_number int, " \
                      " play_time int, " \
                      " last_week_play_time int," \
                      " primary key(player_id, game_id), " \
                      " foreign key(player_id) references Players(player_id));")
    """玩家id 游戏id 成就数目 游玩时长(小时) 近一周游玩时间(小时)"""
    my_db.conn.commit()

def init_competitions_info(my_db):
    # 创建Competitions表
    my_db.cur.execute("create table if not exists Competitions(" \
                      " competition_id int primary key," \
                      " competition_type int," \
                      " game_name varchar(255), " \
                      " team1 varchar(255)," \
                      " team2 varchar(255)," \
                      " competition_date date);")
    """赛事id 赛事级别 游戏名称 队伍1 队伍2 赛事日期"""
    my_db.conn.commit()

def init_games_relations(my_db):
    # 创建游戏相似度表
    my_db.cur.execute("create table if not exists Games_Relations(" \
                      " game1_id int," \
                      " game2_id int, " \
                      " similarity_score float, " \
                      " foreign key(game1_id) references Games(game_id)," \
                      " foreign key(game2_id) references Games(game_id)," \
                      " primary key(game1_id, game2_id));") 
    """游戏1 游戏2 相似度分数"""
    my_db.conn.commit()

def init_admin(my_db):
    # 创建管理员表
    my_db.cur.execute("create table if not exists Admin(" \
                      " admin_id int primary key," \
                      " admin_account varchar(255)," \
                      " admin_password varchar(255));")
    """管理员id 管理员账号 管理员密码"""
    my_db.conn.commit()


def init_post(my_db):
    # 创建社区交流表
    my_db.cur.execute("create table if not exists Posts("\
                      " player_id int,"\
                      " post_id int,"\
                      " post_topic text,"\
                      " sector varchar(255),"\
                      " content text,"\
                      " likes int,"\
                      " comments int,"\
                      " primary key(player_id, post_id));")
    """用户id 帖子id 帖子主题 帖子分区 帖子内容 点赞量 评论量"""
    my_db.conn.commit()


def init_comments(my_db):
    # 创建评论表
    my_db.cur.execute("CREATE TABLE IF NOT EXISTS comments ("
                      "comment_id INT AUTO_INCREMENT PRIMARY KEY,"
                      "post_id INT NOT NULL,"
                      "player_id INT NOT NULL,"
                      "content TEXT NOT NULL,"
                      "create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
                      "likes INT DEFAULT 0);")
    """用户id 帖子id 评论内容"""
    my_db.conn.commit()


if __name__ == '__main__':
    games_info_1 = pd.read_excel('../games_data/Games_Info.xlsx')
    my_db = Database()
    
    # 初始化
    init_players_info(my_db)
    init_games_info(my_db)
    init_players_and_games_info(my_db)
    init_games_relations(my_db)
    init_competitions_info(my_db)
    init_admin(my_db)
    init_post(my_db)
    init_comments(my_db)
    my_db.close()
    print('数据库初始化完成！')
