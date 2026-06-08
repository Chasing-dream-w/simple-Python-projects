import numpy as np
from scipy import spatial
from text2vec import Word2Vec
import random


# 全局模型和向量缓存
_model = None
_vector_cache = {}


def _load_model():
    global _model
    if _model is None:
        print("加载词向量模型...")
        _model = Word2Vec("w2v-light-tencent-chinese")
    return _model


def get_game_vector(game_id, db):
    """获取游戏标签的向量（带缓存）"""
    if game_id in _vector_cache:
        return _vector_cache[game_id]

    tag = db.Get_Game_Tag_By_Id(game_id)
    if not tag or tag.strip() == '':
        vec = np.zeros(768)  # 腾讯模型维度
    else:
        model = _load_model()
        embedding = model.encode([tag], show_progress_bar=False, normalize_embeddings=True)
        vec = embedding[0]
    _vector_cache[game_id] = vec
    return vec


def compute_similarity(vec1, vec2):
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0.0
    return 1 - spatial.distance.cosine(vec1, vec2)


def collaborative_filter_recommend(played_games, db, top_n=20, sim_threshold=0.5, per_source_limit=5):
    """
    基于词向量的协同过滤推荐，每个源游戏独立贡献候选，保证多样性。

    Args:
        played_games: list of int 用户已玩游戏ID
        db: 数据库对象
        top_n: 最终返回推荐数量
        sim_threshold: 相似度阈值（低于此值的不考虑）
        per_source_limit: 每个源游戏最多取多少个候选（推荐理由可能来自不同源）
    Returns:
        list of dict
    """
    if not played_games:
        return []

    # 获取所有游戏
    all_games = db.Get_All_Games_Simple()  # [(id, name, tag, price, score), ...]
    if not all_games:
        return []

    # 构建游戏基本信息字典
    game_names = {g[0]: g[1] for g in all_games}
    game_tags = {g[0]: g[2] for g in all_games}
    game_prices = {g[0]: g[3] for g in all_games}
    game_scores = {g[0]: g[4] for g in all_games}

    # 用于存储候选游戏：{target_id: (max_similarity, source_id)}
    # 注意：每个目标游戏只保留相似度最高的一个源游戏（用于展示理由）
    candidate_map = {}

    # 遍历每个源游戏
    for source_gid in played_games:
        print(f"正在处理源游戏 {source_gid}: {game_names.get(source_gid, '未知')}")
        source_vec = get_game_vector(source_gid, db)
        if np.linalg.norm(source_vec) == 0:
            print(f"  游戏 {source_gid} 向量为零，跳过")
            continue

        # 计算该源游戏与所有其他游戏的相似度
        candidates = []
        for target_gid in game_names:
            if target_gid == source_gid or target_gid in played_games:
                continue
            target_vec = get_game_vector(target_gid, db)
            if np.linalg.norm(target_vec) == 0:
                continue
            sim = compute_similarity(source_vec, target_vec)
            if sim < sim_threshold:
                continue
            candidates.append((target_gid, sim))

        # 取该源游戏相似度最高的 per_source_limit 个候选
        candidates.sort(key=lambda x: x[1], reverse=True)
        top_candidates = candidates[:per_source_limit]
        print(f"  找到 {len(candidates)} 个候选，取前 {len(top_candidates)} 个")

        # 合并到总候选集：如果目标游戏尚未被记录，或者新来源的相似度更高，则更新
        for target_gid, sim in top_candidates:
            if target_gid not in candidate_map or sim > candidate_map[target_gid][0]:
                candidate_map[target_gid] = (sim, source_gid)

    # 将候选按相似度降序排序
    sorted_candidates = sorted(candidate_map.items(), key=lambda x: x[1][0], reverse=True)[:top_n]

    # 构建返回结果
    result = []
    for target_gid, (sim, source_gid) in sorted_candidates:
        source_name = game_names.get(source_gid, "未知游戏")
        result.append({
            "id": target_gid,
            "name": game_names.get(target_gid, "未知游戏"),
            "tag": game_tags.get(target_gid, ""),
            "price": float(game_prices.get(target_gid, 0)),
            "score": int(game_scores.get(target_gid, 0)),
            "reason_game": source_name
        })

    print(f"最终推荐数量: {len(result)}")
    return result


def hybrid_filter_recommend(played_games, db, top_n=20, sim_threshold=0.5, per_source_limit=3, max_score=85):
    """
    混合推荐：基于协同过滤，每个源游戏从相似游戏中随机抽取 per_source_limit 个（评分 < max_score），
    汇总后按评分降序排序。
    """
    if not played_games:
        return []

    all_games = db.Get_All_Games_Simple()
    if not all_games:
        return []

    game_names = {g[0]: g[1] for g in all_games}
    game_tags = {g[0]: g[2] for g in all_games}
    game_prices = {g[0]: g[3] for g in all_games}
    game_scores = {g[0]: g[4] for g in all_games}

    candidate_map = {}  # target_id -> (source_id, score, similarity)

    for source_gid in played_games:
        print(f"处理源游戏 {source_gid}: {game_names.get(source_gid, '未知')}")
        source_vec = get_game_vector(source_gid, db)
        if np.linalg.norm(source_vec) == 0:
            print("  向量为零，跳过")
            continue

        # 收集所有相似且评分低于 max_score 的游戏
        candidates = []
        for target_gid in game_names:
            if target_gid == source_gid or target_gid in played_games:
                continue
            target_vec = get_game_vector(target_gid, db)
            if np.linalg.norm(target_vec) == 0:
                continue
            sim = compute_similarity(source_vec, target_vec)
            if sim < sim_threshold:
                continue
            score = game_scores.get(target_gid, 0)
            if score >= max_score:
                continue
            candidates.append((target_gid, score, sim))

        if len(candidates) == 0:
            print(f"  没有符合条件的候选游戏")
            continue

        # 随机抽取 per_source_limit 个（若不足则全取）
        sample_size = min(per_source_limit, len(candidates))
        selected = random.sample(candidates, sample_size)
        print(f"  找到 {len(candidates)} 个候选，随机抽取 {sample_size} 个")

        for target_gid, score, sim in selected:
            if target_gid not in candidate_map or sim > candidate_map[target_gid][2]:
                candidate_map[target_gid] = (source_gid, score, sim)

    # 按评分降序排序
    sorted_items = sorted(candidate_map.items(), key=lambda x: x[1][1], reverse=True)[:top_n]

    result = []
    for target_gid, (source_gid, score, sim) in sorted_items:
        source_name = game_names.get(source_gid, "未知游戏")
        result.append({
            "id": target_gid,
            "name": game_names.get(target_gid, "未知游戏"),
            "tag": game_tags.get(target_gid, ""),
            "price": float(game_prices.get(target_gid, 0)),
            "score": int(score),
            "reason_game": source_name
        })

    print(f"混合推荐最终数量: {len(result)}")
    return result


def type_based_recommend(played_games, db, top_n=20):
    """
    基于游戏类型的推荐：统计用户玩过的游戏类型，找出最常玩的类型，
    推荐该类型中评分较高且未玩过的游戏。
    兼容多种 game_type 存储格式：Python列表字符串、逗号分隔字符串、单个字符串。
    """
    if not played_games:
        print("用户没有玩过任何游戏")
        return []

    import ast

    # 1. 收集所有游戏的类型（一次性获取，避免循环查询）
    # 一次性获取所有游戏的 id, name, tag, price, score, game_type
    all_games_with_type = db.Get_All_Games_With_Type()  # 需要在 data_base.py 中添加此方法
    if not all_games_with_type:
        # 如果没有一次性获取的方法，回退到原方案
        all_games_with_type = []
        all_games_simple = db.Get_All_Games_Simple()
        for g in all_games_simple:
            gid = g[0]
            game_info = db.Get_Game_Info_By_Id(gid)
            if game_info and len(game_info[0]) > 2:
                game_type = game_info[0][2]
                all_games_with_type.append((gid, g[1], g[2], g[3], g[4], game_type))
            else:
                all_games_with_type.append((gid, g[1], g[2], g[3], g[4], ""))

    # 2. 解析游戏类型的通用函数
    def parse_game_types(type_str):
        """将各种格式的 game_type 解析为列表"""
        if not type_str or type_str == "":
            return []
        # 如果是字符串，尝试多种解析
        try:
            parsed = ast.literal_eval(type_str)
            if isinstance(parsed, list):
                return [str(t).strip() for t in parsed if t]
            else:
                return [str(parsed).strip()]
        except:
            # 如果不是列表格式，尝试按逗号分隔（中文或英文逗号）
            if ',' in type_str:
                return [t.strip().strip('"\'') for t in type_str.split(',') if t.strip()]
            elif '，' in type_str:
                return [t.strip() for t in type_str.split('，') if t.strip()]
            else:
                return [type_str.strip()]

    # 3. 统计用户玩过的游戏的类型频率
    type_counter = {}
    for gid in played_games:
        # 找到该游戏的类型
        game_type_str = ""
        for item in all_games_with_type:
            if item[0] == gid:
                game_type_str = item[5]  # 索引5是 game_type
                break
        if not game_type_str:
            # 如果上面没找到，尝试单独查询
            game_info = db.Get_Game_Info_By_Id(gid)
            if game_info and len(game_info[0]) > 2:
                game_type_str = game_info[0][2]
        types = parse_game_types(game_type_str)
        for t in types:
            type_counter[t] = type_counter.get(t, 0) + 1

    print(f"用户游戏类型统计: {type_counter}")

    if not type_counter:
        print("没有解析到任何有效的游戏类型，请检查数据库中的 game_type 字段")
        return []

    # 4. 找到用户最常玩的类型
    most_common_type = max(type_counter.items(), key=lambda x: x[1])[0]
    print(f"用户最常玩的游戏类型: {most_common_type}")

    # 5. 构建推荐候选列表（从所有游戏中筛选）
    candidates = []
    for item in all_games_with_type:
        gid, name, tag, price, score, game_type_str = item
        if gid in played_games:
            continue
        types = parse_game_types(game_type_str)
        if most_common_type in types:
            candidates.append({
                "id": gid,
                "name": name,
                "tag": tag,
                "price": float(price) if price else 0,
                "score": int(score) if score else 0,
                "reason_game": most_common_type
            })

    # 6. 按评分降序排序，取前 top_n
    candidates.sort(key=lambda x: x["score"], reverse=True)
    result = candidates[:top_n]

    print(f"类型推荐最终数量: {len(result)}")
    return result

