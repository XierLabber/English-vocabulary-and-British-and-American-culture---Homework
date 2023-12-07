import json

import numpy as np
from pyecharts import options as opts
from pyecharts.charts import WordCloud, Bar, Pie

roots_set = {}
recorded_words = {}
normalized_lists = {}

def read_lines_to_set(file_path="./roots.txt"):
    global roots_set
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # 移除每行末尾的换行符，并将字符串添加到集合中
                result = line.rstrip()
                if len(result) != 0:
                    roots_set[result] = 0
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def init():
    global recorded_words
    read_lines_to_set()
    recorded_words = {}

def update(str):
    maxx_len = 0
    tar = ""
    for start in range(len(str)):
        for end in range(start + 1, len(str) + 1):
            if start == 0 and end == len(str):
                continue
            if start != 0 and end != len(str):
                continue
            substring = str[start:end]
            if substring in roots_set.keys():
                tmp_len = end - start
                if tmp_len > maxx_len:
                    maxx_len = tmp_len
                    tar = substring
    
    if maxx_len != 0:
        roots_set[tar] += 1
        if not tar in recorded_words.keys():
            recorded_words[tar] = set()
        recorded_words[tar].add(str)

def read_words_from_file(file_name):
    file_path = "./papers_to_cnt/" + file_name
    with open(file_path) as file:
        for line in file:
            # 使用 split() 将每一行分割成单词
            line_words = line.split()
            for word in line_words:
                word = word.lower()
                word = ''.join(char for char in word if char.isalpha())
                update(word)

def generate_tuple_list():
    ret = []
    for item, val in roots_set.items():
        if val != 0:
            ret.append((item, val))
    return ret

def work_for_file(file_name, top_k = 10):
    init()
    # file_name = "BitSense"
    # file_name = "deTector"
    # file_name = "gpt"
    # file_name = "gpt1"
    # file_name = "gpt2"
    read_words_from_file(file_name + ".txt")
    WordCloud().add(series_name="词根分析", data_pair=generate_tuple_list(), word_size_range=[6, 200]).set_global_opts(
        title_opts=opts.TitleOpts(
            title="词根分析", title_textstyle_opts=opts.TextStyleOpts(font_size=23)
        ),
        tooltip_opts=opts.TooltipOpts(is_show=True),
    ).render(file_name + "_clouds.html")

    # if file_name == "cyclegan":
    #     print(generate_tuple_list())

    sorted_items = sorted(roots_set.items(), key=lambda x: x[1], reverse=True)
    top_k_items = sorted_items[:top_k]

    Bar().add_xaxis(
        list(x[0] for x in top_k_items)
    ).add_yaxis("词频", list(x[1] for x in top_k_items)).set_global_opts(
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
        title_opts=opts.TitleOpts(title=f"""top {top_k}词频统计""", subtitle=f"""{file_name}"""),
    ).render(file_name + "_bar.html")

    Pie().add(
        series_name="访问来源",
        data_pair=top_k_items,
        rosetype="radius",
        radius="55%",
        center=["50%", "50%"],
        label_opts=opts.LabelOpts(is_show=False, position="center"),
    ).set_global_opts(title_opts=opts.TitleOpts(title="词频统计")).set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}")).render(file_name + "_pie.html")

    # print(recorded_words)
    # print(file_name + ".json")
    for key, val in recorded_words.items():
        recorded_words[key] = list(val)
    with open(file_name + ".json", 'w') as file:
        json.dump(recorded_words, file, indent=4)
    
    val_list = list(roots_set.values())
    normalized_lists[file_name] = np.array(val_list) / np.sum(val_list)

def kl_divergence(p, q):
    return np.sum(p * np.log((p + 1e-6) / (q + 1e-6)))

if __name__ == "__main__":
    file_names = [
        "BitSense", 
        "deTector", 
        "cyclegan",
        "gpt", 
        "gpt1", 
        "gpt2"
    ]
    for file_name in file_names:
        work_for_file(file_name)
    
    tmp_str = '| |' + '|'.join(file_names) + '|'
    print(tmp_str)
    tmp_str = '-' * 6 + '|'
    print('|' + tmp_str * (len(file_names) + 1))

    for i in range(len(file_names)):
        i_name = file_names[i]
        print('|' + i_name + '|', end='')
        for j in range(0, len(file_names)):
            j_name = file_names[j]
            # if i == 0 and j == 1:
            #     print(normalized_lists[j_name])
            print(f"{kl_divergence(normalized_lists[j_name], normalized_lists[i_name]):.6f}", '|', end='')
        print()
