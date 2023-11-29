# JAV-Scraper-and-Rename-local-files
收集jav元数据，并规范本地文件（夹）的格式，为emby、kodi、jellyfin收集女优头像。  
python3.7  使用pyinstaller打包成exe。



### 工作流程：  
1、用户选择文件夹，遍历路径下的所有文件。  
2、文件是jav，取车牌号，到javXXX网站搜索影片找到对应网页。  
3、获取网页源码找出“标题”“导演”“发行日期”等信息和DVD封面url。  
4、重命名影片文件。 
5、重命名文件夹或建立独立文件夹。
6、保存信息写入nfo。  
7、下载封面url作fanart.jpg，裁剪右半边作poster.jpg。  
8、移动文件夹，完成归类。  

### 效果展示：  
![image](images/1.png)  
![image](images/2.png)  
![image](images/3.jpg)  


### ini配置文件设置：  
  
[收集nfo]  
是否收集nfo？ = 是  
是否跳过已存在nfo的文件夹？ = 是  
是否收集javlibrary上的影评？ = 是  
  
[重命名影片]  
是否重命名影片？ = 是  
重命名影片的格式 = 车牌+空格+标题  
  
[修改文件夹]  
是否重命名或创建独立文件夹？ = 是  
新文件夹的格式 = 【+全部女优+】+车牌  

[归类影片]  
是否归类影片？ = 否  
归类的根目录 = 所选文件夹  
归类的标准 = 发行年份\首个女优  
  
[获取两张jpg]  
是否获取fanart.jpg和poster.jpg？ = 是  
是否采取群辉video station命名方式？ = 否  
  
[kodi专用]
是否收集女优头像 = 否  
  
[emby服务端]  
网址 = http://localhost:8096/  
api id = 12345678  

[其他设置]  
简繁中文？ = 简  
javlibrary网址 = http://www.x39n.com/  
javbus网址 = https://www.buscdn.work/  
素人车牌(若有新车牌请自行添加) = MIUM、NTK、ARA、GANA、LUXU、DCV、MAAN、HOI、NAMA、SWEET、SIRO、SCUTE、CUTE、SQB  
扫描文件类型 = mp4、mkv、avi、wmv、iso、rmvb、MP4、MKV、AVI、WMV、ISO、RMVB  

[百度翻译API]  
是否需要日语简介？ = 是  
是否翻译为中文？ = 否  
app id =   
密钥 =   
  
[百度人体检测]  
是否需要准确定位人脸的poster？ = 否  
appid =   
api key =   
secret key =  


  
