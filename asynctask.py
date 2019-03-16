# coding=utf-8
import logging
import requests
import os
from celery import Celery


BROKER_URL = 'redis://127.0.0.1:6379'
app = Celery('image_downloader', broker=BROKER_URL)
LOGGER = logging.getLogger(__name__)
BASIC_FOLDER = 'htmlcache'


@app.task
def crawl_tieba_info(game_tieba, basic_type_name):
    if len(game_tieba['gamename']) < 1:
        return
    try:
        folder = "./{0}/{1}".format(BASIC_FOLDER, basic_type_name)
        if not os.path.isdir(folder):
            os.makedirs(folder)
    except OSError:
        LOGGER.error('err making dir ' + folder)
        return
    try:
        filename = folder + "/" + game_tieba['gamename'] + ".html"
        # 跳过已经下载的
        if os.path.isfile(filename):
            LOGGER.info('file exists: '+filename)
            return
        html = requests.get(game_tieba['link'], stream=True)
        with open(filename, 'wb') as f:
            f.write(html.content)
        # LOGGER.info('done: '+game_tieba['gamename'])
    except Exception as exc:
        LOGGER.error('err in ' + game_tieba['gamename'])
