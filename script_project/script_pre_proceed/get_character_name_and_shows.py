import re
import pymysql
from collections import Counter
import numpy as np

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',  # 你的 MySQL 服务器地址
    'user': 'jwq',        # 你的 MySQL 用户名
    'password': '594288', # 你的 MySQL 密码
    'database': 'scripthub',
    'charset': 'utf8mb4'
}

def count_character_occurrences(file_path, characters):
    """
    统计剧本中人物出现的次数
    :param file_path: 剧本文件路径（txt文件）
    :param characters: 需要统计的人物名字集合
    :return: 人物出现次数的字典
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            script_text = file.read()

        # 统计每个人物名称的出现次数
        character_counts = {character: len(re.findall(r'\b' + re.escape(character) + r'\b', script_text)) for character in characters}
        return character_counts

    except FileNotFoundError:
        print("Error: 文件未找到！")
        return {}

def compute_symbol_size_and_category(character_counts):
    """
    计算 symbol_size 和 category
    :param character_counts: 人物出现次数的字典
    :return: 包含 symbol_size 和 category 的字典
    """
    if not character_counts:
        return {}

    # 获取所有出现次数
    values = list(character_counts.values())

    # 计算 symbol_size: 线性映射到 2-7 之间
    min_count, max_count = min(values), max(values)
    symbol_sizes = {char: 2 + round((count - min_count) / (max_count - min_count) * 5) if max_count > min_count else 2
                    for char, count in character_counts.items()}

    # 计算 category: 归一化到 0-7 的整数
    categories = {char: np.digitize(count, np.linspace(min_count, max_count, 8), right=True)
                  for char, count in character_counts.items()}

    return {char: (symbol_sizes[char], categories[char]) for char in character_counts}

def insert_characters_to_db(character_counts, script_id=5):
    """
    将人物信息插入数据库
    :param character_counts: 人物出现次数字典
    :param script_id: 剧本 ID，默认为 3
    """
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO scripts_character (character_name, image_url, symbol_size, value, category, script_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        # 计算 symbol_size 和 category
        computed_values = compute_symbol_size_and_category(character_counts)

        data_to_insert = [
            (char, "", computed_values[char][0], count, computed_values[char][1], script_id)
            for char, count in character_counts.items()
        ]

        # 批量插入
        cursor.executemany(insert_query, data_to_insert)
        conn.commit()
        print(f"{len(character_counts)} characters inserted successfully!")

    except pymysql.MySQLError as e:
        print(f"数据库插入失败: {e}")

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    file_path = "Star-is-Born-A.txt"  # 剧本文本路径
    characters = {'EMERALD', 'ALLY', 'ACTION', 'BOBBY', 'JACK', 'NOODLES', 'BRYAN', 'BACKSTAGE', 'GAIL', 'PAULETTE', 'PHIL', 'CARL', 'BEN', 'PHOTOGRAPHER', 'RAMON', 'REZ', 'LORENZO', 'RICHY', 'TOMMY', 'WOLFIE', 'SOOKI', 'FRANKIE', 'MATTY'}

    # 获取人物出现次数
    character_counts = count_character_occurrences(file_path, characters)
    print("人物出现次数：", character_counts)

    # 插入数据库
    insert_characters_to_db(character_counts)
