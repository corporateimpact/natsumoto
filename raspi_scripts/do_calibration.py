"""
T3_DO計キャリブレーション
"""

#!/usr/bin/ python
# -*- coding: utf-8 -*-

import subprocess
import time
import datetime

res = None

def main():
    """
    メイン処理
    """
    global res
    now = datetime.datetime.now().strftime("[" + "%Y-%m-%d %H:%M:%S" + "] ")
    res = input(now + "\nキャリブレーション選択\n" + '1:DOフル較正\n' + '2:DOゼロ較正\n>>')
    if str.isdecimal(res) == True:
        res = int(res)
        do_calibration(res)
    else:
        print('数字を入力してください')
        time.sleep(0.5)
    now = datetime.datetime.now().strftime("[" + "%Y-%m-%d %H:%M:%S" + "] ")
    print('終了\n' + now)


def do_calibration(res):
    """
    DOセンサーのキャリブレーション処理
    """
    if res == 1:
        print('DOフル較正を行います')
        time.sleep(0.5)
        print('較正中')
        calibration_cmd = 'sudo i2cset -y 1 0x61 0x63 0x61 0x6c i'
        subprocess.call(calibration_cmd.split())
        time.sleep(1)
    elif res == 2:
        print('DOゼロ較正を行います')
        time.sleep(0.5)
        print('較正中')
        calibration_cmd = 'sudo i2cset -y 1 0x61 0x63 0x61 0x6c 0x2c 0x30 i'
        subprocess.call(calibration_cmd.split())
        time.sleep(1)
    else:
        time.sleep(0.5)
        print('コマンドエラー')
        time.sleep(0.5)



if __name__ == '__main__':
    main()







