# encoding=utf-8
import requests
from bs4 import BeautifulSoup


def get_list_agent(_group):
    list_agent = []
    for li in _group.find_all('li'):
        dic_agent = {}
        if li.find('div') is not None:
            d_key = li.find('span').string
            d_value = li.find('input')['value']
            dic_agent[d_key] = d_value
            list_agent.append(dic_agent)
    return list_agent


def main():
    try:
        url = 'http://www.jsons.cn/useragent/'
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        list_group = soup.select('.list-group')
        f = open('user_agent.cfg', 'w', encoding='utf-8')
        f.write('[info]\n')
        f.write('# PC端 User-Agent\n')
        pc_agent = get_list_agent(list_group[0])
        f.write('pc_agent = ' + str(pc_agent))
        f.write('\n# 移动设备端 User-Agent\n')
        mob_agent = get_list_agent(list_group[1])
        f.write('mob_agent = ' + str(mob_agent))
        f.flush()
    except Exception as ex:
        print(ex)
    finally:
        if f:
            f.close()

if __name__ == '__main__':
    main()
