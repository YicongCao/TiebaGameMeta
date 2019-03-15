# coding=utf-8
import json
import os
import csv
import math
from bs4 import BeautifulSoup

import spider

GAME_TIEBA_COUNT_ONE_PAGE = 40 * 5
csv_f = None
csv_w = None

# 获取网页上两个Table内部的所有链接


def get_href_in_td(html, td_index):
    if None == html:
        print('html_text is None')
        return None
    soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
    if None == soup:
        print('soup parse failed')
        return None
    # find td tags
    td_collection = soup.find_all('table')
    if None == td_collection:
        print('soup find td failed')
        return None
    if td_index >= len(td_collection):
        print('td_index out of range: ', td_index, len(td_collection))
        return None
    td_item = td_collection[td_index]
    # find href tags
    hrefs = td_item.find_all('a')
    if None == hrefs:
        print('find no hrefs within td')
        return None
    href_set = []
    for href in hrefs:
        # 游戏贴吧链接区
        if (td_index == 1):
            href_item = {
                'href': href.attrs['href'],
                'text': href.text
            }
            href_set.append(href_item)
        # 游戏类型聚合区
        elif (td_index == 0):
            pop_count_str = href.parent.text
            pop_count_str = pop_count_str.replace(
                href.text, "").replace("(", "").replace(")", "").strip()
            guess_page_count = math.ceil(
                int(pop_count_str) / GAME_TIEBA_COUNT_ONE_PAGE)
            base_href = href.attrs['href'].replace("&pn=1", "")
            for i in range(guess_page_count):
                href_set.append({
                    'href': base_href + "&pn=" + str(i+1),
                    'text': href.text
                })
    if len(href_set) == 0:
        print('warning: empty href_set')
    return href_set


# 获取一个贴吧的关注数、帖子数
def get_pop_of_tieba(html):
    if None == html:
        print('html_text is None')
        return 0, 0
    soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
    if None == soup:
        print('soup parse failed')
        return 0, 0
    # find td tags
    try:
        span_collection = soup.find_all('span', class_="card_menNum")
        follower_count = str(span_collection[0].text).replace(",", "")
        span_collection = soup.find_all('span', class_="card_infoNum")
        topic_count = str(span_collection[0].text).replace(",", "")
        return int(follower_count), int(topic_count)
    except:
        return 0, 0


# 导出 GameTree 到 CSV 表格
def export_game_tree_to_csv(tree):
    with open("gametree_final.csv", "w", encoding="utf-8") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(
            ["gamename", "gametype", "follower_count", "topic_count", "tiebaurl"])
        for base_node in tree[spider.GAME_TREE_BASE_TYPE]:
            for game_tieba in base_node[spider.GAME_TREE_GAME_COLLECTION]:
                csv_writer.writerow(
                    [game_tieba[spider.GAME_TREE_GAME_TIEBA_NAME],
                     base_node[spider.GAME_TREE_BASE_NAME],
                     str(game_tieba[spider.GAME_TREE_GAME_TIEBA_FOLLOWERS]),
                     str(game_tieba[spider.GAME_TREE_GAME_TIEBA_TOPICS]),
                     game_tieba[spider.GAME_TREE_GAME_TIEBA_LINK]])


# 支持断点续传：初始化 CSV
def init_game_tree_csv():
    csv_f = open("gametree_progress.csv", "w", encoding="utf-8")
    csv_w = csv.writer(csv_f)
    csv_w.writerow(
        ["gamename", "gametype", "follower_count", "topic_count", "tiebaurl"])


# 支持断点续传：续写 CSV
def append_game_tree_csv(data):
    csv_w.writerow(data)
