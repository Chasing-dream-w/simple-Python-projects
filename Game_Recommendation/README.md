
```markdown
# 🎮 游戏推荐系统

一个基于 Flask 的 Web 游戏推荐系统，支持用户登录、游戏浏览、社区讨论、电竞赛事查询，以及多种游戏推荐算法。

## ✨ 主要功能

- **用户系统**：注册、登录、个人资料管理
- **游戏库**：游戏浏览、搜索、详情查看
- **推荐系统**：
  - 🔥 热门游戏推荐
  - 🤝 协同过滤推荐（基于词向量）
  - 🎯 基于游戏类型的推荐
  - 🔀 混合推荐算法
- **玩家社区**：发帖、评论、点赞
- **电竞赛事**：赛事信息查询
- **后台管理**：游戏/赛事/帖子的增删改查

## 🛠️ 技术栈

| 技术 | 说明 |
|------|------|
| Python 3.8+ | 后端语言 |
| Flask | Web 框架 |
| MySQL | 数据库 |
| text2vec | 腾讯词向量模型（自动下载） |
| BeautifulSoup | 爬虫工具 |
| Pandas | 数据处理 |

## 📦 环境配置

### 1. 克隆项目

```bash
git clone https://github.com/Chasing-dream-w/simple-python-projects.git
cd simple-python-projects
```

### 2. 安装依赖

```bash
pip install flask mysql-connector-python pandas numpy scipy text2vec requests beautifulsoup4
```

### 3. 配置数据库

- 确保 MySQL 服务已启动
- 修改 `data_base.py` 中的数据库连接配置：

```python
self.conn = mysql.connector.connect(
    port=3306,
    host='127.0.0.1',
    user='root',
    password='你的密码',  # 修改为你的 MySQL 密码
    charset='utf8mb4'
)
```

### 4. 初始化数据库

```bash
cd code
python data_process.py   # 创建数据表结构
```

> ⚠️ 首次运行前需要准备好 Excel 数据文件（`games_data/Games_Info.xlsx` 等），或通过爬虫获取数据。

### 5. 导入数据（可选）

```bash
# 爬取游戏数据（可能需要较长时间）
python spider_get_game.py
python spider_get_game_introduction.py
python spider_get_img.py

# 导入到数据库
python data_base.py
```

> 📌 **重要提示**：项目首次运行 `algorithm.py` 或 `word_embedding.py` 时，`text2vec` 库会自动下载 **腾讯中文词向量模型**（约 110MB），请保持网络畅通。

## 🚀 运行项目

```bash
cd code
python app.py
```

访问 http://127.0.0.1:5000

## 📂 项目结构

```
simple-python-projects/
├── code/
│   ├── app.py                 # Flask 主程序
│   ├── algorithm.py           # 推荐算法实现
│   ├── data_base.py           # 数据库操作
│   ├── data_process.py        # 数据库初始化
│   ├── word_embedding.py      # 词向量模型
│   ├── spider_*.py            # 爬虫脚本
│   └── img/                   # 游戏封面图片
├── page/                      # 前端页面（HTML/CSS/JS）
├── games_data/                # Excel 数据文件
└── README.md
```

## 🔧 常见问题

### 模型文件下载问题

项目依赖 `text2vec` 库，首次运行时会在 `~/.text2vec/datasets/` 目录下自动下载 110MB 的腾讯词向量模型。如果下载失败，请检查网络连接或配置代理。

### 数据库连接失败

- 确认 MySQL 服务已启动
- 检查 `data_base.py` 中的密码是否正确
- 确保 MySQL 用户有创建数据库的权限

### 端口被占用

修改 `app.py` 最后一行：

```python
app.run(host='127.0.0.1', port=5001)  # 改为其他端口
```

## 👥 默认账户

| 类型 | 账号 | 密码 |
|------|------|------|
| 普通用户 | 请在页面注册 | - |
| 管理员 | 需要在数据库中手动添加 | - |

## 📝 注意事项

1. 模型文件（.bin）已通过 `.gitignore` 忽略，不会被提交到 Git
2. 首次加载推荐功能时会稍慢（需要加载词向量模型）
3. 图片资源需要提前下载到 `code/img/` 目录

## 📄 License

仅供学习交流使用
