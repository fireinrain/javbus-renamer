# -*- coding:utf-8 -*-
import re, os, configparser, time, hashlib, json, requests, shutil, traceback
from PIL import Image
from tkinter import filedialog, Tk
from time import sleep

import utils


# 获取用户选取的文件夹路径，返回路径str


# 记录错误txt，无返回
def write_fail(fail_m):
    record_txt = open('【记得清理它】失败记录.txt', 'a', encoding="utf-8")
    record_txt.write(fail_m)
    record_txt.close()


# 调用百度翻译API接口，返回中文简介str
def tran(api_id, key, word, to_lang):
    # init salt and final_sign
    salt = str(time.time())[:10]
    final_sign = api_id + word + salt + key
    final_sign = hashlib.md5(final_sign.encode("utf-8")).hexdigest()
    # 表单paramas
    paramas = {
        'q': word,
        'from': 'jp',
        'to': to_lang,
        'appid': '%s' % api_id,
        'salt': '%s' % salt,
        'sign': '%s' % final_sign
    }
    response = requests.get('http://api.fanyi.baidu.com/api/trans/vip/translate', params=paramas, timeout=10).content
    content = str(response, encoding="utf-8")
    json_reads = json.loads(content)
    try:
        return json_reads['trans_result'][0]['dst']
    except:
        print('    >正在尝试重新日译中...')
        return tran(api_id, key, word)


# 获取一个arzon_cookie，返回cookie
def get_acook():
    session = requests.Session()
    session.get(
        'https://www.arzon.jp/index.php?action=adult_customer_agecheck&agecheck=1&redirect=https%3A%2F%2Fwww.arzon.jp%2F',
        timeout=10)
    return session.cookies.get_dict()


# 控制台颜色
class ConsoleColor:
    RED = '\033[91m'
    GREEN = '\033[32m'
    END = '\033[0m'


def clean_video_folder(video_foler: str, video_type_tuple: ()):
    type_list = ["." + i for i in video_type_tuple]
    type_list.append(".torrent")
    tuple_ = tuple(type_list)
    # 遍历文件夹及其子文件夹
    for root, dirs, files in os.walk(video_foler):
        for file in files:
            file_path = os.path.join(root, file)

            # 如果文件是 .mp4 或 .torrent 文件，则保留，否则删除
            if file.lower().endswith(tuple_):
                print(f'{ConsoleColor.GREEN}保留文件: {file_path}{ConsoleColor.END}')
            else:
                print(f'{ConsoleColor.RED}删除文件: {file_path}{ConsoleColor.END}')
                os.remove(file_path)
        print("-------------------------------------------------")


def short_long_folder_name(folder_name: str) -> str:
    star_names = folder_name.replace("【", "").replace("】", " ")
    stars = star_names.split(" ")
    if len(stars) > 11:
        new_stars = stars[:10]
        new_stars[0] = "【" + new_stars[0]
        new_stars[9] = new_stars[9] + "】"
        new_stars.append(stars[-1])
        return " ".join(new_stars)

    return folder_name


# 每一部jav的“结构体”
class JavFile(object):
    def __init__(self):
        self.name = 'ABC-123.mp4'  # 文件名
        self.car = 'ABC-123'  # 车牌
        self.episodes = 0  # 第几集
        self.trim_prefix = ""


if __name__ == '__main__':
    #  main开始
    print('1、避开12:00-14：00和18:00-1:00，访问javlibrary和arzon很慢。\n'
          '2、若一直连不上javlibrary，请在ini中更新网址\n'
          '3、请确保每一个视频文件外层都有一个和她它对应的文件夹\n')
    # 读取配置文件，这个ini文件用来给用户设置重命名的格式和jav网址
    print('正在读取ini中的设置...', end='')
    config_settings = configparser.RawConfigParser()
    try:
        config_settings.read('config.ini', encoding='utf-8')
        if_nfo = config_settings.get("收集nfo", "是否收集nfo？")
        if_exnfo = config_settings.get("收集nfo", "是否跳过已存在nfo的文件夹？")
        if_review = config_settings.get("收集nfo", "是否收集javlibrary上的影评？")
        if_mp4 = config_settings.get("重命名影片", "是否重命名影片？")
        rename_mp4 = config_settings.get("重命名影片", "重命名影片的格式")
        if_folder = config_settings.get("修改文件夹", "是否重命名或创建独立文件夹？")
        rename_folder = config_settings.get("修改文件夹", "新文件夹的格式")
        if_classify = config_settings.get("归类影片", "是否归类影片？")
        classify_root = config_settings.get("归类影片", "归类的根目录")
        classify_basis = config_settings.get("归类影片", "归类的标准")
        if_jpg = config_settings.get("获取两张jpg", "是否获取fanart.jpg和poster.jpg？")
        if_qunhui = config_settings.get("获取两张jpg", "是否采取群辉video station命名方式？")
        if_sample_images = config_settings.get("获取样品图", "是否获取样品图")
        sample_images_format = config_settings.get("获取样品图", "样品图命名前缀格式")
        if_sculpture = config_settings.get("kodi专用", "是否收集女优头像")
        simp_trad = config_settings.get("其他设置", "简繁中文？")
        library_url = config_settings.get("其他设置", "javlibrary网址")
        bus_url = config_settings.get("其他设置", "javbus网址")
        suren_pref = config_settings.get("其他设置", "素人车牌(若有新车牌请自行添加)")
        file_type = config_settings.get("其他设置", "扫描文件类型")
        if_plot = config_settings.get("百度翻译API", "是否需要日语简介？")
        if_tran = config_settings.get("百度翻译API", "是否翻译为中文？")
        ID = config_settings.get("百度翻译API", "APP ID")
        SK = config_settings.get("百度翻译API", "密钥")
    except:
        print(traceback.format_exc())
        try:
            print('\n    >ini文件丢失...正在重写ini...')
            config_settings.add_section("收集nfo")
            config_settings.set("收集nfo", "是否收集nfo？", "是")
            config_settings.set("收集nfo", "是否跳过已存在nfo的文件夹？", "是")
            config_settings.set("收集nfo", "是否收集javlibrary上的影评？", "是")
            config_settings.add_section("重命名影片")
            config_settings.set("重命名影片", "是否重命名影片？", "是")
            config_settings.set("重命名影片", "重命名影片的格式", "车牌+空格+标题")
            config_settings.add_section("修改文件夹")
            config_settings.set("修改文件夹", "是否重命名或创建独立文件夹？", "是")
            config_settings.set("修改文件夹", "新文件夹的格式", "【+全部女优+】+车牌")
            config_settings.add_section("归类影片")
            config_settings.set("归类影片", "是否归类影片？", "否")
            config_settings.set("归类影片", "归类的根目录", "所选文件夹")
            config_settings.set("归类影片", "归类的标准", "首个女优\\发行年份+月")
            config_settings.add_section("获取两张jpg")
            config_settings.set("获取两张jpg", "是否获取fanart.jpg和poster.jpg？", "是")
            config_settings.set("获取两张jpg", "是否采取群辉video station命名方式？", "否")
            config_settings.set("获取样品图", "是否获取样品图", "是")
            config_settings.set("获取样品图", "样品图命名前缀格式", "sample+数字")
            config_settings.add_section("kodi专用")
            config_settings.set("kodi专用", "是否收集女优头像", "否")
            config_settings.add_section("emby服务端")
            config_settings.set("emby服务端", "网址", "http://localhost:8096/")
            config_settings.set("emby服务端", "API ID", "12345678")
            config_settings.add_section("其他设置")
            config_settings.set("其他设置", "简繁中文？", "简")
            config_settings.set("其他设置", "javlibrary网址", "http://www.x39n.com/")
            config_settings.set("其他设置", "javbus网址", "https://www.buscdn.work/")
            config_settings.set("其他设置", "素人车牌(若有新车牌请自行添加)",
                                "MIUM、NTK、ARA、GANA、LUXU、DCV、MAAN、HOI、NAMA、SWEET、SIRO、SCUTE、CUTE、SQB")
            config_settings.set("其他设置", "扫描文件类型", "mp4、mkv、avi、wmv、iso、rmvb、MP4")
            config_settings.add_section("百度翻译API")
            config_settings.set("百度翻译API", "是否需要日语简介？", "是")
            config_settings.set("百度翻译API", "是否翻译为中文？", "否")
            config_settings.set("百度翻译API", "APP ID", "")
            config_settings.set("百度翻译API", "密钥", "")
            config_settings.add_section("百度人体检测")
            config_settings.set("百度人体检测", "是否需要准确定位人脸的poster？", "否")
            config_settings.set("百度人体检测", "AppID", "")
            config_settings.set("百度人体检测", "API Key", "")
            config_settings.set("百度人体检测", "Secret Key", "")
            config_settings.write(open('config.ini', "w", encoding='utf-8'))
            print('写入“config.ini”文件成功，如果需要修改重命名格式请重新打开ini修改，然后重新启动程序！')
            os.system('pause')
        except:
            print(traceback.format_exc())
            print('\n这个ini文件无法读写，删除它，然后打开exe自动重新创建ini！')
            os.system('pause')

    if if_sculpture == '是':
        if not os.path.exists('女优头像'):
            print('\n“女优头像”文件夹丢失！请把它放进exe的文件夹中！\n')
            os.system('pause')
        if not os.path.exists('【缺失的女优头像统计For Kodi】.ini'):
            config_actor = configparser.ConfigParser()
            config_actor.add_section("缺失的女优头像")
            config_actor.set("缺失的女优头像", "女优姓名", "N(次数)")
            config_actor.add_section("说明")
            config_actor.set("说明", "上面的“女优姓名 = N(次数)”的表达式",
                             "后面的N数字表示你有N部(次)影片都在找她的头像，可惜找不到")
            config_actor.set("说明", "你可以去保存一下她的头像jpg到“女优头像”文件夹",
                             "以后就能保存她的头像到影片的文件夹了")
            config_actor.write(open('【缺失的女优头像统计For Kodi】.ini', "w", encoding='utf-8'))
            print('\n    >“【缺失的女优头像统计For Kodi】.ini”文件丢失...正在重写ini...成功！')
            print('正在重新读取...', end='')
    print('\n读取ini文件成功!')

    if if_plot == '是':
        print('正在尝试通过arzon的成人验证...')
        try:
            acook = get_acook()
            print('通过arzon的成人验证！\n')
        except:
            print('连接arzon失败，请避开网络高峰期！请重启程序！\n')
            os.system('pause')

    if simp_trad == '简':
        library_url += 'cn/'
        t_lang = 'zh'
    else:
        library_url += 'tw/'
        t_lang = 'cht'

    nfo_dict = {'空格': ' ', '车牌': 'ABC-123', '标题': '新时代新中国特色社会主义', '导演': '未知导演',
                '发行年月日': '1970-01-01', '发行年份': '1970', '月': '01', '日': '01',
                '片商': '未知片商', '评分': '0', '首个女优': '未知演员', '全部女优': ['未知演员'],
                '片长': '0'}  # 用于暂时存放影片信息，女优，标题等
    suren_list = suren_pref.split('、')  # 素人番号的列表，来自ini文件的suren_pref
    rename_mp4_list = rename_mp4.split('+')  # 重命名视频的格式，来自ini文件的rename_mp4
    rename_folder_list = rename_folder.split('+')  # 重命名文件夹的格式，来自ini文件的rename_folder
    type_tuple = tuple(file_type.split('、'))  # 视频文件的类型，来自ini文件的file_type
    classify_basis_list = classify_basis.split('\\')  # 归类标准，来自ini文件的classify_basis

    start_key = ''
    while start_key == '':
        # 用户选择文件夹
        print('请选择要整理的文件夹：', end='')
        path = utils.get_directory()
        print(path)
        write_fail('已选择文件夹：' + path + '\n')
        print('...文件扫描开始...如果时间过长...请避开中午夜晚高峰期...\n')
        # 确定归类根目录
        if if_classify == '是':
            classify_root = classify_root.rstrip('\\')
            if classify_root != '所选文件夹':
                if classify_root != path:  # 归类根目录和所选不一样，继续核实归类根目录的合法性
                    if classify_root[:2] != path[:2]:
                        print('归类的根目录“', classify_root, '”和所选文件夹不在同一磁盘无法归类！请修正！')
                        os.system('pause')
                    if not os.path.exists(classify_root):
                        print('归类的根目录“', classify_root, '”不存在！无法归类！请修正！')
                        os.system('pause')
                else:  # 一样
                    classify_root = path + '\\归类完成'
            else:
                classify_root = path + '\\归类完成'
        # 初始化
        fail_times = 0  # 处理过程中失败的个数
        fail_list = []  # 用于存放处理失败的信息
        # root【当前根目录】 dirs【子目录】 files【文件】，root是字符串，后两个是列表
        for root, dirs, files in os.walk(path):
            if if_classify == '是' and root.startswith(classify_root):  # “当前目录”在“目标归类目录”中
                # print('>>该文件夹在归类的根目录中，跳过处理...', root)
                continue
            if if_exnfo == '是' and files and (
                    files[-1].endswith('nfo') or (len(files) > 1 and files[-2].endswith('nfo'))):
                continue
            # 对这一层文件夹进行评估,有多少视频，有多少同车牌视频，是不是独立文件夹
            car_videos = []  # 存放：需要整理的jav的结构体
            cars_dic = {}  # 存放：这一层目录下的几个车牌
            videos_num = 0  # 当前文件夹中视频的数量，可能有视频不是jav
            subtitles = False  # 有没有字幕
            for raw_file in files:
                # 判断文件是不是字幕文件
                if raw_file.endswith(('.srt', '.vtt', '.ass',)):
                    subtitles = True
                    continue
                # 判断是不是视频，得到车牌号
                if raw_file.endswith(type_tuple) and not raw_file.startswith('.'):
                    videos_num += 1
                    # 排除视频文件包含hhd800.com@IPZZ-079.mp4 这种格式
                    trim_prefix = "hhd800.com@"
                    has_trim_prefix = False
                    if trim_prefix in raw_file:
                        has_trim_prefix = True
                        raw_file = raw_file.replace(trim_prefix, "")
                    # video_num_g = re.search(r'([a-zA-Z]{2,6})-? ?(\d{2,5})', raw_file)  # 这个正则表达式匹配“车牌号”可能有点奇怪，
                    video_num_g = re.search(r'([a-zA-Z]{1,6})-? ?(\d{2,5})', raw_file)  # 这个正则表达式匹配“车牌号”可能有点奇怪，

                    if str(video_num_g) != 'None':  # 如果你下过上千部片，各种参差不齐的命名，你就会理解我了。
                        num_pref = video_num_g.group(1).upper()
                        num_suf = video_num_g.group(2)
                        car_num = num_pref + '-' + num_suf
                        if num_pref in suren_list:  # 如果这是素人影片，告诉一下用户，它们需要另外处理
                            fail_times += 1
                            fail_message = '第' + str(fail_times) + '个警告！素人影片：\\' + root.lstrip(
                                path) + '\\' + raw_file + '\n'
                            print('>>' + fail_message, end='')
                            fail_list.append('    >' + fail_message)
                            write_fail('    >' + fail_message)
                            continue  # 素人影片不参与下面的整理
                        video_type = '.' + str(raw_file.split('.')[-1])  # 文件类型，如：.mp4
                        if car_num not in cars_dic:  # cars_dic中没有这个车牌，表示这一层文件夹下新发现一个车牌
                            cars_dic[car_num] = 1  # 这个新车牌有了第一集cd1
                        else:
                            cars_dic[car_num] += 1  # 已经有这个车牌了，加一集cd
                        jav_file = JavFile()
                        if has_trim_prefix:
                            jav_file.trim_prefix = trim_prefix
                        jav_file.car = car_num  # 车牌
                        jav_file.name = raw_file  # 原文件名
                        jav_file.episodes = cars_dic[car_num]  # 这个jav视频，是第几集
                        car_videos.append(jav_file)  # 放到car_videos中
                    else:
                        continue
                else:
                    continue
            if cars_dic:  # 这一层文件夹下有jav
                if len(cars_dic) > 1 or videos_num > len(car_videos) or len(dirs) > 1 or (
                        len(dirs) == 1 and dirs[0] != '.actors'):
                    # 当前文件夹下，车牌不止一个，还有其他非jav视频，            有其他文件夹，除了女优头像文件夹“.actors”
                    separate_folder = False  # 不是独立的文件夹
                else:
                    separate_folder = True  # 这一层文件夹是这部jav的独立文件夹
            else:
                continue

            # 正式开始
            # print(car_videos)
            for srt in car_videos:
                try:
                    car_num = srt.car
                    file = srt.name
                    relative_path = '\\' + root.lstrip(path) + '\\' + file  # 影片的相对于所选文件夹的路径，用于报错
                    # 获取nfo信息的javlibrary搜索网页
                    #  该死的javlibrary 开了cf 5秒盾  只能去找源站ip地址了，设置ssl证书校验跳过
                    library_url = 'https://129.146.0.222/cn/'
                    search_url = library_url + 'vl_searchbyid.php?keyword=' + car_num
                    try:
                        jav_rqs = requests.get(search_url, timeout=10, verify=False)
                        jav_rqs.encoding = 'utf-8'
                        jav_html = jav_rqs.text
                    except:
                        try:  # 用网高峰期，经常打不开javlibrary，尝试第二次
                            print('>>尝试打开javlibrary搜索页面失败，正在尝试第二次打开...')
                            jav_rqs = requests.get(search_url, timeout=10, verify=False)
                            jav_rqs.encoding = 'utf-8'
                            jav_html = jav_rqs.text
                            print('    >第二次尝试成功！')
                        except Exception as e:
                            print(f'Error while fetching javlibrary: {e}')
                            fail_times += 1
                            fail_message = '第' + str(
                                fail_times) + '个失败！打开javlibrary搜索页面失败：' + search_url + '，' + relative_path + '\n'
                            print('>>' + fail_message, end='')
                            fail_list.append('    >' + fail_message)
                            write_fail('    >' + fail_message)
                            continue
                    # 搜索结果的网页，大部分情况就是这个影片的网页，也有可能是多个结果的网页
                    # 尝试找标题，第一种情况：找得到，就是这个影片的网页
                    titleg = re.search(r'<title>([a-zA-Z]{1,6}-\d{1,5}.+?) - JAVLibrary</title>', jav_html)  # 匹配处理“标题”
                    # 搜索结果就是AV的页面
                    if str(titleg) != 'None':
                        title = titleg.group(1)
                    # 第二种情况：搜索结果可能是两个以上，所以这种匹配找不到标题，None！
                    else:  # 继续找标题，但匹配形式不同，这是找“可能是多个结果的网页”上的第一个标题
                        javtype = "javme"
                        pattern = re.compile(r'v=javme(.+?)" title="(.+?-\d+?)[a-z]? ')
                        all_matchs = pattern.findall(jav_html)
                        search_result = None
                        if all_matchs:
                            for item in all_matchs:
                                if item[1].strip() == car_num:
                                    search_result = item
                                    break

                        if search_result is None:
                            javtype = "javli"
                            pattern = re.compile(r'v=javli(.+?)" title="(.+?-\d+?)[a-z]? ')
                            all_matchs = pattern.findall(jav_html)
                            if all_matchs:
                                for item in all_matchs:
                                    if item[1].strip() == car_num:
                                        search_result = item
                                        break

                        # 搜索有几个结果，用第一个AV的网页，打开它
                        if str(search_result) != 'None':
                            first_url = library_url + f'?v={javtype}' + search_result[0]
                            try:
                                jav_rqs = requests.get(first_url, timeout=10,verify=False)
                                jav_rqs.encoding = 'utf-8'
                                jav_html = jav_rqs.text
                            except:
                                fail_times += 1
                                fail_message = '>第' + str(
                                    fail_times) + '个失败！打开javlibrary搜索页面上的第一个AV失败：' + first_url + '，' + relative_path + '\n'
                                print('>>' + fail_message, end='')
                                fail_list.append('    >' + fail_message)
                                write_fail('    >' + fail_message)
                                continue
                            # 找到标题，留着马上整理信息用
                            title = re.search(r'<title>([a-zA-Z]{1,6}-\d{1,5}.+?) - JAVLibrary</title>',
                                              jav_html).group(1)
                        # 第三种情况：搜索不到这部影片，搜索结果页面什么都没有
                        else:
                            # TODO 这里尝试使用javbus查找
                            fail_times += 1
                            fail_message = '第' + str(
                                fail_times) + '个失败！找不到AV信息，无码？新系列素人？年代久远？：' + search_url + '，' + relative_path + '\n'
                            print('>>' + fail_message, end='')
                            fail_list.append('    >' + fail_message)
                            write_fail('>>' + fail_message)
                            continue

                    # 去除title中的特殊字符
                    title = title.replace('\n', '').replace('&', '和').replace('\\', '#').replace('/', '#') \
                        .replace(':', '：').replace('*', '#').replace('?', '？').replace('"', '#').replace('<', '【') \
                        .replace('>', '】').replace('|', '#').replace('＜', '【').replace('＞', '】')
                    # remove some dirty e in title
                    title_list = title.split(" ")
                    code = title_list[0]
                    if code[-1] == 'e':
                        code = code[:-1]
                    title_list[0] = code
                    title = " ".join(title_list)
                    print('>>正在处理：', title)
                    # 处理影片的标题过长
                    if len(title) > 50:
                        title_easy = title[:50]
                    else:
                        title_easy = title
                    # 正则匹配 影片信息 开始！
                    # title的开头是车牌号，而我想要后面的纯标题
                    car_titleg = re.search(r'(.+?) (.+)', title_easy)  # 这边匹配番号，[a-z]可能很奇怪，
                    # 给用户用的标题是 短的title_easy
                    nfo_dict['标题'] = car_titleg.group(2)
                    # 车牌号
                    nfo_dict['车牌'] = car_titleg.group(1)
                    # 片商
                    studiog = re.search(r'rel="tag">(.+?)</a> &nbsp;<span id="maker_', jav_html)
                    if str(studiog) != 'None':
                        nfo_dict['片商'] = studiog.group(1)
                    else:
                        nfo_dict['片商'] = '未知片商'
                    # 上映日
                    premieredg = re.search(r'<td class="text">(\d\d\d\d-\d\d-\d\d)</td>', jav_html)
                    if str(premieredg) != 'None':
                        nfo_dict['发行年月日'] = premieredg.group(1)
                        nfo_dict['发行年份'] = nfo_dict['发行年月日'][0:4]
                        nfo_dict['月'] = nfo_dict['发行年月日'][5:7]
                        nfo_dict['日'] = nfo_dict['发行年月日'][8:10]
                    else:
                        nfo_dict['发行年月日'] = '1970-01-01'
                        nfo_dict['发行年份'] = '1970'
                        nfo_dict['月'] = '01'
                        nfo_dict['日'] = '01'
                    # 片长 <td><span class="text">150</span> 分钟</td>
                    runtimeg = re.search(r'<td><span class="text">(\d+?)</span>', jav_html)
                    if str(runtimeg) != 'None':
                        nfo_dict['片长'] = runtimeg.group(1)
                    else:
                        nfo_dict['片长'] = '0'
                    # 导演
                    directorg = re.search(r'rel="tag">(.+?)</a> &nbsp;<span id="director', jav_html)
                    if str(directorg) != 'None':
                        nfo_dict['导演'] = directorg.group(1)
                    else:
                        nfo_dict['导演'] = '未知导演'
                    # 演员们 和 # 第一个演员
                    actors_prag = re.search(r'<span id="cast(.+?)</td>', jav_html, re.DOTALL)
                    if str(actors_prag) != 'None':
                        actors = re.findall(r'rel="tag">(.+?)</a></span> <span id', actors_prag.group(1))
                        if len(actors) != 0:
                            nfo_dict['首个女优'] = actors[0]
                            nfo_dict['全部女优'] = actors
                        else:
                            nfo_dict['全部女优'] = ['未知演员']
                            nfo_dict['首个女优'] = '未知演员'
                    else:
                        nfo_dict['全部女优'] = ['未知演员']
                        nfo_dict['首个女优'] = '未知演员'
                    nfo_dict['标题'] = nfo_dict['标题'].rstrip(nfo_dict['首个女优'])
                    # 特点
                    genres = re.findall(r'category tag">(.+?)</a></span><span id="genre', jav_html)
                    if len(genres) == 0:
                        genres = ['无特点']
                    if '-c.' in file or '-C.' in file or subtitles:
                        genres.append('中文字幕')
                    # DVD封面cover
                    coverg = re.search(r'src="(.+?)" width="600" height="403"', jav_html)  # 封面图片的正则对象
                    if str(coverg) != 'None':
                        cover = coverg.group(1)
                    else:
                        cover = ''
                    # 评分
                    scoreg = re.search(r'&nbsp;<span class="score">\((.+?)\)</span>', jav_html)
                    if str(scoreg) != 'None':
                        score = float(scoreg.group(1))
                        score = (score - 4) * 5 / 3  # javlibrary上稍微有人关注的影片评分都是6分以上（10分制），强行把它差距拉大
                        if score >= 0:
                            score = '%.1f' % score
                            nfo_dict['评分'] = str(score)
                        else:
                            nfo_dict['评分'] = '0'
                    else:
                        nfo_dict['评分'] = '0'
                    # javlibrary的精彩影评   (.+?\s*.*?\s*.*?\s*.*?)  不用影片简介，用javlibrary上的精彩影片，下面的匹配可能很奇怪，没办法，就这么奇怪
                    plot_review = ''
                    if if_review == '是':
                        review = re.findall(
                            r'(hidden">.+?</textarea>)</td>\s*?<td class="scores"><table>\s*?<tr><td><span class="scoreup">\d\d+?</span>',
                            jav_html, re.DOTALL)
                        if len(review) != 0:
                            plot_review = '\n【精彩影评】：'
                            for rev in review:
                                right_review = re.findall(r'hidden">(.+?)</textarea>', rev, re.DOTALL)
                                if len(right_review) != 0:
                                    plot_review = plot_review + right_review[-1].replace('&', '和') + '////'
                                    continue
                    # arzon的简介 #########################################################
                    plot = ''
                    if if_nfo == '是' and if_plot == '是':
                        while True:
                            arzon_url = 'https://www.arzon.jp/itemlist.html?t=&m=all&s=&q=' + nfo_dict['车牌']
                            print('    >正在查找简介：', arzon_url)
                            try:
                                az_rqs = requests.get(arzon_url, cookies=acook, timeout=10)
                                az_rqs.encoding = 'utf-8'
                                search_html = az_rqs.text
                            except:
                                try:
                                    print('    >尝试打开“', arzon_url, '”搜索页面失败，正在尝试第二次打开...')
                                    az_rqs = requests.get(arzon_url, cookies=acook, timeout=10)
                                    az_rqs.encoding = 'utf-8'
                                    search_html = az_rqs.text
                                    print('    >第二次尝试成功！')
                                except:
                                    fail_times += 1
                                    fail_message = '    >第' + str(
                                        fail_times) + '个失败！连接arzon失败：' + arzon_url + '，' + relative_path + '\n'
                                    print(fail_message, end='')
                                    fail_list.append(fail_message)
                                    write_fail(fail_message)
                                    plot = '【连接arzon失败！看到此提示请重新整理nfo！】'
                                    break
                            # arzon第一次搜索AV  <dt><a href="https://www.arzon.jp/item_1376110.html" title="限界集落に越してきた人妻 ～村民達の慰みモノにされる日々～"><img src=
                            AVs = re.findall(r'<h2><a href="(/item.+?)" title=', search_html)
                            # 可能是几个AV的界面
                            if len(AVs) != 0:
                                # 第一个AV网页
                                if_item_html = re.match(r'/item.+?', AVs[0])
                                # 是/item_1441697.html
                                if if_item_html:
                                    av_url = 'https://www.arzon.jp' + AVs[0]
                                    #################################################################################
                                    try:
                                        rqs = requests.get(av_url, cookies=acook, timeout=10)
                                        rqs.encoding = 'utf-8'
                                        first_html = rqs.text
                                    except:
                                        try:
                                            print('    >尝试打开“', av_url, '”第一个AV页面失败，正在尝试第二次打开...')
                                            rqs = requests.get(av_url, cookies=acook, timeout=10)
                                            rqs.encoding = 'utf-8'
                                            first_html = rqs.text
                                            print('    >第二次尝试成功！')
                                        except:
                                            fail_times += 1
                                            fail_message = '    >第' + str(
                                                fail_times) + '个失败！无法进入第一个搜索结果：' + av_url + '，' + relative_path + '\n'
                                            print(fail_message, end='')
                                            fail_list.append(fail_message)
                                            write_fail(fail_message)
                                            plot = '【连接arzon失败！看到此提示请重新整理nfo！】'
                                            break
                                    ############################################################################
                                    plotg = re.search(r'<h2>作品紹介</h2>([\s\S]*?)</div>', first_html)
                                    # 第一个页面找到plot
                                    if str(plotg) != 'None':
                                        plot_br = plotg.group(1)
                                        plot = ''
                                        for line in plot_br.split('<br />'):
                                            line = line.strip().replace('＆', 'そして')
                                            plot += line
                                        plot = '【影片简介】：' + plot
                                        break
                                    else:  # 第一个页面可能找不到，把第二个页面当做av_url
                                        # 可能不存在第二个页面
                                        if_item_url = re.match(r'/item.+?', AVs[1])
                                        # 是不是/item_1441697.html
                                        if if_item_url:
                                            av_url = 'https://www.arzon.jp' + AVs[1]
                                            #######################################################################
                                            try:
                                                rqs = requests.get(av_url, cookies=acook, timeout=10)
                                                rqs.encoding = 'utf-8'
                                                second_html = rqs.text
                                            except:
                                                try:
                                                    print('    >尝试打开“', av_url,
                                                          ' ”第二个页面失败，正在尝试第二次打开...\n')
                                                    rqs = requests.get(av_url, cookies=acook, timeout=10)
                                                    rqs.encoding = 'utf-8'
                                                    second_html = rqs.text
                                                    print('    >第二次尝试成功！')
                                                except:
                                                    fail_times += 1
                                                    fail_message = '    >第' + str(
                                                        fail_times) + '个失败！无法进入第二个搜索结果：' + av_url + '，' + relative_path + '\n'
                                                    print(fail_message, end='')
                                                    fail_list.append(fail_message)
                                                    write_fail(fail_message)
                                                    plot = '【连接arzon失败！看到此提示请重新整理nfo！】'
                                                    break
                                            ############################################################################
                                            plotg = re.search(r'<h2>作品紹介</h2>\s+?(.+?)\s*<', second_html)
                                            # 第二个页面找到plot
                                            if str(plotg) != 'None':
                                                plot_br = plotg.group(1)
                                                plot = ''
                                                for line in plot_br.split('<br />'):
                                                    line = line.strip().replace('＆', 'そして')
                                                    plot += line
                                                plot = '【影片简介】：' + plot
                                                break
                                            else:  # 第二个页面可能找不到，把第三个页面当做av_url
                                                # 可能不存在第三个页面
                                                if_item_url = re.match(r'/item.+?', AVs[2])
                                                # 是不是/item_1441697.html
                                                if if_item_url:
                                                    av_url = 'https://www.arzon.jp' + AVs[2]
                                                    ############################################################################
                                                    try:
                                                        rqs = requests.get(av_url, cookies=acook, timeout=10)
                                                        rqs.encoding = 'utf-8'
                                                        third_html = rqs.text
                                                    except:
                                                        try:
                                                            print('    >尝试打开“', av_url,
                                                                  '”第三个页面失败，正在尝试第二次打开...\n')
                                                            rqs = requests.get(av_url, cookies=acook, timeout=10)
                                                            rqs.encoding = 'utf-8'
                                                            third_html = rqs.text
                                                            print('    >第二次尝试成功！')
                                                        except:
                                                            fail_times += 1
                                                            fail_message = '    >第' + str(
                                                                fail_times) + '个失败！无法进入第三个搜索结果：' + av_url + '，' + relative_path + '\n'
                                                            print(fail_message, end='')
                                                            fail_list.append(fail_message)
                                                            write_fail(fail_message)
                                                            plot = '【连接arzon失败！看到此提示请重新整理nfo！】'
                                                            break
                                                    ############################################################################
                                                    plotg = re.search(r'<h2>作品紹介</h2>\s+?(.+?)\s*<', third_html)
                                                    # 第三个页面找到plot
                                                    if str(plotg) != 'None':
                                                        plot_br = plotg.group(1)
                                                        plot = ''
                                                        for line in plot_br.split('<br />'):
                                                            line = line.strip().replace('＆', 'そして')
                                                            plot += line
                                                        plot = '【影片简介】：' + plot
                                                        break
                                                    else:  # 第三个搜索界面也找不到
                                                        fail_times += 1
                                                        fail_message = '    >第' + str(
                                                            fail_times) + '个失败！有三个搜索结果：' + arzon_url + '，但找不到简介：' + relative_path + '\n'
                                                        print(fail_message, end='')
                                                        fail_list.append(fail_message)
                                                        write_fail(fail_message)
                                                        plot = '【查无简介】'
                                                        break
                                                # 第三个页面不是/item_1441697.html
                                                else:
                                                    fail_times += 1
                                                    fail_message = '    >第' + str(
                                                        fail_times) + '个失败！有两个搜索结果：' + arzon_url + '，但找不到简介：' + relative_path + '\n'
                                                    print(fail_message, end='')
                                                    fail_list.append(fail_message)
                                                    write_fail(fail_message)
                                                    plot = '【查无简介】'
                                                    break
                                        else:
                                            # 第二个页面不是/item_1441697.html
                                            fail_times += 1
                                            fail_message = '    >第' + str(
                                                fail_times) + '个失败！有一个搜索结果：' + arzon_url + '，但找不到简介：' + relative_path + '\n'
                                            print(fail_message, end='')
                                            fail_list.append(fail_message)
                                            write_fail(fail_message)
                                            plot = '【查无简介】'
                                            break
                                # 第一个页面就不是/item_1441697.html，arzon搜索不到
                                else:
                                    fail_times += 1
                                    fail_message = '    >第' + str(
                                        fail_times) + '个失败！arzon找不到该影片信息：' + arzon_url + '，可能被下架：' + relative_path + '\n'
                                    print(fail_message, end='')
                                    fail_list.append(fail_message)
                                    write_fail(fail_message)
                                    plot = '【影片下架，再无简介】'
                                    break
                            # arzon搜索页面实际是18岁验证
                            else:
                                adultg = re.search(r'１８歳未満', search_html)
                                if str(adultg) != 'None':
                                    fail_times += 1
                                    fail_message = '    >第' + str(
                                        fail_times) + '个失败！成人验证，请重启程序：' + relative_path + '\n'
                                    print(fail_message, end='')
                                    fail_list.append(fail_message)
                                    write_fail(fail_message)
                                    plot = '【连接arzon失败！看到此提示请重新整理nfo！】'
                                    os.system('pause')
                                else:  # 不是成人验证，也没有结果
                                    fail_times += 1
                                    fail_message = '    >第' + str(
                                        fail_times) + '个失败！arzon找不到该影片信息，可能被下架：' + arzon_url + '，' + relative_path + '\n'
                                    print(fail_message, end='')
                                    fail_list.append(fail_message)
                                    write_fail(fail_message)
                                    plot = '【影片下架，再无简介】'
                                    break
                        if if_tran == '是':
                            plot = tran(ID, SK, plot, t_lang)
                    #######################################################################

                    # 1重命名视频
                    new_mp4 = file.rstrip(video_type).rstrip(' ')
                    if if_mp4 == '是':  # 新文件名
                        new_mp4 = ''
                        for j in rename_mp4_list:
                            if j not in nfo_dict:
                                new_mp4 = new_mp4 + j
                            elif j != '全部女优':
                                new_mp4 = new_mp4 + nfo_dict[j]
                            else:
                                new_mp4 = new_mp4 + ' '.join(nfo_dict[j])
                        new_mp4 = new_mp4.rstrip(' ')  # 去除末尾空格，否则windows会自动删除空格，导致程序仍以为带空格
                        cd_msg = ''
                        if cars_dic[car_num] > 1:  # 是CD1还是CDn？
                            cd_msg = '-cd' + str(srt.episodes)
                            new_mp4 += cd_msg
                        # rename mp4
                        if srt.trim_prefix != "":
                            file = trim_prefix + file
                        os.rename(root + '\\' + file, root + '\\' + new_mp4 + video_type)
                        # file发生了变化
                        file = new_mp4 + video_type
                        print('    >修改文件名' + cd_msg + '完成')

                    # 2重命名文件夹
                    new_root = root  # 当前影片的新目录路径
                    new_folder = root.split('\\')[-1]  # 当前影片的新目录名称
                    if if_folder == '是':
                        # 新文件夹名new_folder
                        temp_folder = new_folder
                        new_folder = ''
                        for j in rename_folder_list:
                            if j not in nfo_dict:
                                new_folder = new_folder + j
                            elif j != '全部女优':
                                new_folder = new_folder + nfo_dict[j]
                            else:
                                new_folder = new_folder + ' '.join(nfo_dict[j])
                        new_folder = new_folder.rstrip(' ')  # 去除末尾空格，否则windows会自动删除空格，导致程序仍以为带空格
                        # 最多保留10个演员
                        new_folder = short_long_folder_name(new_folder)
                        # 如果是有字幕的 文件夹保留-C标记
                        if "-4k" in temp_folder or "-4K" in temp_folder:
                            new_folder = new_folder + " 4k"
                        if "-c" in temp_folder or "-C" in temp_folder:
                            new_folder = new_folder + " C"
                        if separate_folder:  # 是独立文件夹，才会重命名文件夹
                            if cars_dic[car_num] == 1 or (cars_dic[car_num] > 1 and cars_dic[car_num] == srt.episodes):
                                # 同一车牌有多部，且这是最后一部，才会重命名
                                newroot_list = root.split('\\')
                                del newroot_list[-1]
                                upper2_root = '\\'.join(newroot_list)  # 当前文件夹的上级目录
                                new_root = upper2_root + '\\' + new_folder  # 上级目录+新目录名称=新目录路径
                                if not os.path.exists(new_root):  # 目标影片文件夹不存在，
                                    # 修改文件夹
                                    os.rename(root, new_root)
                                elif new_root == root:  # 目标影片文件夹存在，但就是现在的文件夹，即新旧相同
                                    os.rename(root, new_root)
                                else:  # 已经有一个那样的文件夹了
                                    # 默认增加一个 D来区分 标记为duplicate
                                    os.rename(root, new_root + " D")
                                    print("f已发现番号视频目录已存在,已做D标记处理")
                                    fail_times += 1
                                    fail_message = '    >第' + str(
                                        fail_times) + '个失败！重命名文件夹失败，重复的影片，已存在相同文件夹：' + relative_path + file + '\n'
                                    print(fail_message, end='')
                                    fail_list.append(fail_message)
                                    write_fail(fail_message)
                                    continue
                        else:  # 不是独立，还有其他影片
                            if not os.path.exists(root + '\\' + new_folder):  # 准备建个新的文件夹，确认没有同名文件夹
                                os.makedirs(root + '\\' + new_folder)
                            # 放进独立文件夹
                            os.rename(root + '\\' + file, root + '\\' + new_folder + '\\' + file)  # 就把影片放进去
                            new_root = root + '\\' + new_folder  # # 当前非独立的目录+新目录名称=新独立的文件夹
                            print('    >创建独立的文件夹完成')
                        # 移除所有不相关的文件只保留视频文件和torrent文件
                        clean_video_folder(new_root, type_tuple)
                    # 更新一下relative_path
                    relative_path = '，\\' + new_root.lstrip(path) + '\\' + file  # 影片的相对于所选文件夹的路径，用于报错
                    # 3写入nfo开始
                    if if_nfo == '是':
                        # 开始写入nfo，这nfo格式是参考的kodi的nfo
                        info_path = new_root + '\\' + new_mp4 + '.nfo'  # nfo存放的地址
                        # print(new_root)
                        f = open(info_path, 'w', encoding="utf-8")
                        f.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\" ?>\n"
                                "<movie>\n"
                                "  <plot>" + plot + plot_review + "</plot>\n"
                                                                  "  <title>" + title + "</title>\n"
                                                                                        "  <director>" + nfo_dict[
                                    '导演'] + "</director>\n"
                                              "  <rating>" + nfo_dict['评分'] + "</rating>\n"
                                                                                "  <year>" + nfo_dict[
                                    '发行年份'] + "</year>\n"
                                                  "  <mpaa>NC-17</mpaa>\n"
                                                  "  <customrating>NC-17</customrating>\n"
                                                  "  <countrycode>JP</countrycode>\n"
                                                  "  <premiered>" + nfo_dict['发行年月日'] + "</premiered>\n"
                                                                                             "  <release>" + nfo_dict[
                                    '发行年月日'] + "</release>\n"
                                                    "  <runtime>" + nfo_dict['片长'] + "</runtime>\n"
                                                                                       "  <country>日本</country>\n"
                                                                                       "  <studio>" + nfo_dict[
                                    '片商'] + "</studio>\n"
                                              "  <id>" + nfo_dict['车牌'] + "</id>\n"
                                                                            "  <num>" + nfo_dict['车牌'] + "</num>\n")
                        for i in genres:
                            f.write("  <genre>" + i + "</genre>\n")
                        for i in genres:
                            f.write("  <tag>" + i + "</tag>\n")
                        for i in nfo_dict['全部女优']:
                            f.write("  <actor>\n    <name>" + i + "</name>\n    <type>Actor</type>\n  </actor>\n")
                        f.write("</movie>\n")
                        f.close()
                        print('    >nfo收集完成')

                    # 4需要两张图片
                    if if_jpg == '是':
                        # 下载海报的地址 cover
                        if "https://" not in cover:
                            cover_url = 'https://' + cover
                        # fanart和poster路径
                        if if_qunhui != '是':
                            fanart_path = new_root + '\\' + new_mp4 + '-fanart.jpg'
                            poster_path = new_root + '\\' + new_mp4 + '-poster.jpg'
                        else:
                            fanart_path = new_root + '\\' + new_mp4 + '.jpg'
                            poster_path = new_root + '\\' + new_mp4 + '.png'
                        # 下载 海报
                        try:
                            # print('    >正在下载封面：', cover_url)
                            # poster_header = {
                            #     "Referer": f"{bus_search_url}",
                            #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
                            # }
                            # r = requests.get(cover_url, stream=True, timeout=10, headers=headers)
                            # with open(fanart_path, 'wb') as f:
                            #     for chunk in r:
                            #         f.write(chunk)
                            # print('    >fanart.jpg下载成功')
                            raise RuntimeError("不使用javlibrary获取海报")
                        except:
                            print('    >从javlibrary下载fanart.jpg失败，正在前往javbus...')
                            # 在javbus上找图片url
                            bus_search_url = bus_url + nfo_dict['车牌']
                            try:
                                # 这里对于非美国的节点访问 需要使用cookie
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
                                bus_search_rqs = requests.get(bus_search_url, timeout=10, headers=headers)
                                bus_search_rqs.encoding = 'utf-8'
                                bav_html = bus_search_rqs.text
                            except:
                                fail_times += 1
                                fail_message = '    >第' + str(
                                    fail_times) + '个失败！连接javbus失败：' + bus_search_url + '，' + relative_path + '\n'
                                print(fail_message, end='')
                                fail_list.append(fail_message)
                                write_fail(fail_message)
                                continue
                            # DVD封面cover
                            coverg = re.search(r'<a class="bigImage" href="(.+?)">', bav_html)  # 封面图片的正则对象
                            if str(coverg) != 'None':
                                cover_url = bus_url + coverg.group(1)

                                print('    >正在从javbus下载封面：', cover_url)
                                try:
                                    r = requests.get(cover_url, stream=True, timeout=10, headers=headers)
                                    with open(fanart_path, 'wb') as f:
                                        for chunk in r:
                                            f.write(chunk)
                                    print('    >fanart.jpg下载成功')
                                except:
                                    fail_times += 1
                                    fail_message = '    >第' + str(
                                        fail_times) + '个失败！下载fanart.jpg失败：' + cover_url + '，' + relative_path + '\n'
                                    print(fail_message, end='')
                                    fail_list.append(fail_message)
                                    write_fail(fail_message)
                                    continue
                            else:
                                fail_times += 1
                                fail_message = '    >第' + str(
                                    fail_times) + '个失败！从javbus上查找封面失败：' + bus_search_url + '，' + relative_path + '\n'
                                print(fail_message, end='')
                                fail_list.append(fail_message)
                                write_fail(fail_message)
                                continue
                            # 获取sample images
                            if if_sample_images == '是':
                                sample_images = re.findall(r'<a class="sample-box" href="([^"]*)">', bav_html)
                                for s in sample_images:
                                    file_name = sample_images_format + "-" + os.path.basename(s)
                                    sample_path = new_root + "\\" + file_name
                                    try:
                                        sample_header = {
                                            "Referer": f"{bus_search_url}",
                                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
                                        }
                                        r = requests.get(s, stream=True, timeout=10, headers=sample_header)
                                        with open(sample_path, 'wb') as f:
                                            for chunk in r:
                                                f.write(chunk)
                                        print(f'    >样品图{file_name}下载成功')
                                    except:
                                        print(f"    >样品图: {file_name} 下载失败")
                                        byte_data = b'x41'
                                        with open(sample_path, 'wb') as f:
                                            f.write(byte_data)

                        # 裁剪生成 poster
                        img = Image.open(fanart_path)
                        w, h = img.size  # fanart的宽 高
                        ex = int(w * 0.52625)  # 0.52625是根据emby的poster宽高比较出来的
                        poster = img.crop((ex, 0, w, h))  # （ex，0）是左下角（x，y）坐标 （w, h)是右上角（x，y）坐标
                        poster.save(poster_path, quality=95)  # quality=95 是无损crop，如果不设置，默认75
                        print('    >poster.jpg裁剪成功')
                        if if_qunhui == '是':
                            shutil.copyfile(fanart_path, new_root + '\\Backdrop.jpg')

                    # 5收集女优头像
                    if if_sculpture == '是':
                        for each_actor in nfo_dict['全部女优']:
                            exist_actor_path = '女优头像\\' + each_actor + '.jpg'  # 事先准备好的女优头像路径
                            # print(exist_actor_path)
                            jpg_type = '.jpg'
                            if not os.path.exists(exist_actor_path):  # 女优图片还没有
                                exist_actor_path = '女优头像\\' + each_actor + '.png'
                                if not os.path.exists(exist_actor_path):  # 女优图片还没有
                                    fail_times += 1
                                    fail_message = '    >第' + str(
                                        fail_times) + '个失败！没有女优头像：' + each_actor + '，' + relative_path + '\n'
                                    print(fail_message, end='')
                                    fail_list.append(fail_message)
                                    write_fail(fail_message)
                                    config_actor = configparser.ConfigParser()
                                    config_actor.read('【缺失的女优头像统计For Kodi】.ini', encoding='utf-8')
                                    try:
                                        each_actor_times = config_actor.get('缺失的女优头像', each_actor)
                                        config_actor.set("缺失的女优头像", each_actor, str(int(each_actor_times) + 1))
                                    except:
                                        config_actor.set("缺失的女优头像", each_actor, '1')
                                    config_actor.write(
                                        open('【缺失的女优头像统计For Kodi】.ini', "w", encoding='utf-8'))
                                    continue
                                else:
                                    jpg_type = '.png'
                            actors_path = new_root + '\\.actors\\'
                            if not os.path.exists(actors_path):
                                os.makedirs(actors_path)
                            shutil.copyfile('女优头像\\' + each_actor + jpg_type,
                                            actors_path + each_actor + jpg_type)  # 复制一封到“.actors”
                            print('    >女优头像收集完成：', each_actor)

                    # 6移动文件夹
                    if if_classify == '是' and (
                            cars_dic[car_num] == 1 or (cars_dic[car_num] > 1 and cars_dic[car_num] == srt.episodes)):
                        # 需要移动文件夹，且，是该影片的最后一集
                        if separate_folder and classify_root.startswith(root):
                            print('    >无法归类，请选择该文件夹的上级目录作它的归类根目录', root.lstrip(path))
                            continue
                        class_root = classify_root + '\\'
                        # 对归类标准再细化
                        for t in classify_basis_list:
                            new_t = ''
                            for j in t.split('+'):
                                if j not in nfo_dict:
                                    new_t = new_t + j
                                elif j != '全部女优':
                                    new_t = new_t + nfo_dict[j]
                                else:
                                    new_t = new_t + ' '.join(nfo_dict[j])
                            class_root += new_t + '\\'  # C:\\Users\\JuneRain\\Desktop\\测试文件夹\\1\\葵司\\
                        new_new_root = class_root + new_folder  # 移动的目标文件夹 C:\\Users\\JuneRain\\Desktop\\测试文件夹\\1\\葵司\\【葵司】AVOP-127
                        if not os.path.exists(new_new_root):  # 不存在目标目录
                            shutil.move(new_root, new_new_root)
                            print('    >归类文件夹完成')
                        else:
                            fail_times += 1
                            fail_message = '    >第' + str(
                                fail_times) + '个失败！归类失败，重复的影片，归类的根目录已存在相同文件夹：' + new_new_root + '\n'
                            print(fail_message, end='')
                            fail_list.append(fail_message)
                            write_fail(fail_message)
                            if not os.path.exists(path + '\\归类失败'):  # 还不存在失败文件夹，先创建一个
                                os.makedirs(path + '\\归类失败')
                            shutil.move(new_root, path + '\\归类失败\\' + new_root.split('\\')[-1])
                            continue

                except:
                    fail_times += 1
                    fail_message = '    >第' + str(
                        fail_times) + '个失败！发生错误，如一直在该影片报错请截图并联系作者：' + relative_path + '\n' \
                                   + traceback.format_exc() + '\n'
                    print(fail_message, end='')
                    fail_list.append(fail_message)
                    write_fail(fail_message)
                    continue
        # 完结撒花
        print('\n当前文件夹完成，', end='')
        if fail_times > 0:
            print('失败', fail_times, '个!  ', path, '\n')
            if len(fail_list) > 0:
                for fail in fail_list:
                    print(fail, end='')
            print('\n“【记得清理它】失败记录.txt”已记录错误\n')
        else:
            print('没有处理失败的AV，干得漂亮！  ', path, '\n')
        # os.system('pause')
        start_key = input('回车继续选择文件夹整理：')

# if __name__ == '__main__':
#     clean_video_folder("H:\非字幕\测试", ("mp4",))
