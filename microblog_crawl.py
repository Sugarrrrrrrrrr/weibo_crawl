from selenium import webdriver
import re
import time
import datetime
import sys

class microblog_crawl:
    def __init__(self, b_i=-1, begin=7, end=7):
        self.pat_z_1 = re.compile(r'转发了 (.*?) 的微博:')
        self.pat_z_2 = re.compile(r'赞\[\d+\] 原文转发\[\d+\] 原文评论\[\d+\]')

        self.pat_y_1 = re.compile(r'赞\[(\d+)\] 转发\[(\d+)\] 评论\[(\d+)\] 收藏 (\d+)月(\d+)日 (\d+):(\d+).*?$')
        self.pat_y_2 = re.compile(r'赞\[(\d+)\] 转发\[(\d+)\] 评论\[(\d+)\] 收藏 (\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+).*?$')
        self.pat_y_3 = re.compile(r'赞\[(\d+)\] 转发\[(\d+)\] 评论\[(\d+)\] 收藏 今天 (\d+):(\d+).*?$')
        self.pat_y_4 = re.compile(r'赞\[(\d+)\] 转发\[(\d+)\] 评论\[(\d+)\] 收藏 (\d+)分钟前.*?$')
        self.non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

        self.begin_list = []
        self.begin_list_init()

        self.start_time = time.time()
        b_dt = datetime.datetime.fromtimestamp(self.start_time) - datetime.timedelta(days=(begin-1))
        self.max_time = time.mktime((b_dt.year, b_dt.month, b_dt.day, 0, 0, 0, 0, 0, 0))
        e_dt = datetime.datetime.fromtimestamp(self.start_time) - datetime.timedelta(days=(end))
        self.min_time = time.mktime((e_dt.year, e_dt.month, e_dt.day, 0, 0, 0, 0, 0, 0))
 
        self.b_i = b_i
        self.d = {}
        log_name = time.strftime('log_%Y-%m-%d', time.localtime(self.start_time)) + '_' + str(int(time.time())) + '.txt'
        self.log = open(log_name, 'w', encoding='utf-8')

        self.driver = webdriver.Edge()
        self.run()

    def begin_list_init(self, uids_file = 'uids.txt'):
        with open(uids_file, 'r') as f:
            for line in f:
                self.begin_list.append(line)
    
    def run(self):
        for i, uid in enumerate(self.begin_list):
            self.usr_crawl(uid.strip(), i+1)

    def usr_crawl(self, uid, index=-1):
        # init uid
        self.d = {}
        self.d['uid'] = uid
        if self.b_i != -1 and index < self.b_i:
            return
        self.page_crawl(uid, page=1, index=index)

    def page_crawl(self, uid, page, index=-1):
        if index != -1:
            print ('page_crawl', index, uid, page)
        else:
            print('page_crawl', uid, page)
            
        time.sleep(2)
        print('sleep')

        if page == 1:
            url = 'https://weibo.cn/u/' + uid
        else:
            url = 'https://weibo.cn/u/' + uid + '?page=' + str(page)
        self.driver.get(url)

        # get poster
        if page == 1:
            try:
                span = self.driver.find_element_by_xpath('/html/body/div[3]/table/tbody/tr/td[2]/div/span[1]')
                self.d['poster'] = span.text.split('\xa0')[0]
            except Exception as e:
                pass

        # microblogs in single page
        div_c_s = self.driver.find_elements_by_class_name('c')
        for i, div in enumerate(div_c_s):
            # single microblog
            div_s = div.find_elements_by_tag_name('div')
            if div_s:
                s = ''
                isTop = False # 是否置顶
                
                # get mid
                mid = div.get_attribute('id')
                if mid.startswith('M_'):
                    self.d['mid'] = mid[2:]

                # get time, count, content
                for div in div_s:
                    text = div.text


                    s_d = '[置顶]'
                    s_z = '转发了 '
                    s_y = '转发理由:'

                    if text.startswith(s_d):
                        isTop = True
                        text = text[len(s_d):]
                    
                    if text.startswith(s_z):
                        text = self.pat_z_1.sub(r'//@\1:', text)
                        text = self.pat_z_2.sub('', text)
                        s = s + text
                        # print (text)
                        
                    elif text.startswith(s_y):
                        text = text[len(s_y):]
                        match = self.pat_y_1.search(text)
                        if match:
                            year = time.localtime()[0]
                            second = 0
                            like_count, forward_count, comment_count, month, day, hour, minute = match.groups()
                            text = self.pat_y_1.sub('', text)
                        else:
                            match = self.pat_y_2.search(text)
                            if match:
                                like_count, forward_count, comment_count, year, month, day, hour, minute, second = match.groups()
                                text = self.pat_y_2.sub('', text)
                            else:
                                match = self.pat_y_3.search(text)
                                if match:
                                    year = time.localtime()[0]
                                    month = time.localtime()[1]
                                    day = time.localtime()[2]
                                    second = 0
                                    like_count, forward_count, comment_count, hour, minute = match.groups()
                                    text = self.pat_y_3.sub('', text)
                                else:
                                    match = self.pat_y_4.search(text)
                                    if match:
                                        like_count, forward_count, comment_count, td_minute = match.groups()
                                        t_post =  datetime.datetime.fromtimestamp(time.time()) - datetime.timedelta(minutes = int(td_minute))
                                        year = t_post.year
                                        month = t_post.month
                                        day = t_post.day
                                        hour = t_post.hour
                                        minute = t_post.minute
                                        second = 0
                                        text = self.pat_y_4.sub('', text)
                        s = text + s
                        # print (text)

                    else:
                        text = self.pat_z_2.sub('', text)
                        
                        match = self.pat_y_1.search(text)
                        if match:
                            year = time.localtime()[0]
                            second = 0
                            like_count, forward_count, comment_count, month, day, hour, minute = match.groups()
                            text = self.pat_y_1.sub('', text)
                        else:
                            match = self.pat_y_2.search(text)
                            if match:
                                like_count, forward_count, comment_count, year, month, day, hour, minute, second = match.groups()
                                text = self.pat_y_2.sub('', text)
                            else:
                                match = self.pat_y_3.search(text)
                                if match:
                                    year = time.localtime()[0]
                                    month = time.localtime()[1]
                                    day = time.localtime()[2]
                                    second = 0
                                    like_count, forward_count, comment_count, hour, minute = match.groups()
                                    text = self.pat_y_3.sub('', text)
                                else:
                                    match = self.pat_y_4.search(text)
                                    if match:
                                        like_count, forward_count, comment_count, td_minute = match.groups()
                                        t_post =  datetime.datetime.fromtimestamp(time.time()) - datetime.timedelta(minutes = int(td_minute))
                                        year = t_post.year
                                        month = t_post.month
                                        day = t_post.day
                                        hour = t_post.hour
                                        minute = t_post.minute
                                        second = 0
                                        text = self.pat_y_4.sub('', text)
                        s = s + text
                        # print (text)

                    # print('------')
                content = s
                t_ = (int(year), int(month), int(day), int(hour), int(minute), int(second), 0, 0, 0)
                self.d['time'] = time.strftime('%x %X', t_)
                t = time.mktime(t_)
                if t < self.min_time and not isTop:
                    return
                
                self.d['forward_count'] = forward_count
                self.d['comment_count'] = comment_count
                self.d['like_count'] = like_count
                self.d['content'] = re.sub('\n', ' ', content).translate(self.non_bmp_map)

                if False:
                    l = ['uid', 'poster', 'mid', 'time', 'forward_count', 'comment_count', 'like_count', 'content']
                    for key in l:
                        print (self.d[key])

                self.write_log()
                # input('pause')
        try:
            next_page = self.driver.find_element_by_partial_link_text('下页')
        except Exception as e:
            return
        
        self.page_crawl(uid, page+1, index)

    def write_log(self):
        line = '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (self.d['uid'], self.d['poster'], self.d['mid'], self.d['time'], self.d['forward_count'], self.d['comment_count'], self.d['like_count'], self.d['content'])
        # print(line)
        self.log.write(line)
        self.log.write('\n')
        self.log.flush()
        
if __name__ == '__main__':
    mc = microblog_crawl()
