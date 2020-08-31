#!/usr/bin/python
# coding: utf-8

# モジュールをインポートする
import time
import datetime

temp_alert = 0
result = []
sensor_name = ["28-01203016c794", "28-01203016c794"]   # 水温用,外気温用



columns_list = ["", "", "", "", ]   #カラムリスト

def get_temp():
    """
    センサーからの読取処理
    """
    global result
    global sensor_name

    # センサーの本数分処理を回す 配列数カウント
    sensor_count = len(sensor_name)
    for i in range(int(sensor_count)):
        # ループ前リセット
        total     = 0
        sumcount  = 0
        line      = 0
        linecount = 0
        str       = 0
        temp      = 0
        i = 1
        # 10回計測
        for num in range(10):
            linecount = 1
            # ファイルをオープンする
            with open("/sys/bus/w1/devices/" + sensor_name[i] + "/w1_slave", "r")as slave_data:
                # センサー値格納ファイルの内容確認
                # 内容例はこんな感じ
                # a7 01 4b 46 7f ff 0c 10 1f : crc=1f YES
                # a7 01 4b 46 7f ff 0c 10 1f t=26437
                # t=数値5桁の部分が温度（℃）　千分の一すると有効値になる
                try:
                    for line in slave_data:  # ターゲットは2行目なのでforで回す
                        if linecount == 2:
                            str = line.split(" ")
                            temp = (float(str[9].replace("t=", "")) / 1000)
                            print(temp)
                            # -20度以上50度以下の値を使用する
                            if -20 < temp < 50:
                                total = total + temp
                                sumcount = sumcount + 1  # 有効な値を読み込めた際は合計数値数+1
                            linecount = 1  # 行カウントを戻す
                        else: # 2行目以外はいらないのでカウントだけ追加
                            linecount = linecount + 1
                except:
                    print("NG!")
            # ファイルをクローズする
            # slave_data.close()
            # 次まで待機
            time.sleep(2)
        # 有効数値を計算する
        if sumcount == 0: #カウントゼロの場合はエラー対応
            if i == 1:
                names = "watertemp"
            elif i == 2:
                names = "temp"
            else:
                names = "err"
                print(names + "sensor error.")
                result.append("err")
        else:
            result.append(round(total / sumcount, 1))
        i = i + 1


def main():
    global result
    # 時刻取得
    date = datetime.datetime.today()
    now = date.strftime('[%Y/%m/%d %H:%M:00]')
    get_temp()
    print(result)
    print(now + "\n" + "水温: " + str(result[0]) + "\n" + "気温: " + str(result[1]))


def callback():
    """
    他から呼び出された際に動かす処理
    """
    global result
    get_temp() #値取得
    date = datetime.datetime.today()
    setdays = date.strftime('%Y-%m-%d')
    settimes = date.strftime('%H:%M:00')
    if -5 < result[0] < 19:
        watertemp_alert = 0
    else:
        watertemp_alert = 1
    return setdays, settimes, result[0], result[1], watertemp_alert


# main関数を呼び出す
if __name__ == '__main__':
    main()
