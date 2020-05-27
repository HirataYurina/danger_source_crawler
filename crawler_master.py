# -*- coding:utf-8 -*-
# author:平手友梨奈ii
# e-mail:1353593259@qq.com
# datetime:2020/4/11 0011 10:18
# filename:crawler.py
# software: PyCharm

import requests
from bs4 import BeautifulSoup
import re
import os
import csv

# 首先连接登录页面 并且保存登录状态
DATA = {"username":'your username', "password":'your password'}
# gid_lis = ['157', '158', '159', '160', '161', '162', '163', '164', '165', '166', '167', '168', '169', '171']
# company_lis = ['第一分司', '第二分司', '第三分司', '第四分司', '第五分司', '第六分司', '第八分司',
#                '第九分司', '第十分司', '第十一分司', '第十二分司', '第十五分司', '第十六分司', '第十八分司']

gid_lis = ['165', '166', '167', '168', '169', '171']
company_lis = ['第十分司', '第十一分司', '第十二分司', '第十五分司', '第十六分司', '第十八分司']

path = 'http://www.cutcckms.com/forum.php?mod=forumdisplay&fid='
url_lis = []

for gid in gid_lis:
    photo_match = path + gid
    url_lis.append(photo_match)

def get_session():
    session = requests.Session()
    session.post('http://www.cutcckms.com/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes',
                 data=DATA)

    return session


def crawl_img(url_list, session):

    count1 = 0

    # 爬取每个分公司的照片
    for url in url_list:
        response1 = session.get(url)
        soup1 = BeautifulSoup(response1.text, 'lxml')
        pg_num = soup1.find('div', class_="pg").text
        pg_num = re.findall(' (.*) ', pg_num)
        page_num = pg_num[0].split('/')[1].strip()
        page_num = range(1, int(page_num) + 1)

        count2 = 0

        # 爬取每个页面的隐患分类
        for page in page_num:
            page_url = url + '&page=' + str(page)
            response2 = session.get(page_url)
            soup2 = BeautifulSoup(response2.text, 'lxml')
            danger_categ_list = soup2.find_all('em')

            # 包含图片URL的页面
            description_lis = []
            img_url = []
            description_tag = soup2.find_all('a', class_='s xst')
            for description in description_tag:
                descrip = description.text
                description_lis.append(descrip)
                img_url.append(description['href'])

            count3 = 0

            # 为每个类别建立文件夹
            for danger_categ in danger_categ_list:
                danger_categ = danger_categ.text
                # 类别名称
                danger_categ = re.search('^\[[\S\s]*\]$', danger_categ)
                if danger_categ:
                    danger_categ = danger_categ.group(0)
                    if not os.path.exists('./' + danger_categ):
                        os.mkdir(path=danger_categ)

                    image_web_url = img_url[count3]
                    response3 = session.get(image_web_url)
                    soup3 = BeautifulSoup(response3.text, 'lxml')
                    src = soup3.find_all('ignore_js_op', soup3)

                    for s in src:

                        count2 += 1

                        img_src_list = s.find_all('img')
                        for img_src_ in img_src_list:
                            try:
                                img_src = img_src_['file']
                                img_src_url = 'http://www.cutcckms.com/' + img_src
                                img_name = company_lis[count1] + '_' + str(count2) + '.jpg'
                                danger_desp = description_lis[count3]

                                danger_source_img = requests.get(img_src_url).content
                                with open('./' + danger_categ + '/' + img_name, 'wb') as file:
                                    file.write(danger_source_img)

                                """
                                    注意编码格式为utf-8 否则会报编码错误
                                """
                                with open('./imgList.csv', 'a+', newline='', encoding="utf-8") as file:
                                    writer = csv.writer(file, delimiter=',')
                                    writer.writerow([img_name, danger_categ, danger_desp])
                            except KeyError:
                                print('------标签中没有file属性------')
                            except UnicodeEncodeError:
                                print('------编码错误------')
                    count3 += 1
        count1 += 1


if __name__ == '__main__':
    session = get_session()
    # 开始爬取图片
    crawl_img(url_lis, session)
