import requests
from xml.dom.minidom import parseString
from bs4 import BeautifulSoup
from time import sleep, ctime
from datetime import datetime
from django.core.mail import send_mail
import os


class Logger:
    def __init__(self, log_file, *pre):
        self.log_file = log_file
        self.pre = pre

    def __call__(self, *msg):
        lst = self.pre + msg
        print('[%s]' % ctime(), *lst)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write('[%s]' % ctime())
            f.write(' '.join(lst))
            f.write('\n')


class watchdog:
    def __init__(self, url, recipent, log_file, mail_max):
        self.url = url
        self.recipent = recipent
        self.mail_max = mail_max
        self.mail_cnt = 0
        self.logger = Logger(log_file)

        lst = self._get()
        self.anno_len = len(lst)
        self.logger('init {}'.format(self.anno_len))

    def _mail(self, title, content):
        send_mail(title, content, 'taraxacum45e9a@aliyun.com', self.recipent)
        self.mail_cnt += len(self.recipent)

    def _get(self):
        rsp = requests.get(self.url)
        rss = rsp.content.decode('gbk')
        doc = parseString(rss)
        return doc.getElementsByTagName('item')

    def _doc2dict(self, doc):
        item = BeautifulSoup(doc.toxml(), 'xml').find('item')
        return {
            'title': item.find('title').text,
            'link': item.find('link').text,
            'pubdate': item.find('pubDate').text
        }

    def _writehtml(self, url):
        fn = url.split('/')[-1]
        with open('/root/download/anno/' + fn, 'wb') as f:
            rsp = requests.get(url)
            f.write(rsp.content)

    def _writexml(self):
        fn = 'rss_notice.xml'
        with open('/root/douwnload/anno/' + fn, 'wb') as f:
            rsp = requests.get(self.url)
            f.write(rsp.content)

    def _announce(self, pool):
        lst = []

        for item in pool:
            data = self._doc2dict(item)
            lst.append(data)
            self._writehtml(data['link'])
            self.logger('{title} | {pubdate} | {url}'.format_map(data))

        self._mail(
            '【WatchDog】教务处公告更新',
            str(lst).replace(',', ',\n')
        )

        if self.mail_cnt >= self.mail_max:
            txt = '[ERROR] The number of mails sent has been {}'.format(
                self.mail_cnt)
            self.logger(txt)
            send_mail('【WatchDog】WatchDog Error', txt)
        return self.mail_cnt >= self.mail_max

    def __call__(self):
        lst = self._get()
        if len(lst) > self.anno_len:
            pool = []
            new_length = len(lst)
            while len(lst) > self.anno_len:
                pool.append(lst[0])
                del lst[0]
            self.anno_len = new_length
            return self._announce(pool)
        else:
            self.logger('No new announcement found')
            return False


def sleep_stratagey():
    t = datetime.now()
    if t.weekday() == 5 or t.weekday() == 6:
        sleep(8*60*60)
    elif t.hour > 18 or t.hour < 8:
        sleep(2*60*60)
    else:
        sleep(15*60)


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "watchdog.settings")

    jwc = watchdog(
        'http://jwc.sjtu.edu.cn/rss/rss_notice.aspx?SubjectID=198015&TemplateID=221027',
        ['john980118@outlook.com'],
        'wd.log',
        150
    )

    while True:
        sleep_stratagey()

        try:
            jwc()
        except BaseException as err:
            jwc.logger('[ERROR] {}'.format(err))
            send_mail(
                '【WatchDog】WatchDog出错',
                str(err),
                'taraxacum45e9a@aliyun.com',
                ['454633705@qq.com']
            )
            break
