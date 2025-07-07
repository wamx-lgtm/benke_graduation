import pymysql
import json

# MySQL 连接信息
DB_CONFIG = {
    'host': 'localhost',
    'user': 'jwq',
    'password': '594288',
    'database': 'scripthub',
    'charset': 'utf8mb4'
}

def get_character_ids(script_id):
    """
    从数据库获取 script_id=2 的所有人物 character_id 和名字对应关系。
    :return: 字典 {character_name: character_id, ...}
    """
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = "SELECT character_name, character_id FROM scripts_character WHERE script_id = %s"
        cursor.execute(query, (script_id,))

        character_map = {name: str(char_id) for name, char_id in cursor.fetchall()}  # 直接转换为字符串

        cursor.close()
        conn.close()
        return character_map

    except pymysql.MySQLError as e:
        print(f"数据库查询错误: {e}")
        return {}

def get_scenes_from_db(script_id):
    """
    从数据库获取 script_id=2 的所有场景文本。
    :return: 场景列表 [{scene_id: int, scene_text: str}, ...]
    """
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = "SELECT scene_id, scene_text FROM scripts_scene WHERE scriptId_id = %s"
        cursor.execute(query, (script_id,))

        scenes = [{'scene_id': scene_id, 'scene_text': scene_text} for scene_id, scene_text in cursor.fetchall()]

        cursor.close()
        conn.close()
        return scenes

    except pymysql.MySQLError as e:
        print(f"数据库查询错误: {e}")
        return []

def extract_interactions(scenes, character_map):
    """
    统计人物交互，生成 {source: "character_id", target: "character_id"} 结构的 JSON 数据。
    :param scenes: 场景列表
    :param character_map: {character_name: character_id} 字典
    :return: 交互 JSON 数据
    """
    interactions = []

    for scene in scenes:
        scene_text = scene['scene_text']

        # 提取当前 Scene 内所有人物（保证顺序，且去重）
        present_characters = []
        for char_name in character_map.keys():
            if char_name in scene_text and char_name not in present_characters:
                present_characters.append(char_name)

        # 形成交互对（前 → 后）
        for i in range(len(present_characters) - 1):
            source = character_map.get(present_characters[i])
            target = character_map.get(present_characters[i + 1])
            if source and target:
                interactions.append({"source": str(source), "target": str(target)})  # 确保是字符串

    return json.dumps(interactions, ensure_ascii=False)

def update_character_links(script_id):
    """
    计算人物交互并更新到 scripts_script 表的 character_links 字段。
    """
    character_map = get_character_ids(script_id)
    if not character_map:
        print("未能获取人物 ID 数据，操作终止。")
        return

    scenes = get_scenes_from_db(script_id)
    character_links_json = extract_interactions(scenes, character_map)

    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        update_query = "UPDATE scripts_script SET character_links = %s WHERE scriptId = %s"
        cursor.execute(update_query, (character_links_json, script_id))
        conn.commit()

        print("人物交互数据已成功更新到数据库！")

    except pymysql.MySQLError as e:
        print(f"数据库更新错误: {e}")

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_character_links(5)
