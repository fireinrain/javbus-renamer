import os
import re
import unittest


class TestAddFunction(unittest.TestCase):

    def test_process(folder_name: str) -> str:
        a = "【JULIA 鈴木さとみ Hitomi 松本菜奈実 桐谷まつり 八乃つばさ 美国沙耶 凛音とうか 須原のぞみ 葵百合香 大桃みすず 音羽美玲 あいだ飛鳥 百瀬とあ 永井れいな 篠崎かんな 高梨ゆあ 望月あやか 石原理央 古賀まつな 佐知子 柊るい 中野七緒 夏希まろん 目黒めぐみ 辻井ほのか ジューン・ラブジョイ 藤森里穂 叶ユリア 小峰ひなた 田中ねね 川村晴 椿りか 神坂朋子 姫咲はな 凪沙ゆきの 笹宮えれな 一色さゆり 朝日奈かれん 楪カレン 辻さくら 冨安れおな 綾瀬ことは 海埜ほたる】PPBD-229"

        star_names = a.replace("【", "").replace("】", " ")
        stars = star_names.split(" ")
        if len(stars) > 11:
            new_stars = stars[:10]
            new_stars[0] = "【" + new_stars[0]
            new_stars[9] = new_stars[9] + "】"
            new_stars.append(stars[-1])
            return " ".join(new_stars)

        return folder_name

    def test_reg(self):
        raw_file = 'ipx-005'
        video_num_g = re.search(r'([a-zA-Z]{1,6})-? ?(\d{2,5})', raw_file)
        print(video_num_g.group(1))
        print(video_num_g.group(2))
        print(video_num_g)


    def test_os_walk(self):
        for root, dirs, files in os.walk("H:\新建文件夹20230129"):
            print(root)
            print(dirs)
            print(files)
            print("--------------------------")


    def test_cf(self):
        import requests
        response = requests.get("https://129.146.0.222/cn/vl_searchbyid.php?keyword=IPX-061",verify=False)
        print(response.text)


    def test_rename_dir(self):
        import os
        import re

        def rename_folders(directory_path):
            # 获取目录下所有子目录
            subdirectories = [d for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))]

            for subdirectory in subdirectories:
                original_path = os.path.join(directory_path, subdirectory)

                # 使用正则表达式匹配日期格式，假设日期格式为X月X日
                match = re.search(r'(\d{1,2}月\d{1,2}日)', subdirectory)

                if match:
                    # 提取匹配到的日期
                    original_date = match.group(0)

                    # 将日期格式调整为XX月XX日
                    modified_date = original_date.zfill(4)  # 在单数字月份或日期前面补零
                    modified_path = os.path.join(directory_path, subdirectory.replace(original_date, modified_date))

                    # 重命名文件夹
                    os.rename(original_path, modified_path)
                    print(f'Renamed: {original_path} -> {modified_path}')


        # 指定要处理的目录路径
        target_directory = "C:/ceshi/riqi"

        # 调用函数进行重命名
        rename_folders(target_directory)


if __name__ == '__main__':
    unittest.main()
