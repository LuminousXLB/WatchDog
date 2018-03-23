from django.core.mail import send_mail
import os


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "watchdog.settings")

    send_mail(
        '[WatchDog] test email',
        'just test',
        'taraxacum45e9a@aliyun.com',
        ['john980118@163.com']
    )
