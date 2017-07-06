from urllib3.util.retry import Retry
from requests import Session
from requests.adapters import HTTPAdapter
import itertools
import configparser
from bs4 import BeautifulSoup
import time
import random
import os


''' 下载页面内容，在做网络爬虫时，一般的思路是先把爬到的网页内容下载下来，保存到自己的本地
然后再解析下载的网页内容，将有用的数据保存至DB中 '''
def download(_url, _timeout, _headers=None, _proxies=None):
    try:
        s = Session()
        # get方式请求url内容，并设置超时，请求头和代理
        res = s.get(_url, timeout=_timeout, headers=_headers, proxies=_proxies)
        # 返回网页内容
        return res.text
    except Exception as ex:
        print(ex)
        return None


# 下载页面内容，当下载失败请求状态码为指定的状态码时重试
def download_with_retry(_url, _timeout, _retries, _retry_status_code, _headers=None, _proxies=None):
    try:
        s = Session()
        # get方式请求url内容，并设置超时及失败重试请求，请求头和代理
        s.mount('http://', HTTPAdapter(max_retries=Retry(total=_retries, status_forcelist=_retry_status_code)))
        res = s.get(_url, timeout=_timeout, headers=_headers, proxies=_proxies)
        # 返回网页内容
        return res.text
    except Exception as ex:
        print(ex)
        return None


# 将网页内容保存在文件中
def save(_text, _file_name):
    try:
        # 保存在项目的download目录下，当download目录不存在时自动创建目录
        if not os.path.exists('download'):
            os.makedirs('download')
        file_path = './download/%s' % _file_name
        # 创建并保存文件内容
        f = open(file_path, 'w')
        f.write(_text)
    except Exception as ex:
        print(ex)
    finally:
        if f:
            f.close()


# 获取user agent，当不停的同一网站的多个页面数据时，有很多网站会将同一user agent和同一ip的请求视为攻击并且拦截掉
def get_user_agent(_type):
    # 从配置文件中读取配置信息
    config = configparser.ConfigParser()
    config.read('user_agent.cfg', encoding='utf-8')
    # 随机获取PC端的User-Agent
    if _type == 'pc':
        pc_agent = eval(config.get('info', 'pc_agent'))
        index = random.randint(0, len(pc_agent) - 1)
        dic = dict(pc_agent[index])
        for key in dic:
            return dic[key]
        return None
    # 随机获取移动端User-Agent
    elif _type == 'mobile':
        pc_agent = list(config.get('info', 'mob_agent'))
        print(len(pc_agent))
        index = random.randint(0, len(pc_agent) - 1)
        dic = pc_agent[index]
        for key in dic:
            return dic[key]
        return None


def main():
    # 读取配置文件
    conf = configparser.ConfigParser()
    conf.read('config.cfg')
    # 获取超时设置
    timeout = int(conf.get('config', 'timeout'))
    # 获取重试次数设置
    retries = int(conf.get('config', 'retries'))
    # 获取重试错误码设置
    retry_status_code = list(conf.get('config', 'retry_status_code'))
    ''' 
        从0开始计数，当抓取的页面数据含有下一页内容，则继续下载网页内容
        http://example.webscraping.com是一个很不错的爬虫实例网站，很适合爬虫菜鸟练手
    '''
    for index in itertools.count(0):
        url = 'http://example.webscraping.com/places/default/index/%d' % index
        ''' 
            每次切换不同的User-Agent，以便被网站拦截，更好的方式其实还应该设置代理IP，
            但由于本人没有找到比较稳定的免费代理IP，示例代码中就没有使用代理IP
        '''
        user_agent = get_user_agent('pc')
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;",
            "User-Agent": user_agent
        }
        text = download_with_retry(url, timeout, retries, retry_status_code, headers)
        if text is None:
            continue
        soup = BeautifulSoup(text, 'html.parser')
        page = soup.find(id='pagination')
        if page is None:
            print(text)
        a_list = page.find_all('a')
        if a_list:
            href = a_list[-1].get('href')
            if href:
                next_index = int(href.split('/')[-1])
                save(text, '%d.html' % index)
                if next_index <= index:
                    print(next_index)
                    break
        time.sleep(1)

if __name__ == '__main__':
    main()
