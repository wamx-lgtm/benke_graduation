import re
import pymysql
import json
from collections import Counter

# MySQL 连接信息
DB_CONFIG = {
    'host': 'localhost',       # 修改为你的 MySQL 服务器地址
    'user': 'jwq',             # 修改为你的 MySQL 用户名
    'password': '594288',      # 修改为你的 MySQL 密码
    'database': 'scripthub',   # 修改为你的数据库名称
    'charset': 'utf8mb4'       # 防止中文字符乱码
}

# 常见无意义单词（停用词）列表
STOPWORDS = {"im","go","dr","int","do","just","can't","can","all","so","a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in", "into", "is", "it", "no", "not", "of", "on", "or", "such", "that", "the", "their", "then", "there", "these", "they", "this", "to", "was", "will", "with", "he", "she", "we", "you", "i", "me", "my", "your", "our", "his", "her", "its", "them", "us", "from", "up", "back", "him", "off", "out"}

def get_top_words_from_file(file_path, top_n=20):
    """
    统计剧本文件中的高频词，忽略停用词，并归一化到 0-8 之间
    :param file_path: 剧本文件路径（txt文件）
    :param top_n: 返回的高频词数量
    :return: 归一化后的高频词及其比例（JSON 格式）
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            script_text = file.read()
        
        # 仅保留字母和空格，并转换为小写
        words = re.findall(r'\b[a-zA-Z]+\b', script_text.lower())
        
        # 过滤掉停用词
        filtered_words = [word for word in words if word not in STOPWORDS]
        
        # 统计词频
        word_counts = Counter(filtered_words)
        
        # 获取高频词
        top_words = word_counts.most_common(top_n)
        
        # 计算最大最小值
        max_freq = top_words[0][1] if top_words else 1
        min_freq = top_words[-1][1] if len(top_words) > 1 else 1  # 处理只有一个单词的情况

# 避免 min_freq == max_freq 导致除零错误
        if max_freq == min_freq:
            normalized_words = {word: 5 for word, count in top_words}  # 若只有一个值，设为中间值
        else:
            normalized_words = {
                word: round(3 + (count - min_freq) / (max_freq - min_freq) * (8 - 3))
                for word, count in top_words
            }
        
        return json.dumps(normalized_words, ensure_ascii=False)  # 转换为 JSON 字符串
    except FileNotFoundError:
        print("Error: 文件未找到！")
        return "{}"

def insert_wordcloud_to_db(words_json, script_id=2):
    """
    将高频词 JSON 数据插入 MySQL 数据库。
    :param words_json: 高频词 JSON 数据
    :param script_id: 剧本 ID，默认为 2
    """
    try:
        # 建立数据库连接
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO scripts_wordcloud (words, scriptId_id)
        VALUES (%s, %s)
        """

        # 插入数据
        cursor.execute(insert_query, (words_json, script_id))

        # 提交事务
        conn.commit()
        print("Wordcloud data inserted successfully!")

    except pymysql.MySQLError as e:
        print(f"Error inserting wordcloud data: {e}")

    finally:
        # 关闭数据库连接
        cursor.close()
        conn.close()

if __name__ == "__main__":
    file_path = "Star-Is-Born-A.txt"  # 修改为你的剧本文本路径
    top_words_json = get_top_words_from_file(file_path, top_n=25)
    
    if top_words_json != "{}":
        insert_wordcloud_to_db(top_words_json, script_id=5)
