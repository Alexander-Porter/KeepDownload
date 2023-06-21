import re
import time
import requests
import logging
import webbrowser
import os
def get_biggest_file_url(urls):
  biggest_file_size = 0
  biggest_file_url = None

  for url in urls:
    response = requests.head(url)
    file_size = int(response.headers['Content-Length'])

    if file_size > biggest_file_size:
      biggest_file_size = file_size
      biggest_file_url = url

  return biggest_file_url
def extract_all_videos(t):
    t=str(t)
    pattren = re.compile(r'https://[^\s]+.mp4')
    url_lst = pattren.findall(t)
    return url_lst
def extract_url(t):
    t=str(t)
    pattren = re.compile(r'https://.*')
    url_lst = pattren.findall(t)
    return url_lst[0]
def download(videos):

    for i in videos:
        url=get_biggest_file_url(i["link"])
        os.system('curl -o "%s.mp4" %s'%(i["name"],url))
def getVideoFromId(courseId,token):
    h={
        "Authorization":"Bearer "+token
    }
    courseData=requests.get("http://api.gotokeep.com/course/v3/plans/%s?trainer_gender=M&betaType="%(courseId),headers=h).json()["data"]["workouts"]
    videos=[]
    for i in courseData:
        print("Now for" +i["name"])
        try:
            childData={
                "name":i["name"],
                "link":[i["multiVideo"]["totalVideoMap"]["super"]["url"]]
            }
        except :
            print(i["name"]+"暂无最高画质，启用候补.\n一般来说，文件名中有XXXP或者screenVideo字样的为全过程视频\n(TO DO：自动筛选画质，合并为新视频.)")
            childData={
                "name":i["name"],
                "link":extract_all_videos(courseData)
            }
        videos.append(childData)
    logging.debug(videos)
    return videos



def get_token():
    loginQrData=requests.get("http://api.gotokeep.com/account/v2/qrcode?authType=my").json()
    logging.info(loginQrData)
    webbrowser.open(loginQrData["data"]["qrcodeUrl"])
    while True:
        check=requests.get("http://api.gotokeep.com/account/v2/qrcode/login_check?qrcodeId="+loginQrData["data"]["qrcodeId"]).json()
        logging.info(check)
        if check["ok"]:
            return check["data"]["token"]
        else:
            time.sleep(3)

def save_token(token):
  """Saves the token to a file.

  Args:
    token: The token to save.
  """

  with open('token.txt', 'w') as f:
    f.write(token)


def check_token():
  try:
    with open('token.txt', 'r') as f:
      token = f.read()
  except FileNotFoundError:

    return True
  return False
def main():
  """Gets a new token if the old token has been duel.
  """

  if check_token():
    token = get_token()
    save_token(token)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
    format='%(message)s',
    datefmt='%Y-%m-%d %a %H:%M:%S',
    filename='History.txt')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    main()
    with open('token.txt', 'r') as f:
      token = f.read()
    print("Keep Downloader.")
    while True:
        logging.info("2)在此处按鼠标右键粘贴Keep App分享课程得到的链接，之后按回车.按Ctrl+C退出程序.")
        from urllib.parse import urlparse
        url=extract_url(input("粘贴分享链接："))
        cId=(urlparse(url).path).split("/")[-1]
        allVideos=getVideoFromId(cId,token)
        download(allVideos)
        logging.info("下载完成！\n")
