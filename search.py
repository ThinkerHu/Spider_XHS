import csv
import json
import re
import requests

from comment import get_comments
from one import OneNote
from xhs_utils.xhs_util import get_headers, get_search_data, get_params, js, check_cookies, timestamp_to_str, \
    is_timestamp_between_dates, timestamp_to_time, contains_strings

search_key = "北京 雾霾"


class Search:

    def __init__(self, cookies=None):
        self.csv_writer = None
        if cookies is None:
            self.cookies = check_cookies()
        else:
            self.cookies = cookies
        self.search_url = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"
        self.headers = get_headers()
        self.params = get_params()
        self.oneNote = OneNote(self.cookies)

    def init_csv_writer(self, keyword, startDate, endDate):
        f = open(f'话题【{keyword}】从{startDate}到{endDate}相关笔记.csv', mode='a', encoding='utf-8', newline='')
        self.csv_writer = csv.DictWriter(f,
                                         fieldnames=['笔记ID', '用户昵称', '帖子类型', '帖子链接', '发布时间',
                                                     '发布日期', '标题',
                                                     '内容',
                                                     '点赞数', '收藏数', '评论数'])
        self.csv_writer.writeheader()

    def get_search_note(self, query, number):
        data = get_search_data()
        api = '/api/sns/web/v1/search/notes'
        data = json.dumps(data, separators=(',', ':'))
        data = re.sub(r'"keyword":".*?"', f'"keyword":"{query}"', data)
        page = 0
        note_ids = []
        while len(note_ids) < number:
            page += 1
            data = re.sub(r'"page":".*?"', f'"page":"{page}"', data)
            ret = js.call('get_xs', api, data, self.cookies['a1'])
            self.headers['x-s'], self.headers['x-t'] = ret['X-s'], str(ret['X-t'])
            response = requests.post(self.search_url, headers=self.headers, cookies=self.cookies,
                                     data=data.encode('utf-8'))
            res = response.json()
            if not res['data']['has_more']:
                print(f'搜索结果数量为 {len(note_ids)}, 不足 {number}')
                break
            items = res['data']['items']
            for note in items:
                note_id = note['id']
                note_ids.append(note_id)
                if len(note_ids) >= number:
                    break
        return note_ids

    def search_note(self, query, start, end, sort):
        self.init_csv_writer(query, start, end)
        data = get_search_data()
        data['sort'] = sort
        api = '/api/sns/web/v1/search/notes'
        data = json.dumps(data, separators=(',', ':'))
        data = re.sub(r'"keyword":".*?"', f'"keyword":"{query}"', data)

        page = 0
        index = 0
        while True:
            page += 1
            data = re.sub(r'"page":".*?"', f'"page":"{page}"', data)
            ret = js.call('get_xs', api, data, self.cookies['a1'])
            self.headers['x-s'], self.headers['x-t'] = ret['X-s'], str(ret['X-t'])
            response = requests.post(self.search_url, headers=self.headers, cookies=self.cookies,
                                     data=data.encode('utf-8'))
            res = response.json()
            try:
                items = res['data']['items']
            except:
                print(f'搜索结果数量为 {index}')
                break
            for item in items:
                index += 1
                print(item)
                url = self.oneNote.detail_url + item['id']
                note = self.oneNote.get_one_note_info(url)
                if note is None:
                    print("帖子信息为空")
                else:
                    print(timestamp_to_str(note.upload_time))
                    if is_timestamp_between_dates(note.upload_time, start, end) & contains_strings(note.desc,
                                                                                                   search_key):
                        dit_1 = {
                            '笔记ID': note.note_id,
                            '用户昵称': note.nickname,
                            '帖子类型': note.note_type,
                            '帖子链接': url,
                            '发布时间': note.upload_time,
                            '发布日期': timestamp_to_time(note.upload_time),
                            '标题': note.title,
                            '内容': note.desc,
                            '点赞数': note.share_count,
                            '收藏数': note.collected_count,
                            '评论数': note.comment_count
                        }
                        self.csv_writer.writerow(dit_1)
                        get_comments(item['id'])
                    else:
                        print("is not in time or not contain keyword")

            if not res['data']['has_more']:
                print(f'搜索结果数量为 {index}')
                break

        print(f'搜索结果保存完成，共 {index} 个笔记')


if __name__ == '__main__':
    search = Search()
    start = "2019-03-16"
    end = "2024-03-16"
    # 排序方式 general: 综合排序 popularity_descending: 热门排序 time_descending: 最新排序
    sort = 'general'
    search.search_note(search_key, start, end, sort)
