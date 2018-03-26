from time import ctime


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


class Borg(object):
    _shared_state = {}

    def __new__(cls, *args, **kwargs):
        obj = super(Borg, cls).__new__(cls, *args, **kwargs)
        obj.__dict__ = cls._shared_state
        return obj


