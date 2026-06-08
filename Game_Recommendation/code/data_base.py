# 数据库处理逻辑
import mysql.connector
import pandas as pd
import ast


class Database:
    def __init__(self):
        # 链接数据库
        self.conn = mysql.connector.connect(
            port=3306,
            host='127.0.0.1',  # 本地测试
            user='root',
            password='114514',
            charset='utf8mb4'
        )
        self.cur = self.conn.cursor(buffered=True)
        # 创建数据库
        self.cur.execute("create database if not exists Games;")
        self.cur.execute("use Games;")

    def close(self):
        # 关闭数据库连接
        self.cur.close()
        self.conn.close()

    # 添加玩家信息
    """用户ID 用户名 用户账号 用户密码 用户邮箱 游戏列表 游戏总时长 游戏总价值"""

    def Add_Players_Info(self, player_id, user_name, user_account, user_password,
                         user_email, user_games_list, user_total_play_time=0, user_total_value=0):
        # 检查是否存在该用户
        sql = "select * from Players " \
              " where player_id = %s;"
        val = (player_id,)
        self.cur.execute(sql, val)
        result = self.cur.fetchall()
        if len(result) > 0:
            print("该用户已存在")
            return
        sql = """insert into Players(player_id, user_name, user_account, user_password,
                user_email,user_games_list, user_total_play_time, user_total_value)
                values(%s, %s, %s, %s, %s, %s, %s, %s);"""
        val = (
        player_id, user_name, user_account, user_password, user_email, str(user_games_list), user_total_play_time,
        user_total_value)
        self.cur.execute(sql, val)
        self.conn.commit()

    # 添加游戏信息
    """游戏ID 游戏名称 游戏类型 游戏价格 游戏评分 游戏评论 游戏标签 游戏介绍"""

    def Add_Games_Info(self, game_id, game_name, game_type, game_price, game_score, game_comment, game_tag,
                       game_introduction):
        # 检查是否存在该游戏
        sql = "select * from Games " \
              "where game_id = %s;"
        val = (game_id,)
        self.cur.execute(sql, val)
        result = self.cur.fetchall()
        if len(result) > 0:
            print("该游戏已存在")
            return
        if game_price == '未上架':
            game_price = 0
        if game_type is None:
            game_type = "未分类"
        if pd.isna(game_comment):
            game_comment = "暂无评价"
        sql = """insert into Games(
                game_id, game_name, game_type, game_price, game_score, game_comment, game_tag, game_introduction)
                values(%s, %s, %s, %s, %s, %s, %s, %s)"""
        val = (
        game_id, game_name, str(game_type), float(game_price), game_score, game_comment, game_tag, game_introduction)
        self.cur.execute(sql, val)
        self.conn.commit()

    # 添加玩家-游戏交互信息
    """玩家id 游戏id 成就数目 游玩时长(小时) 近一周游玩时间(小时)"""

    def Add_Players_And_Games_Info(self, player_id, game_id, achievement_number, play_time, last_week_play_time):
        # 检查是否存在该用户-游戏交互信息
        sql = "select * from Players_And_Games " \
              "where player_id = %s and game_id = %s;"
        val1 = (player_id, game_id)
        self.cur.execute(sql, val1)
        result = self.cur.fetchall()
        if len(result) > 0:
            print("该用户-游戏交互信息已存在")
            return
        sql = """insert into Players_And_Games(
                player_id, game_id, achievement_number, play_time, last_week_play_time)
                values(%s, %s, %s, %s, %s);"""
        val = (player_id, game_id, achievement_number, play_time, last_week_play_time)
        self.cur.execute(sql, val)
        self.conn.commit()

    # 添加赛事信息
    """赛事id 赛事级别 游戏名称 队伍1 队伍2 赛事日期"""

    def Add_Competitions_Info(self, competition_id, competition_type, game_name, team1, team2, competition_date):
        sql = """insert into Competitions(
                competition_id, competition_type, game_name, team1, team2, competition_date)
                values(%s, %s, %s, %s, %s, %s);"""
        val = (competition_id, competition_type, game_name, team1, team2, competition_date)
        self.cur.execute(sql, val)
        self.conn.commit()

    # 添加游戏相似度
    """游戏1 游戏2 相似度分数"""

    def Add_Game_Similarity(self, game1_id, game2_id, similarity_score):
        sql = """insert into Games_Relations(
                game1_id, game2_id, similarity_score)
                values (%s, %s, %s);"""
        val = (game1_id, game2_id, similarity_score)
        self.cur.execute(sql, val)
        self.conn.commit()

    # 添加管理员
    """管理员id 管理员账号 管理员密码"""

    def Add_Admin(self, admin_id=0, admin_count='20251226', admin_password='123456'):
        # 检查是否存在管理员
        sql = "select * from Admin " \
              "where admin_id = %s and admin_password = %s;"
        val = (admin_id, admin_password)
        self.cur.execute(sql, val)
        result = self.cur.fetchall()
        if len(result) > 0:
            print("管理员已存在")
            return
        # 添加管理员
        sql = """insert into Admin( 
                admin_id, admin_account, admin_password)
                values (%s, %s, %s);"""
        val = (admin_id, admin_count, admin_password)
        self.cur.execute(sql, val)
        self.conn.commit()

    # 更新用户信息
    def Update_Player_Info(self, key, value, player_id):
        # 修改用户名
        if key == 0:
            sql = """update Players set user_name = %s where player_id = %s;"""
            val = (value, player_id)
            self.cur.execute(sql, val)
        # 修改用户密码
        elif key == 1:
            sql = """update Players set user_password = %s where player_id = %s;"""
            val = (value, player_id)
            self.cur.execute(sql, val)
        # 修改用户邮箱
        elif key == 2:
            sql = """update Players set user_email = %s where player_id = %s;"""
            val = (value, player_id)
            self.cur.execute(sql, val)
        # 修改用户游戏列表
        elif key == 3:
            sql = """update Players set user_games_list = %s where player_id = %s;"""
            val = (value, player_id)
            self.cur.execute(sql, val)
        # 修改用户总游玩时长
        elif key == 4:
            sql = """update Players set user_total_play_time = %s where player_id = %s;"""
            val = (value, player_id)
            self.cur.execute(sql, val)
        # 修改用户总价值
        elif key == 5:
            sql = """update Players set user_total_value = %s where player_id = %s;"""
            val = (value, player_id)
            self.cur.execute(sql, val)
        else:
            print("检查输入的key值, 更新失败")
        self.conn.commit()
        print("用户信息更新成功")

    # 导入游戏数据
    def Data_To_SQL_Add_Games_Info(self, data):
        data = data.values.tolist()
        for i in range(len(data)):
            game_id = int(data[i][0])
            game_name = data[i][1]
            game_type = ast.literal_eval(data[i][6])
            game_price = data[i][7]
            if data[i][8] == '无评' or data[i][8] == '无评价':
                game_score = 0
            else:
                game_score = int(data[i][8])
            game_comment = data[i][9]
            game_introduction = data[i][10]
            game_tage = data[i][11]
            self.Add_Games_Info(game_id, game_name, game_type, game_price, game_score, game_comment, game_tage,
                                game_introduction)
            print(i)

    # 添加用户信息
    def Data_To_SQL_Add_Players_Info(self, data):
        data = data.values.tolist()
        # 先把初始数据加入
        for i in range(len(data)):
            player_id = int(data[i][0])
            user_name = data[i][1]
            user_account = data[i][2]
            user_password = data[i][3]
            user_email = data[i][4]
            user_games_list = ast.literal_eval(data[i][5])
            user_total_play_time = 0
            user_total_value = 0
            self.Add_Players_Info(player_id, user_name, user_account, user_password, user_email, user_games_list,
                                  user_total_play_time, user_total_value)

    def Update_Player_Info_And_Total_Value_And_Total_Play_Time(self, data):
        data = data.values.tolist()
        # 更新计算游戏总价值+总时长
        for i in range(len(data)):
            games_list = ast.literal_eval(data[i][5])
            user_id = int(data[i][0])
            total_value = 0
            total_play_time = 0
            for game_id in games_list:
                game_id = int(game_id)
                print(game_id)
                sql1 = """select game_price from Games where game_id = %s;"""
                val = (game_id,)
                self.cur.execute(sql1, val)
                game_price = self.cur.fetchone()[0]
                total_value += game_price
                sql2 = """select play_time from Players_And_Games where player_id = %s and game_id = %s;"""
                val = (user_id, game_id)
                self.cur.execute(sql2, val)
                play_time = self.cur.fetchone()[0]
                total_play_time += play_time
            self.Update_Player_Info(5, total_value, user_id)
            self.Update_Player_Info(4, total_play_time, user_id)

    # 将交互数据导入数据库
    def Data_To_SQL_Add_Games_And_Players_Info(self, data):
        data = data.values.tolist()
        for i in range(len(data)):
            for _ in range(len(data[i])):
                user_id = int(data[i][0])
                game_id = int(data[i][1])
                achievement_number = int(data[i][2])
                play_time = int(data[i][3])
                last_week_play_time = int(data[i][4])
                self.Add_Players_And_Games_Info(user_id, game_id, achievement_number, play_time, last_week_play_time)
        print("交互导入数据成功")

    # 导入赛事数据
    def Data_To_SQL_Add_Competitions_Info(self, data):
        pass

    # 验证用户登录信息
    def Vertify_User_Login_Info(self, user_account, user_password):
        sql = """select * from Players where user_account = %s and user_password = %s;"""
        val = (user_account, user_password)
        self.cur.execute(sql, val)
        result = self.cur.fetchall()
        if len(result) > 0:
            return True
        else:
            return False

    # 统计游戏tag数量，并返回tag列表
    def Get_Game_Tag_List(self):
        sql = """select game_tag from Games;"""
        self.cur.execute(sql)
        result = self.cur.fetchall()
        tag_list = []
        tags_number = 0
        for i in range(len(result)):
            if result[i][0] not in tag_list:
                tag_list.append(result[i][0])
                tags_number += 1
        return tag_list, tags_number

    # tag标签修正
    def Modify_Game_Tag(self):
        sql = """update games set game_tag = case when char_length(game_tag) <=2
              then concat(game_tag,'游戏') else game_tag end;"""
        self.cur.execute(sql)
        self.conn.commit()
        print("游戏标签修正成功")

    # 根据游戏id返回游戏详情数据
    def Get_Game_Info_By_Id(self, id):
        sql = """select * from Games where game_id = %s;"""
        val = (id,)
        self.cur.execute(sql, val)
        result = self.cur.fetchall()
        return result

    # 根据tag返回游戏列表
    def Get_Game_List_By_Tag(self, tag):

        sql = """select game_id, game_name, game_price, game_score from Games where game_tag = %s;"""
        val = (tag,)
        self.cur.execute(sql, val)
        result = self.cur.fetchall()
        return result

    # 返回游戏的id 名称 tag price score
    def Get_Game_Info_No_Params(self):
        sql = """select game_id, game_name, game_tag, game_price, game_score from Games;"""
        self.cur.execute(sql)
        result = self.cur.fetchall()
        return result

    # 游戏库首页显示内容为前80个游戏
    def Get_Game_List_For_Home(self):
        sql = """select game_id, game_name, game_tag, game_price, game_score from Games limit 80;"""
        self.cur.execute(sql)
        result = self.cur.fetchall()
        return result

    # 返回用户信息
    def Get_User_Info(self, user_account):
        sql = """select * from Players where user_account = %s;"""
        val = (user_account,)
        self.cur.execute(sql, val)
        result = self.cur.fetchone()
        return result

    # 返回游戏信息
    def Get_Game_Info(self, game_id):
        sql = """select game_name, game_price, game_score, game_comment from Games where game_id = %s;"""
        val = (game_id,)
        self.cur.execute(sql, val)
        result = self.cur.fetchone()
        return result

    # 返回用户-游戏交互信息
    def Get_User_And_Game_Info(self, user_id, game_id):
        sql = """select achievement_number, play_time, last_week_play_time from Players_And_Games where player_id = %s and game_id = %s;"""
        val = (user_id, game_id)
        self.cur.execute(sql, val)
        result = self.cur.fetchone()
        return result

    # 验证管理员登录信息
    def Vertify_Admin_Login_Info(self, admin_account, admin_password):
        sql = """select * from Admin where admin_account = %s and admin_password = %s;"""
        val = (admin_account, admin_password)
        self.cur.execute(sql, val)
        result = self.cur.fetchall()
        if len(result) > 0:
            return True
        else:
            return False

    # 检验用户是否存在
    def Vertify_User_Is_Exist(self, user_account):
        sql = """select * from Players where user_account = %s;"""
        val = (user_account,)
        self.cur.execute(sql, val)
        result = self.cur.fetchall()
        if len(result) > 0:
            return True
        else:
            return False

    # 检验游戏是否存在
    def Vertify_Game_Is_Exist(self, game_id):
        sql = """select * from Games where game_id = %s;"""
        val = (game_id,)
        self.cur.execute(sql, val)
        result = self.cur.fetchall()
        if len(result) > 0:
            return True
        else:
            return False

    # 获取用户个数
    def Get_User_Number(self):
        sql = """select count(*) from Players;"""
        self.cur.execute(sql)
        result = self.cur.fetchone()[0]
        return result

    # 删除游戏
    def Delete_Game_By_Id(self, game_id):
        sql = """delete from Games where game_id = %s;"""
        val = (game_id,)
        self.cur.execute(sql, val)
        self.conn.commit()
        print("游戏删除成功")
        return True

    # 删除赛事信息
    def Delete_Competition_By_Id(self, competition_id):
        sql = """delete from Competitions where competition_id = %s;"""
        val = (competition_id,)
        self.cur.execute(sql, val)
        self.conn.commit()
        print("赛事信息删除成功")

    # 查询游戏信息-id
    def Query_Game_Info_By_Id(self, game_id):
        sql = """select * from Games where game_id = %s;"""
        val = (game_id,)
        self.cur.execute(sql, val)
        result = self.cur.fetchone()
        return result

    # 查询游戏信息-名称
    def Query_Game_Info_By_Name(self, game_name):
        sql = """select * from Games where game_name = %s;"""
        val = (game_name,)
        self.cur.execute(sql, val)
        result = self.cur.fetchone()
        return result

    # 查询赛事信息-id
    def Query_Competition_Info_By_Id(self, competition_id):
        sql = """select * from Competitions where competition_id = %s;"""
        val = (competition_id,)
        self.cur.execute(sql, val)
        result = self.cur.fetchone()
        return result


    # 玩家发布帖子
    def Add_Post(self, player_id, post_topic, sector, content, likes=0, comments=0):
        """添加新帖子，自动生成 post_id"""
        # 获取当前最大帖子ID，新ID = 最大ID + 1
        sql_max = "SELECT IFNULL(MAX(post_id), 0) FROM posts"
        self.cur.execute(sql_max)
        max_id = self.cur.fetchone()[0]
        new_post_id = max_id + 1
        sql_insert = """INSERT INTO posts(post_id, player_id, post_topic, sector, content, likes, comments)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        val = (new_post_id, player_id, post_topic, sector, content, likes, comments)
        self.cur.execute(sql_insert, val)
        self.conn.commit()
        return new_post_id


    def Update_Post_Likes(self, post_id):
        """帖子点赞数 +1（根据 post_id）"""
        sql = "UPDATE posts SET likes = likes + 1 WHERE post_id = %s"
        val = (post_id,)
        self.cur.execute(sql, val)
        self.conn.commit()


    def Add_Comment(self, post_id, player_id, content):
        """添加评论，返回新评论ID"""
        sql = """INSERT INTO comments(post_id, player_id, content)
                 VALUES (%s, %s, %s)"""
        val = (post_id, player_id, content)
        self.cur.execute(sql, val)
        self.conn.commit()
        return self.cur.lastrowid


    def Increment_Post_Comment_Count(self, post_id):
        """帖子评论数 +1"""
        sql = "UPDATE posts SET comments = comments + 1 WHERE post_id = %s"
        val = (post_id,)
        self.cur.execute(sql, val)
        self.conn.commit()


    def Get_Comments_By_Post_Id(self, post_id):
        """获取帖子的所有评论，按时间正序"""
        sql = """
            SELECT c.comment_id, c.content, c.create_time, c.likes, pl.user_name
            FROM comments c
            JOIN Players pl ON c.player_id = pl.player_id
            WHERE c.post_id = %s
            ORDER BY c.create_time ASC
        """
        val = (post_id,)
        self.cur.execute(sql, val)
        return self.cur.fetchall()


    def Get_Next_Post_Id(self):
        """获取下一个可用的帖子ID"""
        sql = "SELECT IFNULL(MAX(post_id), 0) + 1 FROM posts"
        self.cur.execute(sql)
        return self.cur.fetchone()[0]


    def Get_All_Posts(self):
        """获取所有帖子，按时间倒序（需关联用户表获取作者名）"""
        sql = """
            SELECT p.post_id, p.post_topic, p.content, p.sector, 
                   p.likes, p.comments, p.create_time, pl.user_name
            FROM posts p
            JOIN Players pl ON p.player_id = pl.player_id
            ORDER BY p.create_time DESC
        """
        self.cur.execute(sql)
        return self.cur.fetchall()


    def Insert_Post(self, post_id, player_id, post_topic, sector, content, likes=0, comments=0):
        """插入新帖子，包含post_id"""
        sql = """INSERT INTO posts(post_id, player_id, post_topic, sector, content, likes, comments, create_time)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())"""
        val = (post_id, player_id, post_topic, sector, content, likes, comments)
        self.cur.execute(sql, val)
        self.conn.commit()


    def Get_Post_By_Id(self, post_id):
        """根据帖子ID获取帖子详情（包含作者名）"""
        sql = """
            SELECT p.post_id, p.post_topic, p.content, p.sector, 
                   p.likes, p.comments, p.create_time, pl.user_name
            FROM posts p
            JOIN Players pl ON p.player_id = pl.player_id
            WHERE p.post_id = %s
        """
        val = (post_id,)
        self.cur.execute(sql, val)
        return self.cur.fetchone()


    def Get_Top_Rated_Games(self, limit=20):
        """获取评分最高的前 limit 个游戏"""
        try:
            sql = "SELECT game_id, game_name, game_tag, game_price, game_score FROM games ORDER BY game_score DESC LIMIT %s"
            self.cur.execute(sql, (limit,))
            return self.cur.fetchall()
        except Exception as e:
            print(f"获取热门游戏出错: {e}")
            return []

    def Get_User_Played_Games(self, user_id):
        """获取用户玩过的所有游戏ID列表（用于协同过滤）"""
        try:
            sql = "SELECT game_id FROM players_and_games WHERE player_id = %s"
            self.cur.execute(sql, (user_id,))
            rows = self.cur.fetchall()
            return [row[0] for row in rows]
        except Exception as e:
            print(f"获取用户游戏列表出错: {e}")
            return []

    def Get_Game_Info_Batch(self, game_ids):
        """批量获取游戏信息，返回字典 {game_id: (name, tag, price, score)}"""
        if not game_ids:
            return {}
        placeholders = ','.join(['%s'] * len(game_ids))
        sql = f"SELECT game_id, game_name, game_tag, game_price, game_score FROM games WHERE game_id IN ({placeholders})"
        self.cur.execute(sql, game_ids)
        rows = self.cur.fetchall()
        result = {}
        for row in rows:
            result[row[0]] = {
                "name": row[1],
                "tag": row[2],
                "price": float(row[3]) if row[3] else 0,
                "score": int(row[4]) if row[4] else 0
            }
        return result


    def Get_Game_Name_By_Id(self, game_id):
        """根据ID获取游戏名称"""
        sql = "SELECT game_name FROM games WHERE game_id = %s"
        self.cur.execute(sql, (game_id,))
        row = self.cur.fetchone()
        return row[0] if row else "未知游戏"

    def Get_All_Games_Tags(self):
        """返回字典 {game_id: tag_str}"""
        sql = "SELECT game_id, game_tag FROM games"
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        return {row[0]: row[1] for row in rows}


    def Get_Game_Tag_By_Id(self, game_id):
        """根据ID获取游戏标签"""
        sql = "SELECT game_tag FROM games WHERE game_id = %s"
        self.cur.execute(sql, (game_id,))
        row = self.cur.fetchone()
        return row[0] if row else ""

    def Get_All_Games_Simple(self):
        """获取所有游戏的基础信息：id, name, tag, price, score"""
        sql = "SELECT game_id, game_name, game_tag, game_price, game_score FROM games"
        self.cur.execute(sql)
        return self.cur.fetchall()


    def Get_All_Posts_For_Admin(self):
        """获取所有帖子（包含作者信息），用于管理员管理"""
        sql = """
            SELECT p.post_id, p.post_topic, p.content, p.sector, 
                   p.likes, p.comments, p.create_time, pl.user_name
            FROM posts p
            JOIN Players pl ON p.player_id = pl.player_id
            ORDER BY p.create_time DESC
        """
        self.cur.execute(sql)
        return self.cur.fetchall()

    def Delete_Post_By_Id(self, post_id):
        """删除帖子"""
        sql = "DELETE FROM posts WHERE post_id = %s"
        val = (post_id,)
        self.cur.execute(sql, val)
        self.conn.commit()
        return self.cur.rowcount > 0

    def Update_Game_Info(self, game_id, field, value):
        """更新游戏信息，field 为字段名，value 为新值"""
        if field not in ['game_name', 'game_type', 'game_price', 'game_score', 'game_comment', 'game_tag',
                         'game_introduction']:
            return False
        # 转义特殊字符防止 SQL 注入？使用参数化查询即可
        sql = f"UPDATE games SET {field} = %s WHERE game_id = %s"
        val = (value, game_id)
        self.cur.execute(sql, val)
        self.conn.commit()
        return self.cur.rowcount > 0

    def Update_Competition_Info(self, competition_id, field, value):
        """更新赛事信息"""
        if field not in ['competition_type', 'game_name', 'team1', 'team2', 'competition_date']:
            return False
        sql = f"UPDATE competitions SET {field} = %s WHERE competition_id = %s"
        val = (value, competition_id)
        self.cur.execute(sql, val)
        self.conn.commit()
        return self.cur.rowcount > 0


    def Get_Max_Game_Id(self):
        """获取当前最大的游戏ID"""
        sql = "SELECT MAX(game_id) FROM games"
        self.cur.execute(sql)
        result = self.cur.fetchone()[0]
        return result if result is not None else 0


    def Get_All_Games_With_Type(self):
        """获取所有游戏的基础信息及类型：id, name, tag, price, score, game_type"""
        sql = "SELECT game_id, game_name, game_tag, game_price, game_score, game_type FROM games"
        self.cur.execute(sql)
        return self.cur.fetchall()



    def Get_Same_Tag_Games(self, game_tag, limit=80):
        """根据游戏标签的前两个汉字进行模糊查询"""
        if not game_tag or not isinstance(game_tag, str):
            return []

        # 取标签前两个字符作为模糊匹配关键词
        keyword = game_tag[:2]
        try:
            sql = """
                SELECT game_id, game_name, game_tag, game_price, game_score
                FROM games
                WHERE game_tag LIKE %s
                LIMIT %s
            """
            pattern = f'%{keyword}%'
            self.cur.execute(sql, (pattern, limit))
            result = self.cur.fetchall()
            return result
        except Exception as e:
            print(f"模糊查询游戏失败: {e}")
            return []


# 初始一个用户,一个管理员,500款游戏
if __name__ == '__main__':
    user_data = pd.read_excel('../games_data/示例用户数据1.xlsx')
    user_game_data = pd.read_excel('../games_data/示例交互数据.xlsx')
    game_data = pd.read_excel('../games_data/Games_Info.xlsx')
    my_db = Database()
    my_db.Data_To_SQL_Add_Games_Info(game_data)  # 导入游戏数据
    my_db.Data_To_SQL_Add_Players_Info(user_data)  # 导入用户数据
    my_db.Data_To_SQL_Add_Games_And_Players_Info(user_game_data)  # 导入用户-游戏交互数据
    my_db.Update_Player_Info_And_Total_Value_And_Total_Play_Time(user_data)  # 更新用户信息
    my_db.Add_Admin()
    my_db.Modify_Game_Tag()  # 修正游戏标签
    # 导入赛事数据
    my_db.close()