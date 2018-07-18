#encoding=utf-8
import requests
import sys
import re
from bs4 import BeautifulSoup
import json
import os
import urllib
reload(sys)
sys.setdefaultencoding('utf-8')

sid=0 #当前歌曲的ID
def GetMusicName():
    headers = {\
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64)'\
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140'\
    ' Safari/537.36'
    }   
    r = requests.get("http://music.baidu.com/top/dayhot",headers = headers)
    bs = BeautifulSoup(r.content,'lxml')
    searchResults = bs.find_all('span',class_="song-title")
    songlist = []
    for name in searchResults:
        #print('--id:' + str(id) + '---歌曲名称：' +name.get_text())
        songlist.append(name.get_text()) 
    return songlist
def Schedule(a,b,c):
    '''
    Use the Schedule function to print the status of downloading
    '''
    per = 100.0 * a * b / c
    if per > 100 :
        per = 100
    #print '%.2f%%' % per

def DownloadMusic(name):
    global sid
    #获取搜索结果
    headers = {\
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64)'\
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140'\
    ' Safari/537.36'
    }
    r = requests.get("https://c.y.qq.com/soso/fcgi-bin/client_search_cp?ct=24&qqmusic_ver=1298&new_json=1&remoteplace=txt.yqq.song&searchid=58762948048961367&t=0&aggr=1&cr=1&catZhida=1&lossless=0&flag_qc=0&p=1&n=20&w="+name +"&g_tk=5381&jsonpCallback=MusicJsonCallback4629048390507926&loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0",headers = headers) 
    sRes = r.text
    sRes = sRes[34:-1]
    #转化为标准的JSON格式 
    jsonRes = json.loads(sRes)
    #获取歌曲的文件名和歌曲id
    listContent = jsonRes['data']['song']['list']
    if(len(listContent) == 0):
        return 0
    filename = 'C400' + jsonRes['data']['song']['list'][0]['file']['media_mid'] + '.m4a'
    songid = jsonRes['data']['song']['list'][0]['file']['media_mid']
    songname = jsonRes['data']['song']['list'][0]['album']['name']
    #检索当前歌曲库是否存在该文件
    path = '/mnt/mydisk/mymusic/'
    realName = songname + '.mp3'
    local = os.path.join(path,realName)
    if(os.path.exists(local) != False):
        return 1
    #由以上的参数获取歌曲的vKey
    r1 = requests.get("https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg?g_tk=5381&jsonpCallback=MusicJsonCallback6925399814011781&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&cid=205361747&callback=MusicJsonCallback6925399814011781&uin=0&songmid="+ songid+"&filename="+filename+"&guid=9125560300")
    sRes = r1.text[34:-1]
    jsonRes = json.loads(sRes)
    vkey = jsonRes['data']['items'][0]['vkey']
    #下载歌曲并显示当前下载的状态
    url = 'http://dl.stream.qqmusic.qq.com/' + filename + '?vkey=' + vkey +'&guid=9125560300&uin=0&fromtag=66'
    logs = '---id:'+str(sid) +'-----dowloading----resource file name:' + filename + '-----song name:'+songname +'---\n'
    try:    
	urllib.urlretrieve(url,local,Schedule)
    except:
	logs +=str(sid) + 'has an Error!\n'
    #重命名歌曲文件，方便之后的检索
    oriFilePath = os.path.join(path,filename)
    if(os.path.exists(oriFilePath) == True):
    	os.rename(oriFilePath,os.path.join(path,realName))
    #写入日志
    crawlerLogs = open('./getmusic.log','ab')
    crawlerLogs.write(logs)
    sid += 1
    return 2


#The main process start 
if __name__ == '__main__': 
	songlist = GetMusicName()
	for searchname in songlist:
    		DownloadMusic(searchname)
