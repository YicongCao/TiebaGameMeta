# coding=utf-8
import requests
import json
import time
from urllib.parse import urljoin, urlencode, quote_plus
from urllib.request import urlopen

import utils
from asynctask import crawl_tieba_info


START_PAGE = "http://tieba.baidu.com/f/fdir?fd=%D3%CE%CF%B7&sd=%B5%E7%D7%D3%BE%BA%BC%BC%BC%B0%D1%A1%CA%D6"
TIEBA_DETAIL_URL = "https://tieba.baidu.com/f?kw={0}&ie=utf-8"

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
}

GAME_TREE_BASE_TYPE = "tree"
GAME_TREE_BASE_NAME = "gametype"
GAME_TREE_BASE_LINK = "link"
GAME_TREE_GAME_COLLECTION = "gamecollection"
GAME_TREE_GAME_TIEBA_NAME = "gamename"
GAME_TREE_GAME_TIEBA_LINK = "link"
GAME_TREE_GAME_TIEBA_FOLLOWERS = "followers"
GAME_TREE_GAME_TIEBA_TOPICS = "topics"

JSON_TEMP_FILE_NAME = "gametree"


def get_html_from_url(url):
    if None == url:
        return None
    try:
        r = requests.get(url, headers=HEADERS)
        if r.status_code != 200:
            print("open {0} failed".format(url))
            return None
        return r.text
    except:
        return None


def get_html_from_url_ex(url):
    if None == url:
        return None
    try:
        page = urlopen(url)
        html = page.read()
        html = html.decode('utf-8')
        return html
    except:
        return None


def crawl_tieba_info_test(game_tieba):
    if len(game_tieba['gamename']) < 1:
        return
    try:
        html = requests.get(game_tieba['link'], stream=True)
        with open(game_tieba['gamename'] + ".html", 'wb') as f:
            f.write(html.content)
    except Exception as exc:
        pass


if __name__ == "__main__":
    # 这次爬虫的写法选择了广度优先遍历
    # 如果是在一个for循环中直接爬完游戏分类、每个分类的游戏贴吧、以及每个贴吧的人气数据
    # 那样写的话就是深度优先遍历，以前主要也是这样写
    # 这次只是为了好玩：）

    # 如果meta信息已经dump到了本地，则不需要重新爬取
    game_tree = utils.read_json_from_file(JSON_TEMP_FILE_NAME)
    game_count = 61400
    if None == game_tree:
        print('gametree phase initializing...')
        index_html = get_html_from_url(START_PAGE)
        game_type_links = utils.get_href_in_td(index_html, 0)
        game_tree = {}
        game_tree[GAME_TREE_BASE_TYPE] = []
        # 补全 GameTree 第一部分 游戏品类的链接
        for link in game_type_links:
            game_tree[GAME_TREE_BASE_TYPE].append({
                GAME_TREE_BASE_NAME: link['text'],
                GAME_TREE_BASE_LINK: urljoin(START_PAGE, link['href'])
            })
            print("base type added: ", link['text'], " href: ", link['href'])
        print('gametree phase 1 done')
        # 补全 GameTree 第二部分 每个品类下游戏贴吧的链接
        game_count = 0
        for base_node in game_tree[GAME_TREE_BASE_TYPE]:
            game_type_html = get_html_from_url(base_node['link'])
            game_item_links = utils.get_href_in_td(game_type_html, 1)
            base_node[GAME_TREE_GAME_COLLECTION] = []
            for link in game_item_links:
                if len(str(link['text'])) > 1:
                    base_node[GAME_TREE_GAME_COLLECTION].append({
                        GAME_TREE_GAME_TIEBA_NAME: link['text'],
                        GAME_TREE_GAME_TIEBA_LINK: urljoin(
                            START_PAGE, link['href'])
                    })
                    print("game added: ", link['text'],
                          " type: ", base_node[GAME_TREE_BASE_NAME])
                    game_count += 1
        print('gametree phase 2 done')
        utils.dump_json_to_file(JSON_TEMP_FILE_NAME, game_tree)
    # 补全 GameTree 第三部分 每个游戏贴吧的关注人数、帖子数量信息
    timestamp_start = time.time()
    finished_count = 0
    for base_node in game_tree[GAME_TREE_BASE_TYPE]:
        for game_tieba in base_node[GAME_TREE_GAME_COLLECTION]:
            try:
                # 以前同步爬取的代码，慢到天际
                # if GAME_TREE_GAME_TIEBA_FOLLOWERS in game_tieba:
                #     continue
                # if len(str(game_tieba[GAME_TREE_GAME_TIEBA_NAME])) <= 1:
                #     game_tieba[GAME_TREE_GAME_TIEBA_FOLLOWERS] = 0
                #     game_tieba[GAME_TREE_GAME_TIEBA_TOPICS] = 0
                #     continue
                # game_tieba_detail_url = TIEBA_DETAIL_URL.format(
                #     quote_plus(game_tieba[GAME_TREE_GAME_TIEBA_NAME]))
                # game_tieba_html = get_html_from_url_ex(game_tieba_detail_url)
                # if None == game_tieba_html:
                #     continue
                # followers, topics = utils.get_pop_of_tieba(game_tieba_html)
                # # followers, topics = utils.get_pop_of_tieba(None)
                # game_tieba[GAME_TREE_GAME_TIEBA_FOLLOWERS] = followers
                # game_tieba[GAME_TREE_GAME_TIEBA_TOPICS] = topics
                # print("tieba added: ", game_tieba[GAME_TREE_GAME_TIEBA_NAME],
                #       " followers: ", followers, " topics: ", topics, " progress: ",
                #       finished_count, "/", game_count, " time remains: " +
                #       str((time.time() - timestamp_start) *
                #           (game_count-finished_count)/(finished_count+1)/3600) + "h")
                # finished_count += 1
                # if finished_count % 500 == 0:
                #     print("dumping json to file")
                #     utils.dump_json_to_file(JSON_TEMP_FILE_NAME, game_tree)

                # 改为使用消息队列并发爬取六万多条信息
                # 等都爬取完成后，再运行spideroffline.py来离线统计结果
                crawl_tieba_info.delay(
                    game_tieba, base_node[GAME_TREE_BASE_NAME])

            except Exception as e:
                print(e)
                continue
    print('gametree phase 3 done')
    # utils.export_game_tree_to_csv(game_tree)
    print('gametree export done')
    print('finished')
