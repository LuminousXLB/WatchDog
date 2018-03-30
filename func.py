import birthday
import jwc_anno
import sys

if __name__ == '__main__':
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "watchdog.settings")

    actions = {
        'birthday': birthday.app,
        'jwc': jwc_anno.app
    }
    if len(sys.argv) < 2 or sys.argv[1] not in actions:
        print('usage: python func.py ACTION')
        print('ACTION can be:')
        for k in actions:
            print('    %s' % k)
        sys.exit(1)
    actions[sys.argv[1]]()
