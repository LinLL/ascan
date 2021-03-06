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

    def __init__(self, host, max_tries=3, loop=None, max_workers=10, key_num=3):
        self.host = host
        self.key_num = key_num
        self.max_tries = max_tries
        self.max_workers = max_workers
        self.loop = loop or asyncio.get_event_loop()
        self.q = asyncio.Queue(loop=self.loop)
        self._session = None
        self.error404_flag = False
        self.conerror = 0               #连接失败数，大于10次代表被封或者无法正常连接，抛出异常
        self.stop = False
        self.done = []
        self.status30x = 0
        self.error30x_flag = False
        self.keys_30x = None

    @property
    def session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession(loop=self.loop, read_timeout=10)
        return self._session

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

    def fetch_error(self, host, num=3):
        """
        获取错误页面关键词,如果是404标记无法访问页面则修改error404_flag标志位为真，使用404判断页面
        :param host:
        :param num: 提取关键词数量
        :return: error keys
        """
        keys = []
        randoms = [self.fetch_random(host) for i in range(4)]
        status = [statu for statu,content in randoms]
        contents = [content for statu,content in randoms]
        self.catch_web_strs(contents[0], 20, num)
        if  set(status)=={404}:
            self.error404_flag = True
        else:
            keys = self.catch_web_strs(contents[0], 20, num)                  #确定共同关键字
            while True:
                num = len(keys)
                for k in keys:
                    for content in contents[1:]:
                        if k not in content:
                            keys.remove(k)
                if len(keys) == num:
                    break
        return keys

    def checkpath(self, keys, content):
        """
        关键词全部命中，说明是不存在页面
        :param keys: 关键词
        :param content: 页面
        :return:
        """
        flag = 0
        for k in keys:
            if k in content:
                flag += 1
        if flag < len(keys):
            return True
        else:
            return False

    async def afetch_page(self, url, keys):
        try:
            response = await self.session.get(url, allow_redirects=False)
        except aiohttp.ClientError as e :
            self.conerror += 1
            if self.conerror > 10:
                print("Too many error connections. Take care of fireware!")
                self.stop = True
                self.conerror = 0
            return
        if response.status in [301,302]:
            self.status30x += 1
            content = await response.read()
            if self.status30x>5 and not self.error30x_flag:
                self.error30x_flag = True
                self.keys_30x = self.catch_web_strs(content, 10)
            if self.error30x_flag:
                if self.checkpath(self.keys_30x, content):
                    self.done.append((url, response.status))
            else:
                self.done.append((url, response.status))
        else:
            if self.error404_flag:                          #根据之前提取关键字时确定的404页面状态选择判断方法
                if response.status != 404:
                    self.done.append((url,response.status))

            else:
                content = await response.read()
                if self.checkpath(keys, content):
                    self.done.append((url, response.status))

        await response.release()

    async def work(self, keys):
        try:
            while True:
                if self.stop == False:
                    url = await self.q.get()
                    if "::" in url[0]:                               #避免双冒号出现在url中引发urljoion合并bug
                        self.q.task_done()
                        continue

                    url = urllib.parse.urljoin(self.host, url[0])
                    await self.afetch_page(url, keys)
                    self.q.task_done()
                else:
                    await self.q.get()
                    self.q.task_done()
        except asyncio.CancelledError as e:
            pass
        except Exception as e:
            print(e)
            pass

    async def scan(self):
        keys = self.fetch_error(self.host)
        asyncio.ensure_future(self.status(), loop=self.loop)
        workers = [asyncio.ensure_future(self.work(keys), loop=self.loop) for _ in range(self.max_workers)]
        self.getdic()
        await self.q.join()
        for w in workers:
            w.cancel()

    async def status(self):
        while True:
            print(self.q.qsize())
            await asyncio.sleep(10.0)

if __name__=="__main__":
    import time
    t = time.time()
    d = Dirscaner("http://www.jzyz.jzedu.cn/", max_workers=100)
    d.loop.run_until_complete(d.scan())
    d.close()
    t = time.time()-t
    print(t)
    print(d.done)


