from time import sleep, ctime
from datetime import datetime, timedelta
from django.core.mail import send_mail
import pandas as pd


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


class Postman:
    def __init__(self, send_from, recipent_list, administrator, mail_max, log_file, *pre):
        self.send_from = send_from
        self.recipent_list = recipent_list
        self.administrator = administrator
        self.mail_max = mail_max
        self.mail_cnt = 0
        self.pre = ' '.join(pre)
        self.log = Logger(log_file, pre, 'mail: ')

    def __call__(self, subject, message):
        send_mail(
            '[{}] {}'.format(self.pre, subject),
            message,
            self.send_from,
            self.recipent_list
        )
        self.mail_cnt += 1
        self.log(self.mail_cnt, subject, message)
        if self.mail_cnt == self.mail_max:
            self.alert('touch mail max')

    def alert(self, message):
        send_mail(
            '[{}] {}'.format(self.pre, 'alert'),
            message,
            self.from_email,
            [self.administrator]
        )
        self.log(self.mail_cnt, 'alert', message)


class WatchDog:
    def __init__(self, postman, logger, xlsx_file, sheet_name, oforamt='%Y-%m-%d'):
        self.df = pd.read_excel(xlsx_file, sheet_name, index_col='toyear')
        self.iformat = '%Y-%m-%d'
        self.oforamt = oforamt
        self.postman = postman
        self.log = logger

    def check(self, day, delta=0):
        f = datetime.strftime(day, self.iformat)
        e = datetime.strftime(day+timedelta(delta), self.iformat)
        print(f, e)
        print(self.df)
        res = self.df[f:e]
        ret = res.values.tolist()
        for item in ret:
            item[0] = item[0].strftime(self.oforamt)
        return ret

    def __call__(self):
        today = datetime.now()
        lst7 = self.check(today, 7)

        msg = [
            '=== 生日提醒 ===',
            '- 今天'
        ]
        msg += ['    '+str(item) for item in self.check(today)]
        msg.append(
            '- 三天之内'
        )
        msg += ['    '+str(item) for item in self.check(today, 3)]
        msg.append(
            '- 七天之内'
        )
        msg += ['    '+str(item) for item in lst7]
        msg.append(
            '=== that\'s all ==='
        )
        self.log(str(lst7))
        self.postman('生日提醒', '\n'.join(msg))


def today(yesterday=False):
    if yesterday:
        return datetime.strftime(datetime.now()-timedelta(1), '%Y-%m-%d')
    else:
        return datetime.strftime(datetime.now(), '%Y-%m-%d')


if __name__ == '__main__':
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "watchdog.settings")

    log = Logger('birthday.log')
    postman = Postman(
        'taraxacum45e9a@aliyun.com',
        ['454633705@qq.com'],
        '454633705@qq.com',
        200,
        'birthday.log',
        'birthday'
    )
    wd = WatchDog(postman, log, 'sisi.xlsx', 'Sheet1')

    td = today(yesterday=True)
    while True:
        try:
            if today() != td:
                wd()
                log('sleep(60*60*8)')
                sleep(60*60*8)
            else:
                log('sleep(60*30)')
                sleep(60*30)
        except BaseException as err:
            postman.alert(err.msg)
            break
