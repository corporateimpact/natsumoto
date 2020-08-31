#!/usr/bin/python
# coding: utf-8

# モジュールをインポートする
import time
import datetime
import MySQLdb
import set_info
import sshtunnel
from sshtunnel import SSHTunnelForwarder    # 別々に読み込まないとエラー

temp_alert = 0
result = []
now = None
setdays = None
settimes = None
sensor_name = ["28-01203016c794", "28-01203016c794"]   # 水温用,外気温用


def get_temp():
    """
    センサーからの読取処理
    """
    global result
    global sensor_name
    global now

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
                    print(now + " " + sensor_name[i] + " sensor read NG!")
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
                print(now + " " + names + " sensor Access error.")
                result.append("err")
        else:
            result.append(round(total / sumcount, 1))
        i = i + 1


def set_mysql():
    """
    MySQLへデータ登録する処理
    """
    global result
    global now
    global setdays
    global settimes
    ssh_info = set_info.get_ssh_connect()
    mysql_info = set_info.get_mysql_connect()  # 0 ホスト名 1 ユーザ名 2 パスワード 3 データベース 4 テーブル 5 エンコード 6 接続ポート
    # 接続準備
    #watertemp = result[0]
    #airtemp = result[1]
    with SSHTunnelForwarder(
            (str(ssh_info[0]), int(ssh_info[1])),
            ssh_password='pm#corporaet1',  # ここ変数にすると確実にエラーが起きる
            ssh_pkey=str(ssh_info[4]),
            ssh_username=str(ssh_info[2]),
            remote_bind_address=(str(ssh_info[0]), 3306),  # ここ変数にすると確実にエラーが起きる
            local_bind_address=(str(mysql_info[0]), 3306),  # ここ変数にすると確実にエラーが起きる
    ) as server:
        print("a")
        conn = MySQLdb.connect(
            host=str(mysql_info[0]),
            user=str(mysql_info[1]),
            password=str(mysql_info[2]),
            db=str(mysql_info[3]),
            charset=str(mysql_info[5]),
            port=int(mysql_info[6]),
        )
        cursor = conn.cursor()
        print("b")
        # センサー値エラーの対応
        if result[0] == "err":
            try:
                #cursor = conn.cursor()
                sql_a = 'select water_temp from natsumoto_data order by days desc, times desc limit 1;'
                cursor.execute(sql_a)
                conn.commit()
                result[0] = sql_a.fetchall()
                print(now + ' watertemp None, DB Request.')
            except:
                print(now + ' watertemp None, DB Request error')
            finally:
                #conn.close()
                pass
        else:
            pass
        print("c")
        if resul[1] == "err":
            try:
                #cursor = conn.cursor()
                sql_b = 'select air_temp from natsumoto_data order by days desc, times desc limit 1;'
                cursor.execute(sql_b)
                conn.commit()
                result[1] = sql_b.fetchall()
                print('[' + now + '] temp None, DB Request.')
            except:
                print(now + ' airtemp None, DB Request error')
            finally:
                #conn.close()
                pass
        # アラート値の設定 範囲内→0　範囲外→1
        print("d")
        if -5 < result[0] < 19:
            watertemp_alert = 0
        else:
            watertemp_alert = 1
        # 開始
        print("e")
        try:
            #cursor = conn.cursor()
            sql = "insert into water_temp values (%s, %s, %s, %s, %s)"
            val = (setdays, settimes, result[0], result[1], watertemp_alert)
            cursor.execute(sql, val)
            print("f")
            conn.commit()
        # print("Data commited.")
        except:
            print("DB Access Error!")
        finally:
            print("g")
            conn.close()
            print("h")


def csv_write():
    """
    csvファイルに取得情報を書き込む処理
    """
    global result
    global setdays
    output_file = "/home/natsumotopi/mainsys/data/infos/1/" + setdays + ".csv"
    # 書き込みデータ準備
    w_data = now + ", watertemp:" + str(result[0]) + ", airtemp:" + str(result[1]) + "\n"
    with open(output_file, mode='a') as f:
        try:           # データ書き込み
            f.write(w_data)
        except:        # 書き込み失敗時
            print(now + " data export Error.")


def main():
    # 時刻取得
    global now
    global setdays
    global settimes
    global result
    date = datetime.datetime.today()
    now = date.strftime('%Y/%m/%d %H:%M:00')
    setdays = date.strftime('%Y-%m-%d')
    settimes = date.strftime('%H:%M:00')
    result = [15.0, 25.0]
    #get_temp()
    print("1")
    set_mysql()
    print("2")
    csv_write()
    print("3")


# main関数を呼び出す
if __name__ == '__main__':
    main()
