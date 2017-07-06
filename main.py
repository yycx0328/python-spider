from urllib3.util.retry import Retry
from requests import Session
from requests.adapters import HTTPAdapter
import itertools
import configparser
from bs4 import BeautifulSoup
import time
import random
import os


def download(_url, _timeout, _headers=None, _proxies=None):
    try:
        s = Session()
        res = s.get(_url, timeout=_timeout, headers=_headers, proxies=_proxies)
        return res.text
    except Exception as ex:
        print(ex)
        return None


def download_with_retry(_url, _timeout, _retries, _retry_status_code, _headers=None, _proxies=None):
    try:
        s = Session()
        s.mount('http://', HTTPAdapter(max_retries=Retry(total=_retries, status_forcelist=_retry_status_code)))
        res = s.get(_url, timeout=_timeout, headers=_headers, proxies=_proxies)
        return res.text
    except Exception as ex:
        print(ex)
        return None


def save(_text, _file_name):
    try:
        if not os.path.exists('download'):
            os.makedirs('download')
        file_path = './download/%s' % _file_name
        f = open(file_path, 'w')
        f.write(_text)
    except Exception as ex:
        print(ex)
    finally:
        if f:
            f.close()


def get_user_agent(_type):
    config = configparser.ConfigParser()
    config.read('user_agent.cfg', encoding='utf-8')
    if _type == 'pc':
        pc_agent = eval(config.get('info', 'pc_agent'))
        index = random.randint(0, len(pc_agent) - 1)
        dic = dict(pc_agent[index])
        for key in dic:
            return dic[key]
        return None
    elif _type == 'mobile':
        pc_agent = list(config.get('info', 'mob_agent'))
        print(len(pc_agent))
        index = random.randint(0, len(pc_agent) - 1)
        dic = pc_agent[index]
        for key in dic:
            return dic[key]
        return None


def main():
    conf = configparser.ConfigParser()
    conf.read('config.cfg')
    timeout = int(conf.get('config', 'timeout'))
    retries = int(conf.get('config', 'retries'))
    retry_status_code = list(conf.get('config', 'retry_status_code'))

    for index in itertools.count(0):
        url = 'http://example.webscraping.com/places/default/index/%d' % index
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
