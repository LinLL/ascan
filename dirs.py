import asyncio,aiohttp,random,string,requests,difflib
import urllib.parse


def random_s(strlen=8):
    chars = list(string.ascii_letters)
    random.shuffle(chars)
    return "".join(chars[:strlen])

def cscheme(url):
    parse = urllib.parse.urlparse(url)
    if parse.scheme is "":
        return False
    else:
        return True

class Dirscaner:

    def __init__(self, hosts, max_tries=4, loop=None):
        self.hosts = hosts
        self.max_tries = max_tries
        self.loop = loop or asyncio.get_event_loop()
        self.q = asyncio.Queue(loop=self.loop)
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.error404_flag = False

    def close(self):
        self.session.close()

    def getdic(self, fpath=None):
        fpath = fpath or "dirdic"
        with open(fpath) as dic:
            for p in dic:
                self.q.put_nowait(p.split())

    def fetch_random(self, host):
        path = "/"+random_s()
        url = urllib.parse.urljoin(host, path)
        resp = requests.get(url)
        return resp.status_code,resp.content

    def catch_web_strs(self, content, lenth, num=3):
        random_nums = [random.randint(0,len(content)) for i in range(num)]
        return [content[i:i+lenth] for i in random_nums]

    def fetch_error(self, host):
        randoms = [self.fetch_random(host) for i in range(4)]
        status = [statu for statu,content in randoms]
        contents = [content for statu,content in randoms]
        self.catch_web_strs(contents[0], 20)
        if list(set(status)) == 404:
            self.error404_flag = True
        else:
            keys = self.catch_web_strs(contents[0], 20)                  #确定关键字是否在其他页面出现


if __name__=="__main__":
    d = Dirscaner("http://www.baidu.com")
    d.fetch_error(host="http://www.baidu.com")
    d.close()