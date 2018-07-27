from selenium import webdriver
import re
import time
import datetime
import sys

driver = webdriver.Edge()
uid_list = ['5655248349', '1291477752', '1792634467']

if __name__ == '__main__':

    pat_z_1 = re.compile(r'转发了 (.*?) 的微博:')
    pat_z_2 = re.compile(r'赞\[\d+\] 原文转发\[\d+\] 原文评论\[\d+\]')

    pat_y_1 = re.compile(r'赞\[(\d+)\] 转发\[(\d+)\] 评论\[(\d+)\] 收藏 (\d+)月(\d+)日 (\d+):(\d+).*?$')
    pat_y_2 = re.compile(r'赞\[(\d+)\] 转发\[(\d+)\] 评论\[(\d+)\] 收藏 (\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+).*?$')
    pat_y_3 = re.compile(r'赞\[(\d+)\] 转发\[(\d+)\] 评论\[(\d+)\] 收藏 今天 (\d+):(\d+).*?$')
    pat_y_4 = re.compile(r'赞\[(\d+)\] 转发\[(\d+)\] 评论\[(\d+)\] 收藏 (\d+)分钟前.*?$')
    
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

    uid = '1682534647'
    mid = ''
    t = ''
    forward_count = ''
    comment_count = ''
    like_count = ''
    content = ''
    poster = ''

    page = 1

    if page == 1:
        url = 'https://weibo.cn/u/' + uid
    else:
        url = 'https://weibo.cn/u/' + uid + '?page=' + str(page)

    driver.get(url)

    # get poster
    if page == 1:
        try:
            span = driver.find_element_by_xpath('/html/body/div[3]/table/tbody/tr/td[2]/div/span[1]')
            poster = span.text.split('\xa0')[0]
        except Exception as e:
            pass
    

    div_c_s = driver.find_elements_by_class_name('c')

    for i, div in enumerate(div_c_s):
        if i in []:
            continue
        print(i, '------')

        div_s = div.find_elements_by_tag_name('div')

        if div_s:
            s = ''
            mid = div.get_attribute('id')
            if mid.startswith('M_'):
                mid = mid[2:]

            for div in div_s:
                text = div.text

                s_z = '转发了 '
                s_y = '转发理由:'
                
                if text.startswith(s_z):
                    text = pat_z_1.sub(r'//@\1:', text)
                    text = pat_z_2.sub('', text)
                    s = s + text
                    # print (text)
                    
                elif text.startswith(s_y):
                    text = text[len(s_y):]
                    match = pat_y_1.search(text)
                    if match:
                        year = time.localtime()[0]
                        second = 0
                        like_count, forward_count, comment_count, month, day, hour, minute = match.groups()
                        text = pat_y_1.sub('', text)
                    else:
                        match = pat_y_2.search(text)
                        if match:
                            like_count, forward_count, comment_count, year, month, day, hour, minute, second = match.groups()
                            text = pat_y_2.sub('', text)
                        else:
                            match = pat_y_3.search(text)
                            if match:
                                year = time.localtime()[0]
                                month = time.localtime()[1]
                                day = time.localtime()[2]
                                second = 0
                                like_count, forward_count, comment_count, hour, minute = match.groups()
                            else:
                                match = pat_y_4.search(text)
                                if match:
                                    like_count, forward_count, comment_count, td_minute = match.groups()
                                    t_post =  datetime.datetime.fromtimestamp(time.time()) - datetime.timedelta(minutes = int(td_minute))
                                    year = t_post.year
                                    month = t_post.month
                                    day = t_post.day
                                    hour = t_post.hour
                                    minute = t_post.minute
                                    second = 0
                    s = text + s
                    # print (text)

                else:
                    match = pat_y_1.search(text)
                    if match:
                        year = time.localtime()[0]
                        second = 0
                        like_count, forward_count, comment_count, month, day, hour, minute = match.groups()
                        text = pat_y_1.sub('', text)
                    else:
                        match = pat_y_2.search(text)
                        if match:
                            like_count, forward_count, comment_count, year, month, day, hour, minute, second = match.groups()
                            text = pat_y_2.sub('', text)
                        else:
                            match = pat_y_3.search(text)
                            if match:
                                year = time.localtime()[0]
                                month = time.localtime()[1]
                                day = time.localtime()[2]
                                second = 0
                                like_count, forward_count, comment_count, hour, minute = match.groups()
                            else:
                                match = pat_y_4.search(text)
                                if match:
                                    like_count, forward_count, comment_count, td_minute = match.groups()
                                    t_post =  datetime.datetime.fromtimestamp(time.time()) - datetime.timedelta(minutes = int(td_minute))
                                    year = t_post.year
                                    month = t_post.month
                                    day = t_post.day
                                    hour = t_post.hour
                                    minute = t_post.minute
                                    second = 0
                                    
                    s = s + text
                    # print (text)

                print('------')
            content = s
            t_ = (int(year), int(month), int(day), int(hour), int(minute), int(second), 0, 0, 0)
            t = time.strftime('%x %X', t_)
            
            print(uid)
            print(mid)
            print(t)
            print(forward_count)
            print(comment_count)
            print(like_count)
            print(re.sub('\n', ' ', content).translate(non_bmp_map))
            print(poster)

        print('-------------------------')
        
