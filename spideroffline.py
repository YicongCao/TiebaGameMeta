# coding=utf-8
import os
import glob
import csv
import time
from urllib.parse import urljoin, urlencode, quote_plus

import spider
import utils

if __name__ == "__main__":
    csv_file = open("gametree.csv", "w", encoding="utf-8")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(
        ["gamename", "gametype", "follower_count", "topic_count", "tiebaurl"])
    total_count = 0
    time_start = time.time()
    for infile in glob.glob("./htmlcache/*/*.html"):
        folder, fullname = os.path.split(infile)
        parentfolder, subfolder = os.path.split(folder)
        filename, extension = os.path.splitext(fullname)
        try:
            with open(infile, 'r', encoding="utf-8") as f:
                game_tieba_html = f.read()
                followers, topics = utils.get_pop_of_tieba(game_tieba_html)
                tieba_url = spider.TIEBA_DETAIL_URL.format(
                    quote_plus(filename))
                csv_writer.writerow(
                    [filename, subfolder, str(followers), str(topics), tieba_url])
                total_count += 1
                print('parsed ', total_count, ' tieba: ', filename, ", type: ", subfolder,
                      ", followers: ", str(followers), ", topics: ", str(
                          topics), ", remaining: ",
                      str((time.time() - time_start)/(total_count+1)
                          * (60000-total_count)/60) + "min")
                if total_count % 20 == 0:
                    csv_file.flush()
        except Exception as e:
            print(e)
            continue
    csv_file.close()
