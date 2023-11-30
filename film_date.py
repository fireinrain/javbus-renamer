import os
import re

import requests
from bs4 import BeautifulSoup

import utils


# 获取作品信息
def fetch_film_info(code: str) -> {}:
    # URL to send the GET request to
    code = code.upper()
    # 桃子特有
    if code == 'AP-027':
        code = code + "_2018-07-11"
    url = f"https://www.javbus.com/{code}"

    # Custom headers
    headers = {
        'authority': 'www.javbus.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh,en;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7,ja;q=0.6',
        'cache-control': 'max-age=0',
        'cookie': 'PHPSESSID=r5vcbumug9golfcic7juk6oba3; 4fJN_2132_seccodecSAJL4TJ8GJH=11161.d933c2686777d0cfb0; 4fJN_2132_lastcheckfeed=576343%7C1697851770; 4fJN_2132_nofavfid=1; 4fJN_2132_lip=172.70.122.159%2C1697851781; 4fJN_2132_ulastactivity=d904a01rINv29Bt6olBES08uFwqtxP7YA06jkgxU8cxkAsv9uB%2B1; 4fJN_2132_auth=a50cI7AENAtN%2FOrFfQHVLuQs8TQwROGraxac8scKFKheQFBqA2YMGRnJ9R9N64jUyN48rE1qFVA6kdaHKghKYuXEErw; bus_auth=ce4dK9xmji9gnnfTwnqQGRi1Ppw%2BmztGtvna7nZ9bLjY0CSRFcNYtECvXmylJGbitKQ; existmag=mag',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }

    # Send GET request with custom headers
    response = requests.get(url, timeout=6, headers=headers)

    av_info = {}
    # Check the status code of the response
    if response.status_code == 200:
        # Request was successful

        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, 'lxml')
        # 获取到的网页信息需要进行解析，使用lxml解析器，其实默认的解析器就是lxml，但是这里会出现警告提示，方便你对其他平台移植
        webtitle = str(soup.h3.string)
        # print(webtitle)
        av_info['avid'] = webtitle.split(" ")[0]
        # print(avid)
        av_info['avdesc'] = webtitle[len(av_info['avid']) + 1:len(webtitle)]
        av_info['product_date'] = re.search(
            r'\d\d\d\d.\d\d.\d\d', response.text).group(0)
        if re.search(r'(\d+)分鐘', response.text) is not None:
            av_info['duartion'] = re.search(r'(\d+)分鐘', response.text).group(1)
        else:
            av_info['duartion'] = ''

        if re.search('導演:<.*">(.*)</a></p>', response.text) is not None:
            av_info['director'] = re.search(
                '導演:<.*">(.*)</a></p>', response.text)[1]
        else:
            av_info['director'] = ''
        if re.search('系列:<.*">(.*)</a>', response.text) is not None:
            av_info['series'] = re.search('系列:<.*">(.*)</a>', response.text)[1]
        else:
            av_info['series'] = ''
        av_info['Category'] = re.findall(
            '<input type="checkbox" name="gr_sel".*">(.*)</a>',
            response.text)
        if re.search('製作商:<.*">(.*)</a>', response.text) is not None:
            av_info['producer'] = re.search('製作商:<.*">(.*)</a>', response.text)[1]
        else:
            av_info['producer'] = ''
        if re.search('發行商:<.*">(.*)</a>', response.text) is not None:
            av_info['issuer'] = re.search('發行商:<.*">(.*)</a>', response.text)[1]
        else:
            av_info['issuer'] = ''
        if re.findall(
                '<a href="https://www.javbus.com/star/.{3,5}">(.{1,8})</a>', response.text) is not None:
            av_info['actors'] = re.findall(
                '<a href="https://www.javbus.com/star/.{3,5}">(.{1,8})</a>',
                response.text)
        else:
            av_info['actors'] = ''
        gid = re.search(r'var gid = (\d{10,12});', response.text).group(1)
        uc = re.search(r'var uc = (\d+);', response.text).group(1)
        img = re.search('var img = \'(.*)\';', response.text).group(1)
        # 发行日期
        # publish_date = dom.xpath('/html/body/div[5]/div[1]/div[2]/p[2]')
        # if publish_date:
        #     result['publish_date'] = publish_date
        # else:
        #     result['publish_date'] = ''
        av_info['gid'] = gid
        av_info['uc'] = uc
        av_info['img'] = img

        # print(av_info)
        # print("Success! Response content:", response.text)

    else:
        # Request failed
        print(f"Error! Status code: {response.status_code}")
        print("当前番号:", code)
    return av_info


def is_start_with_date_string(s):
    # 定义日期字符串的正则表达式
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}')

    # 使用正则表达式进行匹配
    match = date_pattern.match(s)

    # 如果匹配成功，返回True，否则返回False
    return bool(match)


# # ipx-005 别识别成了ipx-500
#     # ipx-072   ipx-720
#     # ipx-077   ipx-770
#     # ipx-088   ipx-880
#  需要注意有些作品被错误rename了
#  因为一个bug
# 给作品目录
def update_film_folder_date(film_folder: str):
    for root, dirs, files in os.walk(film_folder):
        # print(root)
        # print(dirs)
        if dirs:
            for dir in dirs:
                date_string = is_start_with_date_string(dir)
                if date_string:
                    continue
                temp = dir
                clean_folder_name = dir.replace("【", "").replace("】", " ")
                if len(temp) == clean_folder_name:
                    continue

                folder_name_split = clean_folder_name.split(" ")
                code = ""
                for name in folder_name_split:
                    if "-" in name:
                        code = name
                        break
                film_info = fetch_film_info(code)
                publish_date = film_info['product_date']
                new_folder = root + os.sep + publish_date + temp
                older_foder = root + os.sep + temp
                print(f"old folder: {older_foder} ---> new folder: {new_folder}")
                os.rename(older_foder, new_folder)
                # print(older_foder)
        print("--------------------------")


if __name__ == '__main__':
    path = utils.get_directory()
    print(path)
    print('已选择文件夹：' + path + '\n')
    print('...文件夹更新日期开始...如果时间过长...请避开中午夜晚高峰期...\n')
    update_film_folder_date(path)
    # info = fetch_film_info("ipzz-034")
    # print(info)
