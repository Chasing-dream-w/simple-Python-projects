# 网页逻辑
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
import os
import ast
from data_base import Database
import warnings
import time

# 抑制一些警告
warnings.filterwarnings("ignore")

my_db = Database()
app = Flask(__name__, template_folder='../page', static_folder='../page')

# 设置密钥，用于session
app.secret_key = 'game_recommendation_secret_key_2024'

# 配置应用
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SESSION_COOKIE_SECURE'] = False  # 开发环境设为False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


# 禁用缓存，用于开发
@app.after_request
def add_no_cache(response):
    if app.debug:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
    return response


@app.route('/')
def index():
    """首页，重定向到登录页"""
    return redirect(url_for('login'))


# 修改 login 函数的登录成功部分
@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'GET':
        # 如果已经登录，直接跳转到相应页面
        if session.get('logged_in'):
            # 检查是否是管理员，决定跳转到哪个页面
            if session.get('is_admin'):
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('main'))
        return render_template('login.html')

    # 处理POST请求（登录）
    if request.content_type != 'application/json':
        # 如果不是JSON请求，尝试获取表单数据
        username = request.form.get('username')
        password = request.form.get('password')
    else:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "请输入用户名和密码"})

    # 验证用户/管理员 - 优先验证管理员
    exist_admin = my_db.Vertify_Admin_Login_Info(username, password)
    exist_user = my_db.Vertify_User_Login_Info(username, password) if not exist_admin else False

    if exist_admin or exist_user:
        session['logged_in'] = True
        session['username'] = username
        session['is_admin'] = exist_admin

        if exist_user:
            # 获取用户ID并存入session
            user_info = my_db.Get_User_Info(username)
            if user_info:
                session['user_id'] = user_info[0]
        # 如果是管理员，强制跳转到admin页面
        if exist_admin:
            redirect_url = url_for('admin')
        else:
            redirect_url = url_for('main')

        # 返回JSON响应
        return jsonify({
            "success": True,
            "message": "登录成功",
            "is_admin": exist_admin,  # 让前端知道是管理员
            "redirect": redirect_url
        })
    else:
        return jsonify({"success": False, "message": "用户名或密码错误"})


@app.route('/api/check_admin')
def check_admin():
    """检查用户是否是管理员"""
    if not session.get('logged_in'):
        return jsonify({"is_admin": False}), 401

    is_admin = session.get('is_admin', False)
    return jsonify({"is_admin": is_admin})


# ========== 游戏管理API =========

@app.route('/api/admin/delete_game/<game_id>', methods=['DELETE'])
def delete_game(game_id):
    """删除游戏"""
    if not session.get('is_admin'):
        return jsonify({"success": False, "message": "无权限操作"}), 403

    try:
        # 调用数据库操作函数删除游戏
        result = my_db.Delete_Game_By_Id(game_id)

        if result:
            return jsonify({"success": True, "message": "游戏删除成功"})
        else:
            return jsonify({"success": False, "message": "游戏删除失败，可能不存在"})
    except Exception as e:
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500


@app.route('/api/admin/add_game', methods=['POST'])
def add_game():
    """添加游戏 - 修正字段名匹配"""
    if not session.get('is_admin'):
        return jsonify({"success": False, "message": "无权限操作"}), 403

    data = request.get_json()

    print(f"接收到游戏数据: {data}")  # 调试信息

    # 验证必要字段
    required_fields = ['game_id', 'game_name', 'game_type', 'game_price']
    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "message": f"缺少必要字段: {field}"})

    try:
        # 匹配数据库方法
        result = my_db.Add_Games_Info(
            game_id=data['game_id'],
            game_name=data['game_name'],
            game_type=data['game_type'],
            game_price=float(data['game_price']),
            game_score=float(data.get('game_score', 0)),
            game_comment=str(data.get('game_comment', '')),
            game_tag=data.get('game_tag', ''),
            game_introduction=data.get('game_introduction', '')
        )

        if result:
            return jsonify({"success": True, "message": "游戏添加成功"})
        else:
            return jsonify({"success": False, "message": "游戏添加失败"})
    except Exception as e:
        print(f"添加游戏错误: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500


# ========== 赛事管理API ==========

@app.route('/api/admin/add_tournament', methods=['POST'])
def add_tournament():
    """添加赛事"""
    if not session.get('is_admin'):
        return jsonify({"success": False, "message": "无权限操作"}), 403

    data = request.get_json()

    # 验证必要字段
    required_fields = ['competition_id', 'competition_type', 'game_name', 'team1', 'team2', 'competition_date']
    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "message": f"缺少必要字段: {field}"})

    try:
        # 调用数据库操作函数添加赛事
        result = my_db.Add_Competitions_Info(
            competiton_id=data['competition_id'],
            competition_type=data['competition_type'],
            game_name=data['game_name'],
            team1=data['team1'],
            team2=data['team2'],
            competition_date=data['competition_date']
        )

        if result:
            return jsonify({"success": True, "message": "赛事添加成功"})
        else:
            return jsonify({"success": False, "message": "赛事添加失败"})
    except Exception as e:
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500


@app.route('/api/admin/query_game', methods=['GET'])
def query_game():
    """查询游戏(支持按ID和名称查询)"""
    if not session.get('is_admin'):
        return jsonify({"success": False, "message": "无权限操作"}), 403

    try:
        game_id = request.args.get('id')
        game_name = request.args.get('name')

        if game_id:
            # 按ID查询
            result = my_db.Query_Game_Info_By_Id(game_id)
        elif game_name:
            # 按名称查询
            result = my_db.Query_Game_Info_By_Name(game_name)
        else:
            return jsonify({"success": False, "message": "缺少查询条件"})

        if result:
            # 格式化返回数据，匹配数据库字段
            game_data = {
                "game_id": result[0] if len(result) > 0 else '',
                "game_name": result[1] if len(result) > 1 else '',
                "game_type": result[2] if len(result) > 2 else '',
                "game_price": float(result[3]) if len(result) > 3 and result[3] else 0,
                "game_score": float(result[4]) if len(result) > 4 and result[4] else 0,
                "game_comment": str(result[5]) if len(result) > 5 else '',
                "game_tag": result[6] if len(result) > 6 else '',
                "game_introduction": result[7] if len(result) > 7 else ''
            }
            return jsonify({"success": True, "data": game_data})
        else:
            return jsonify({"success": False, "message": "未找到游戏"})
    except Exception as e:
        print(f"查询游戏失败: {str(e)}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500


@app.route('/api/admin/delete_tournament/<tournament_id>', methods=['DELETE'])
def delete_tournament(tournament_id):
    """删除赛事"""
    if not session.get('is_admin'):
        return jsonify({"success": False, "message": "无权限操作"}), 403

    try:
        # 调用数据库操作函数删除赛事
        result = my_db.Delete_Competition_By_Id(tournament_id)

        if result:
            return jsonify({"success": True, "message": "赛事删除成功"})
        else:
            return jsonify({"success": False, "message": "赛事删除失败，可能不存在"})
    except Exception as e:
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500


@app.route('/api/admin/query_tournament/<tournament_id>', methods=['GET'])
def query_tournament(tournament_id):
    """查询赛事"""
    if not session.get('is_admin'):
        return jsonify({"success": False, "message": "无权限操作"}), 403

    try:
        # 调用数据库操作函数查询赛事
        result = my_db.Query_Competition_Info_By_Id(tournament_id)

        if result:
            return jsonify({"success": True, "data": result})
        else:
            return jsonify({"success": False, "message": "未找到赛事"})
    except Exception as e:
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500


# 修改 main 路由，阻止管理员访问
@app.route('/main')
def main():
    """主页面"""
    # 检查是否已登录
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # 如果是管理员，重定向到管理员界面
    if session.get('is_admin'):
        return redirect(url_for('admin'))

    # 这里可以传递 is_admin 到模板，在前端显示管理员入口
    return render_template('main.html', is_admin=False)


# 玩家社区页面
@app.route('/post_list')
def post_list():
    """玩家社区帖子列表页面"""
    # 检查用户是否已登录
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('post_list.html')


@app.route('/post_detail')
def post_detail():
    """帖子详情页面"""
    # 检查用户是否已登录
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    # 获取帖子ID参数
    post_id = request.args.get('id', default=1, type=int)
    return render_template('post_detail.html', post_id=post_id)


@app.route('/game_detail')
def game_detail():
    """游戏详情页面"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('game_detail.html')


@app.route('/api/game/<int:game_id>')
def api_game_detail(game_id):
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "请先登录"}), 401

    try:
        game_info = my_db.Get_Game_Info_By_Id(game_id)[0]
        if not game_info:
            return jsonify({"success": False, "message": "游戏不存在"}), 404

        # 提取数据
        game_data = {
            "id": game_info[0],
            "name": game_info[1],
            "type_raw": game_info[2],  # 游戏类型（如 "['动作','角色扮演']"）
            "price": float(game_info[3]) if game_info[3] else 0,
            "score": int(game_info[4]) if game_info[4] else 0,
            "comment": str(game_info[5]) if len(game_info) > 5 else "",  # 评价文字（褒贬不一、好评如潮等）
            "tag_raw": game_info[6] if len(game_info) > 6 else "",  # 玩家提供的标签
            "introduction": game_info[7] if len(game_info) > 7 else ""
        }

        # 解析游戏类型标签（type_raw）
        type_tags = []
        if game_data["type_raw"]:
            try:
                parsed = ast.literal_eval(game_data["type_raw"])
                if isinstance(parsed, list):
                    type_tags = [str(t).strip() for t in parsed if t]
                else:
                    type_tags = [str(parsed).strip()]
            except (ValueError, SyntaxError):
                # 回退处理
                cleaned = game_data["type_raw"].strip('[]')
                type_tags = [t.strip().strip('"\'') for t in cleaned.split(',') if t.strip()]

        # 解析玩家标签（tag_raw）
        player_tags = []
        if game_data["tag_raw"]:
            try:
                parsed = ast.literal_eval(game_data["tag_raw"])
                if isinstance(parsed, list):
                    player_tags = [str(t).strip() for t in parsed if t]
                else:
                    player_tags = [str(parsed).strip()]
            except (ValueError, SyntaxError):
                cleaned = game_data["tag_raw"].strip('[]')
                player_tags = [t.strip().strip('"\'') for t in cleaned.split(',') if t.strip()]

        # 构建前端需要的数据
        frontend_game = {
            "id": game_data["id"],
            "name": game_data["name"],
            "image": f"/img/{game_data['id']}.jpg",
            "typeTags": type_tags,
            "playerTags": player_tags,
            "price": game_data["price"],
            "description": game_data["introduction"],
            "rating": game_data["score"] / 20.0,  # 转换为5分制
            "commentText": game_data["comment"],  # 评价文字
        }

        return jsonify({"success": True, "game": frontend_game})
    except Exception as e:
        print(f"获取游戏详情错误: {e}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500


@app.route('/admin')
def admin():
    """管理员页面"""
    # 检查是否已登录
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # 检查是否是管理员
    if not session.get('is_admin'):
        # 如果不是管理员，重定向到主页面
        return redirect(url_for('main'))

    # 传递 is_admin=True 给模板，避免前端再发请求
    return render_template('admin.html', is_admin=True)


@app.route('/register', methods=['POST'])
def register():
    """注册处理"""
    if request.content_type != 'application/json':
        # 如果不是JSON请求，尝试获取表单数据
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
    else:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

    # 验证输入
    if not all([username, email, password, confirm_password]):
        return jsonify({"success": False, "message": "请填写所有字段"})

    if len(username) < 3 or len(username) > 12:
        return jsonify({"success": False, "message": "用户名长度需为3-12位字符"})

    if len(password) < 6:
        return jsonify({"success": False, "message": "密码长度至少为6位"})

    if password != confirm_password:
        return jsonify({"success": False, "message": "两次输入的密码不一致"})

    print(username, email, password, confirm_password)
    # 检查用户是否已存在
    exist_user = my_db.Vertify_User_Is_Exist(username)
    if exist_user:
        return jsonify({"success": False, "message": "用户名已存在"})

    # 简单检查邮箱格式
    if '@' not in email or '.' not in email:
        return jsonify({"success": False, "message": "邮箱格式不正确"})

    # 保存用户信息到数据库
    try:
        user_id = my_db.Get_User_Number()
        my_db.Add_Players_Info(
            player_id=user_id,
            user_name="取个响亮的名字吧",
            user_account=username,
            user_email=email,
            user_password=password,
            user_games_list=[],
            user_total_play_time=0,
            user_total_value=0
        )

        return jsonify({
            "success": True,
            "message": "注册成功！",
            "auto_login": True,
            "username": username
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"注册失败: {str(e)}"})


# 获取用户信息
@app.route('/api/user/profile')
def get_user_profile():
    # 检查用户是否已登录
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "请先登录"})

    try:
        # 获取用户信息
        user_info = my_db.Get_User_Info(session.get('username'))

        # 确保user_info是元组且有足够的元素
        if not user_info or len(user_info) < 8:
            return jsonify({"success": False, "message": "用户信息不完整"})

        user_id = user_info[0]
        user_name = user_info[1]
        user_account = user_info[2] if len(user_info) > 2 else session.get('username')
        user_email = user_info[4] if len(user_info) > 4 else ""

        # 处理游戏列表
        if len(user_info) > 5 and user_info[5]:
            try:
                user_games_list = ast.literal_eval(user_info[5])
            except:
                user_games_list = []
        else:
            user_games_list = []

        user_total_play_time = user_info[6] if len(user_info) > 6 else 0
        user_total_value = user_info[7] if len(user_info) > 7 else 0

        # 保存到session
        session['user_id'] = user_id
        session['user_games_list'] = user_games_list

        # 计算称号
        if len(user_games_list) <= 10:
            tagline = "初出茅庐"
        elif len(user_games_list) <= 100:
            tagline = "略有见识"
        elif len(user_games_list) <= 1000:
            tagline = "鉴游无数"
        else:
            tagline = "玩遍万家"

        # 计算头像字母
        avatar_name = user_name or user_account or session.get('username') or 'U'
        avatar_letter = str(avatar_name)[0].upper()

        # 返回JSON响应 - 注意：前端期望的是 {"success": True, "data": {...}} 结构
        return jsonify({
            "success": True,
            "data": {
                "username": user_name,
                "account": user_account,
                "email": user_email,
                "games_list": user_games_list,
                "total_play_time": user_total_play_time,
                "total_value": user_total_value,
                "avatarLetter": avatar_letter,
                "tagline": tagline
            }
        })
    except Exception as e:
        print(f"获取用户信息错误: {str(e)}")
        return jsonify({"success": False, "message": f"获取用户信息失败: {str(e)}"})


@app.route('/create_post')
def create_post_page():
    """发帖页面"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('create_post.html')


@app.route('/api/create_post', methods=['POST'])
def api_create_post():
    """处理发帖"""
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "请先登录"}), 401

    data = request.get_json()
    topic = data.get('topic')
    sector = data.get('sector')
    content = data.get('content')

    if not topic or not sector or not content:
        return jsonify({"success": False, "message": "参数不完整"})

    # 获取当前用户ID
    username = session.get('username')
    user_info = my_db.Get_User_Info(username)
    if not user_info:
        return jsonify({"success": False, "message": "用户不存在"})
    player_id = user_info[0]  # 假设第一个字段是 player_id

    # 生成新帖子ID
    new_post_id = my_db.Get_Next_Post_Id()

    # 插入帖子（点赞、评论初始为0）
    try:
        my_db.Add_Post(
            player_id=player_id,
            post_topic=topic,
            sector=sector,
            content=content,
            likes=0,
            comments=0,
        )

    except Exception as e:
        print(f"发帖失败: {e}")
        return jsonify({"success": False, "message": "服务器错误"}), 500

    return jsonify({"success": True, "message": "发布成功"})


@app.route('/api/posts')
def api_get_posts():
    """返回所有帖子（JSON）"""
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "请先登录"}), 401

    try:
        posts = my_db.Get_All_Posts()  # 返回元组列表
        post_list = []
        for p in posts:
            post_list.append({
                "id": p[0],
                "title": p[1],
                "content": p[2][:100] + "..." if len(p[2]) > 100 else p[2],
                "sector": p[3],
                "likes": p[4],
                "comments": p[5],
                "time": p[6].strftime("%Y-%m-%d %H:%M") if p[6] else "",
                "author": p[7]
            })
        return jsonify({"success": True, "posts": post_list})
    except Exception as e:
        print(f"获取帖子列表失败: {e}")
        return jsonify({"success": False, "message": "服务器错误"}), 500


@app.route('/api/post/<int:post_id>')
def api_get_post(post_id):
    """获取单个帖子详情"""
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "请先登录"}), 401

    try:
        post = my_db.Get_Post_By_Id(post_id)
        if not post:
            return jsonify({"success": False, "message": "帖子不存在"}), 404

        post_data = {
            "id": post[0],
            "title": post[1],
            "content": post[2],
            "sector": post[3],
            "likes": post[4],
            "comments": post[5],
            "time": post[6].strftime("%Y-%m-%d %H:%M") if post[6] else "",
            "author": post[7]
        }
        return jsonify({"success": True, "post": post_data})
    except Exception as e:
        print(f"获取帖子详情失败: {e}")
        return jsonify({"success": False, "message": "服务器错误"}), 500


@app.route('/api/post/<int:post_id>/like', methods=['POST'])
def api_like_post(post_id):
    """点赞帖子"""
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "请先登录"}), 401

    try:
        my_db.Update_Post_Likes(post_id)
        return jsonify({"success": True, "message": "点赞成功"})
    except Exception as e:
        print(f"点赞失败: {e}")
        return jsonify({"success": False, "message": "服务器错误"}), 500


@app.route('/api/post/<int:post_id>/comments')
def api_get_comments(post_id):
    """获取帖子的评论列表"""
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "请先登录"}), 401

    try:
        comments = my_db.Get_Comments_By_Post_Id(post_id)
        comment_list = []
        for c in comments:
            comment_list.append({
                "id": c[0],
                "content": c[1],
                "time": c[2].strftime("%Y-%m-%d %H:%M") if c[2] else "",
                "likes": c[3],
                "author": c[4]
            })
        return jsonify({"success": True, "comments": comment_list})
    except Exception as e:
        print(f"获取评论失败: {e}")
        return jsonify({"success": False, "message": "服务器错误"}), 500


@app.route('/api/post/<int:post_id>/comment', methods=['POST'])
def api_add_comment(post_id):
    """发表评论"""
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "请先登录"}), 401

    data = request.get_json()
    content = data.get('content', '').strip()
    if not content:
        return jsonify({"success": False, "message": "评论内容不能为空"})

    # 获取当前用户ID
    username = session.get('username')
    user_info = my_db.Get_User_Info(username)
    if not user_info:
        return jsonify({"success": False, "message": "用户不存在"})
    player_id = user_info[0]

    try:
        # 插入评论
        comment_id = my_db.Add_Comment(post_id, player_id, content)
        # 帖子评论数 +1
        my_db.Increment_Post_Comment_Count(post_id)

        # 获取用户昵称用于返回
        author_name = user_info[1]  # user_info[1] 是用户名

        return jsonify({
            "success": True,
            "message": "评论成功",
            "comment": {
                "id": comment_id,
                "content": content,
                "author": author_name,
                "time": "刚刚",  # 前端可显示，实际时间由数据库生成
                "likes": 0
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"评论失败: {e}")
        return jsonify({"success": False, "message": "服务器错误"}), 500


# 用户游戏统计数据
@app.route('/api/user/stats')
def get_user_stats():
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "请先登录"})

    try:
        user_games_list = session.get('user_games_list', [])
        user_id = session.get('user_id')

        if not user_id:
            # 如果session中没有user_id，尝试获取用户信息
            user_info = my_db.Get_User_Info(session.get('username'))
            if user_info and len(user_info) > 0:
                user_id = user_info[0]
                session['user_id'] = user_id

        total_games = len(user_games_list)
        total_play_time = 0
        total_value = 0
        total_achievements = 0

        for game_id in user_games_list:
            time.sleep(0.1)
            try:
                game_info = my_db.Get_Game_Info(game_id)
                if game_info and len(game_info) > 1:
                    total_value += game_info[1] if game_info[1] else 0

                if user_id == session.get('user_id'):
                    user_game_info = my_db.Get_User_And_Game_Info(game_id=game_id, user_id=user_id)
                    if user_game_info and len(user_game_info) > 2:
                        total_achievements += user_game_info[0] if user_game_info[0] else 0
                        total_play_time += user_game_info[1] if user_game_info[1] else 0
            except Exception as e:
                print(f"处理游戏ID {game_id} 时出错: {str(e)}")
                continue

        return jsonify({
            "success": True,
            "data": {
                "totalGames": total_games,
                "totalAchievements": total_achievements,
                "totalValue": total_value,
                "totalHours": total_play_time
            }
        })
    except Exception as e:
        print(f"获取统计数据错误: {str(e)}")
        return jsonify({"success": False, "message": f"获取统计数据失败: {str(e)}"})


# 用户游戏详情数据
@app.route('/api/user/games')
def get_user_games():
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "请先登录"})

    try:
        user_games_list = session.get('user_games_list', [])
        user_id = session.get('user_id')

        return_data = []

        for game_id in user_games_list:
            time.sleep(0.05)
            try:
                # 获取游戏信息
                game_info = my_db.Get_Game_Info(game_id)
                if not game_info or len(game_info) < 4:
                    continue
                game_name = game_info[0]
                game_price = game_info[1] if game_info[1] else 0
                game_score = game_info[2] if game_info[2] else 0
                game_comment = game_info[3] if len(game_info) > 3 else ""

                # 获取用户游戏信息
                achievements = 0
                play_time = 0
                last_play_time = None

                if user_id == session.get('user_id'):
                    user_game_info = my_db.Get_User_And_Game_Info(game_id=game_id, user_id=user_id)
                    if user_game_info:
                        achievements = user_game_info[0] if user_game_info[0] else 0
                        play_time = user_game_info[1] if user_game_info[1] else 0
                        last_play_time = user_game_info[2] if len(user_game_info) > 4 else None

                # 添加游戏数据
                return_data.append({
                    "name": game_name,
                    "achievements": achievements,
                    "hours": play_time,
                    "value": game_price,
                    "score": game_score,
                })
            except Exception as e:
                print(f"处理游戏 {game_id} 详情时出错: {str(e)}")
                continue

        return jsonify({
            "success": True,
            "games": return_data
        })
    except Exception as e:
        print(f"获取游戏详情错误: {str(e)}")
        return jsonify({"success": False, "message": f"获取游戏详情失败: {str(e)}"})


@app.route('/api/games')
def get_all_games():
    """获取所有游戏，支持搜索(接口)"""
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "请先登录"})

    game_tag_1 = request.args.get('type', 'all')
    if game_tag_1 == 'all':
        # 获取前80个游戏（首页显示）
        result = my_db.Get_Game_List_For_Home()
    else:
        # 模糊查询：根据标签前两个汉字匹配
        result = my_db.Get_Same_Tag_Games(game_tag_1, limit=80)

    processed_games = []
    for row in result:
        # 根据实际返回的字段顺序提取
        game_id = row[0]
        game_name = row[1]
        game_tag = row[2]
        game_price = row[3]
        game_score = row[4]
        processed_games.append({
            "id": game_id,
            "name": game_name,
            "tag": game_tag,
            "price": float(game_price) if game_price else 0,
            "score": int(game_score) if game_score else 0
        })

    return jsonify({
        "success": True,
        "games": processed_games,
        "total": len(processed_games),
        "type": game_tag_1
    })


# 获取所有游戏标签
@app.route('/api/game_tags')
def get_game_tags():
    """获取所有游戏标签"""
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "请先登录"})

    # 直接返回标签列表
    game_tags = [
        "全部游戏", "热门推荐", "免费开玩游戏", "实用工具", "网络出版",
        "冒险游戏", "独立游戏", "大型多人在线游戏", "角色扮演游戏",
        "动作游戏", "模拟游戏", "策略游戏", "非游戏本体", "体育游戏",
        "游戏开发", "休闲游戏", "动画制作和建模", "教育游戏", "抢先体验游戏"
    ]
    return jsonify({
        "success": True,
        "tags": game_tags
    })


@app.route('/img/<path:filename>')
def serve_image(filename):
    """提供图片文件"""
    try:
        # 获取当前文件的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建img文件夹路径
        img_dir = os.path.join(current_dir, '..', 'img')
        print(f"尝试提供图片: {filename}, 从目录: {img_dir}")

        # 检查文件是否存在
        file_path = os.path.join(img_dir, filename)
        if not os.path.exists(file_path):
            print(f"图片文件不存在: {file_path}")
            # 返回默认图片或404
            return "", 404

        return send_from_directory(img_dir, filename)
    except Exception as e:
        print(f"提供图片失败: {str(e)}")
        return "", 404


@app.route('/game_news')
def game_news():
    """游戏资讯页面"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('game_news.html')


# ========== 推荐算法 API ==========

@app.route('/recommend')
def recommend():
    """智能算法推荐页面"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('recommend.html')


@app.route('/api/recommend/hot')
def api_recommend_hot():
    """热门游戏：按评分降序返回前20个游戏"""
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "请先登录"}), 401

    try:
        # 从数据库获取评分最高的前20个游戏
        hot_games = my_db.Get_Top_Rated_Games(limit=20)
        games_list = []
        for game in hot_games:
            games_list.append({
                "id": game[0],
                "name": game[1],
                "tag": game[2],      # 标签字符串
                "price": float(game[3]) if game[3] else 0,
                "score": int(game[4]) if game[4] else 0
            })
        return jsonify({"success": True, "games": games_list})
    except Exception as e:
        print(f"获取热门游戏失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/recommend/collaborative')
def api_recommend_collaborative():
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "请先登录"}), 401

    user_games_list = session.get('user_games_list', [])
    print("用户游戏列表:", user_games_list)
    if not user_games_list:
        user_info = my_db.Get_User_Info(session.get('username'))
        if user_info and len(user_info) > 5:
            try:
                user_games_list = ast.literal_eval(user_info[5])
                session['user_games_list'] = user_games_list
            except:
                user_games_list = []
    if not user_games_list:
        return jsonify({"success": True, "games": []})

    try:
        from algorithm import collaborative_filter_recommend
        recommendations = collaborative_filter_recommend(user_games_list, my_db)
        return jsonify({"success": True, "games": recommendations})
    except Exception as e:
        print(f"协同过滤推荐失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/recommend/hybrid')
def api_recommend_hybrid():
    """混合推荐：协同过滤 + 低分筛选 + 每个源游戏取前3"""
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "请先登录"}), 401

    user_games_list = session.get('user_games_list', [])
    if not user_games_list:
        user_info = my_db.Get_User_Info(session.get('username'))
        if user_info and len(user_info) > 5:
            try:
                user_games_list = ast.literal_eval(user_info[5])
                session['user_games_list'] = user_games_list
            except:
                user_games_list = []
    if not user_games_list:
        return jsonify({"success": True, "games": []})

    try:
        from algorithm import hybrid_filter_recommend
        recommendations = hybrid_filter_recommend(user_games_list, my_db, top_n=20, per_source_limit=3, max_score=85)
        return jsonify({"success": True, "games": recommendations})
    except Exception as e:
        print(f"混合推荐失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/recommend/type_based')
def api_recommend_type_based():
    """类型推荐：根据用户玩过的游戏类型，推荐相同类型中评分较高的游戏"""
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "请先登录"}), 401

    user_games_list = session.get('user_games_list', [])
    if not user_games_list:
        user_info = my_db.Get_User_Info(session.get('username'))
        if user_info and len(user_info) > 5:
            try:
                user_games_list = ast.literal_eval(user_info[5])
                session['user_games_list'] = user_games_list
            except:
                user_games_list = []
    if not user_games_list:
        return jsonify({"success": True, "games": []})

    try:
        from algorithm import type_based_recommend
        recommendations = type_based_recommend(user_games_list, my_db, top_n=20)
        return jsonify({"success": True, "games": recommendations})
    except Exception as e:
        print(f"类型推荐失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# ========== 修改游戏信息 API ==========
@app.route('/api/admin/update_game', methods=['POST'])
def update_game():
    """管理员修改游戏信息"""
    if not session.get('is_admin'):
        return jsonify({"success": False, "message": "无权限操作"}), 403

    data = request.get_json()
    game_id = data.get('game_id')
    field = data.get('field')
    value = data.get('value')

    if not game_id or not field or value is None:
        return jsonify({"success": False, "message": "缺少必要参数"})

    # 允许修改的字段白名单
    allowed_fields = ['game_name', 'game_type', 'game_price', 'game_score', 'game_comment', 'game_tag', 'game_introduction']
    if field not in allowed_fields:
        return jsonify({"success": False, "message": "不允许修改该字段"})

    try:
        success = my_db.Update_Game_Info(game_id, field, value)
        if success:
            return jsonify({"success": True, "message": "游戏信息修改成功"})
        else:
            return jsonify({"success": False, "message": "游戏不存在或修改失败"})
    except Exception as e:
        print(f"修改游戏信息失败: {e}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500

@app.route('/api/user/add_game', methods=['POST'])
def api_user_add_game():
    """用户手动添加游戏（包含成就、价格、时长）"""
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "请先登录"}), 401

    data = request.get_json()
    game_name = data.get('game_name', '').strip()
    achievements = data.get('achievements', 0)
    price = data.get('price', 0.0)
    hours = data.get('hours', 0.0)

    if not game_name:
        return jsonify({"success": False, "message": "游戏名称不能为空"})

    # 1. 查询或创建游戏记录
    existing_game = my_db.Query_Game_Info_By_Name(game_name)
    if existing_game:
        game_id = existing_game[0]
        # 如果已存在，价格以现有记录为准（覆盖用户输入的价格）
        actual_price = existing_game[3] if len(existing_game) > 3 else price
    else:
        # 生成新游戏ID
        max_id = my_db.Get_Max_Game_Id()
        new_id = max_id + 1
        while my_db.Vertify_Game_Is_Exist(new_id):
            new_id += 1
        # 插入新游戏（默认类型、标签等）
        default_type = "其他"
        default_score = 0
        default_comment = "手动添加"
        default_tag = ""
        default_intro = "手动添加的游戏"
        success = my_db.Add_Games_Info(
            game_id=new_id,
            game_name=game_name,
            game_type=default_type,
            game_price=float(price),
            game_score=default_score,
            game_comment=default_comment,
            game_tag=default_tag,
            game_introduction=default_intro
        )
        if not success:
            return jsonify({"success": False, "message": "游戏创建失败"})
        game_id = new_id
        actual_price = float(price)

    # 2. 获取用户信息
    username = session.get('username')
    user_info = my_db.Get_User_Info(username)
    if not user_info or len(user_info) < 6:
        return jsonify({"success": False, "message": "用户信息异常"})

    user_id = user_info[0]
    # 解析现有游戏列表
    import ast
    try:
        games_list = ast.literal_eval(user_info[5]) if user_info[5] else []
    except:
        games_list = []
    if not isinstance(games_list, list):
        games_list = []

    # 检查是否已拥有
    if game_id in games_list:
        return jsonify({"success": False, "message": "您已经拥有该游戏"})

    # 3. 添加交互记录（成就、时长）
    # Add_Players_And_Games_Info 方法需要参数 (player_id, game_id, achievement_number, play_time, last_week_play_time)
    # 这里 last_week_play_time 默认为 0
    my_db.Add_Players_And_Games_Info(user_id, game_id, achievements, hours, 0)

    # 4. 更新用户的游戏列表
    games_list.append(game_id)
    my_db.Update_Player_Info(3, str(games_list), user_id)

    # 5. 更新用户的总价值（累加游戏价格）
    current_total_value = user_info[7] if len(user_info) > 7 else 0
    new_total_value = current_total_value + actual_price
    my_db.Update_Player_Info(5, new_total_value, user_id)

    # 6. 更新用户的总游玩时长（累加）
    current_total_hours = user_info[6] if len(user_info) > 6 else 0
    new_total_hours = current_total_hours + hours
    my_db.Update_Player_Info(4, new_total_hours, user_id)

    return jsonify({"success": True, "message": f"游戏“{game_name}”已添加（成就:{achievements}, 价格:{actual_price}, 时长:{hours}小时），请重新登录后查看"})


# ========== 修改赛事信息 API ==========
@app.route('/api/admin/update_tournament', methods=['POST'])
def update_tournament():
    """管理员修改赛事信息"""
    if not session.get('is_admin'):
        return jsonify({"success": False, "message": "无权限操作"}), 403

    data = request.get_json()
    tournament_id = data.get('tournament_id')
    field = data.get('field')
    value = data.get('value')

    if not tournament_id or not field or value is None:
        return jsonify({"success": False, "message": "缺少必要参数"})

    # 允许修改的字段白名单
    allowed_fields = ['competition_type', 'game_name', 'team1', 'team2', 'competition_date']
    if field not in allowed_fields:
        return jsonify({"success": False, "message": "不允许修改该字段"})

    try:
        # 调用数据库中的更新方法
        success = my_db.Update_Competition_Info(tournament_id, field, value)
        if success:
            return jsonify({"success": True, "message": "赛事信息修改成功"})
        else:
            return jsonify({"success": False, "message": "赛事不存在或修改失败"})
    except Exception as e:
        print(f"修改赛事信息失败: {e}")
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500


# ========== 帖子管理API（管理员） ==========

@app.route('/api/admin/posts', methods=['GET'])
def admin_get_posts():
    """管理员获取所有帖子"""
    if not session.get('is_admin'):
        return jsonify({"success": False, "message": "无权限操作"}), 403

    try:
        posts = my_db.Get_All_Posts_For_Admin()
        post_list = []
        for p in posts:
            post_list.append({
                "id": p[0],
                "title": p[1],
                "content": p[2][:100] + "..." if len(p[2]) > 100 else p[2],
                "sector": p[3],
                "likes": p[4],
                "comments": p[5],
                "time": p[6].strftime("%Y-%m-%d %H:%M") if p[6] else "",
                "author": p[7]
            })
        return jsonify({"success": True, "posts": post_list})
    except Exception as e:
        print(f"获取帖子列表失败: {e}")
        return jsonify({"success": False, "message": "服务器错误"}), 500

@app.route('/api/admin/delete_post/<int:post_id>', methods=['DELETE'])
def admin_delete_post(post_id):
    """管理员删除帖子"""
    if not session.get('is_admin'):
        return jsonify({"success": False, "message": "无权限操作"}), 403

    try:
        success = my_db.Delete_Post_By_Id(post_id)
        if success:
            return jsonify({"success": True, "message": "帖子删除成功"})
        else:
            return jsonify({"success": False, "message": "帖子不存在或删除失败"})
    except Exception as e:
        print(f"删除帖子失败: {e}")
        return jsonify({"success": False, "message": "服务器错误"}), 500


# 赛事信息页面
@app.route('/tournaments')
def tournaments():
    # 检查用户是否已登录
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # 渲染赛事信息页面
    return render_template('tournaments.html')  # 赛事页面文件名为 tournaments.html


# 赛事数据API（用于AJAX请求）
@app.route('/api/tournaments')
def get_tournaments():
    # 检查用户是否已登录
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401

    # 获取查询参数
    game = request.args.get('game', 'PUBG')
    year = request.args.get('year', '2025')

    # 从数据库获取赛事数据
    tournaments_data = [
        {
            "id": 1,
            "name": "PUBG全球锦标赛 2025",
            "date": "2025-12-19",
            "level": "全球总决赛",
            "status": "ended"
        },
        {
            "id": 2,
            "name": "PUBG全球系列赛 10",
            "date": "2025-11-28",
            "level": "S级赛事",
            "status": "ended"
        },
        # ... 更多赛事数据
    ]

    return jsonify({
        "success": True,
        "data": tournaments_data,
        "game": game,
        "year": year
    })


@app.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    return redirect(url_for('login'))


@app.route('/check_session')
def check_session():
    """检查session状态"""
    if session.get('logged_in'):
        return jsonify({
            "logged_in": True,
            "username": session.get('username')
        })
    else:
        return jsonify({"logged_in": False})


if __name__ == '__main__':
    print("=" * 50)
    print("游戏推荐系统 - 登录模块")
    print("=" * 50)
    print("访问地址: http://127.0.0.1:5000")
    print("=" * 50)

    # 关键修复：禁用自动重载器，避免Windows线程问题
    app.run(
        debug=True,
        host='127.0.0.1',
        port=5000,
        use_reloader=False,  # 禁用自动重载
        threaded=True  # 启用多线程
    )