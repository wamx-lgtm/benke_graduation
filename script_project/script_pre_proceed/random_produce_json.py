import random
import json

def generate_unique_pairs(num_pairs):
    pairs = set()  # 使用集合避免重复对
    while len(pairs) < num_pairs:
        source = random.randint(55,71)
        target = random.randint(55,71)
        # 确保 source 和 target 不相等
        if source != target:
            pairs.add((source, target))
    
    return [{"source": str(pair[0]), "target": str(pair[1])} for pair in pairs]

# 生成 10 对不重复的 source 和 target
num_pairs = 80
random_pairs = generate_unique_pairs(num_pairs)

# 将生成的随机对输出到 ttt.json 文件
with open("ttt.json", "w") as file:
    json.dump(random_pairs, file, indent=4)

print("Random pairs have been written to ttt.json.")
