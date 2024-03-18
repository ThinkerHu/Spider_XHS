import requests
import time
import csv

from xhs_utils.xhs_util import get_comment_cookies

f = open('小红书评论.csv', mode='a', encoding='utf-8', newline='')
csv_writer = csv.DictWriter(f, fieldnames=['ID', '父帖ID', '笔记ID', '内容', '发布时间', '昵称', '头像链接',
                                           '用户id',
                                           '帖子类型'])
csv_writer.writeheader()


def spider(url):
    localCookie = get_comment_cookies()
    headers = {
        "Cookie": localCookie,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(url=url, headers=headers).json()
    return response


def get_time(ctime):
    timeArray = time.localtime(int(ctime / 1000))
    otherStyleTime = time.strftime("%Y.%m.%d", timeArray)
    return str(otherStyleTime)


def get_sub_comments(note_id, root_comment_id, sub_comment_cursor):
    while True:
        url = f"https://edith.xiaohongshu.com/api/sns/web/v2/comment/sub/page?note_id={note_id}&root_comment_id={root_comment_id}&num=10&cursor={sub_comment_cursor}&image_formats=jpg,webp,avif"
        time.sleep(0.2)
        sub_comment_data = spider(url)
        for index in sub_comment_data['data']['comments']:
            print("帖子详情")
            dit_1 = {
                'ID': index['id'].strip(),
                '父帖ID': root_comment_id,
                '笔记ID': note_id,
                '内容': index['content'].strip(),
                '发布时间': get_time(index['create_time']),
                '昵称': index['user_info']['nickname'].strip(),
                '头像链接': index['user_info']['image'],
                '用户id': index['user_info']['user_id'],
                '帖子类型': '二级评论'
            }
            csv_writer.writerow(dit_1)
        if not sub_comment_data['data']['has_more']:
            break
        sub_comment_cursor = sub_comment_data['data']['cursor']


def get_comments(note_id):
    cursor = ''
    page = 0
    while True:
        time.sleep(0.2)
        url = f"https://edith.xiaohongshu.com/api/sns/web/v2/comment/page?note_id={note_id}&cursor={cursor}"
        json_data = spider(url)
        for index in json_data['data']['comments']:
            dit = {
                'ID': index['id'].strip(),
                '父帖ID': '',
                '笔记ID': note_id,
                '内容': index['content'].strip(),
                '发布时间': get_time(index['create_time']),
                '昵称': index['user_info']['nickname'].strip(),
                '头像链接': index['user_info']['image'],
                '用户id': index['user_info']['user_id'],
                '帖子类型': '一级评论'
            }
            csv_writer.writerow(dit)
            get_sub_comments(note_id, index['id'], index['sub_comment_cursor'])
        if not json_data['data']['has_more']:
            break
        cursor = json_data['data']['cursor']
        page = page + 1
        print(f'正在打印帖子ID为{note_id}的第{page}页评论数据')
