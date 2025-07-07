import re

def extract_characters(file_path):
    """
    从剧本文件中提取人物名称
    :param file_path: 剧本文件路径（txt文件）
    :return: 提取到的人物名称字典格式
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            script_text = file.read()

        # 使用正则表达式来匹配大写字母并且上下为空行的名称
        # 匹配完全大写字母的行，且上下行为空行
        # 例如：\nIVAR THE WITLESS\n
        characters = re.findall(r'^[A-Z]+$', script_text, re.MULTILINE)


        # 去除换行符并去重
        cleaned_characters = {character.strip() for character in characters if '\n' not in character}

        return cleaned_characters

    except FileNotFoundError:
        print("Error: 文件未找到！")
        return {}

# 示例用法
if __name__ == "__main__":
    file_path = "Star-Is-Born-A.txt"  # 这里替换为你的剧本文件路径
    characters = extract_characters(file_path)
    print("剧本中的人物：")
    print(characters)
