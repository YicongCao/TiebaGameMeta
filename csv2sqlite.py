# coding=utf-8
import os
import csv
import json
import sqlite3

CLEAR_TABLE = '''
drop table if exists games;
'''

CREATE_TABLE = '''
create table games
(
    name varchar(255) default 'noname',
    type varchar(255) default 'notype',
    followers int default -1,
    topics int default -1,
    url varchar(255) default 'localhost'
);
'''

INSERT_DATA = '''
insert into games (name, type, followers, topics, url)
values ("{name}", "{type}", "{followers}", "{topics}", "{url}")
'''

QUERY_BY_NAME = '''
select *
from games where name LIKE "%{name}%" order by followers desc, topics desc
'''


conn = sqlite3.connect('gamesqlite.db')
cursor = conn.cursor()
cursor.execute(CLEAR_TABLE)
cursor.execute(CREATE_TABLE)
# gameset = set()

with open('gametree.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for line in reader:
        # if line['name'] in gameset:
        #     continue
        columns = {}
        columns['name'] = line['gamename'].replace("\"", "")
        columns['type'] = line['gametype']
        columns['followers'] = line['follower_count']
        columns['topics'] = line['topic_count']
        columns['url'] = line['tiebaurl']
        cursor.execute(INSERT_DATA.format(**columns))
        # gameset.add(line['name'])

print('insert {0} lines'.format(cursor.rowcount))
cursor.close()
conn.commit()
cursor = conn.cursor()
keyword = '王者荣耀'
query = {'name': keyword}
cursor.execute(QUERY_BY_NAME.format(**query))
result = cursor.fetchall()
print('games matching {0}:\r\n'.format(keyword))
for game in result:
    print(str(game) + '\r\n')
conn.close()
