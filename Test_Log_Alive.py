import datetime
import time
from threading import Thread


def alive():
    while True:
        print(f"( alive :) {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.")
        time.sleep(5)


def test_time():
    while True:
        print(f"\rВремя: {datetime.datetime.now().strftime('%H:%M:%S.')}", end='')
        time.sleep(1)


if __name__ == '__main__':
    th = Thread(target=alive)
    th.start()
    test_time()
