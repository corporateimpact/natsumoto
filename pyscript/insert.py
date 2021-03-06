#!/usr/bin/ python
# -*- coding: utf-8 -*-

"""
取得したデータを登録する処理
"""
import sshtunnel
from sshtunnel import SSHTunnelForwarder    # 別々に読み込まないとエラー
import MySQLdb
import get_temp
import set_info
import sys
import err
import os
import datetime

# global
data = None
ssh_info = None
mysql_info = None
mysql_columns = None
mysql_value = None
sql = None
output_file = None

def get_infomation():
    """
    必要なデータを読み込み準備する関数
    """
    global data
    global ssh_info
    global mysql_info
    global mysql_columns
    global mysql_value
    global sql
    global output_file
    data = get_temp.callback()                   # 0 日付 1 時刻 2 水温 3 外気温
    ssh_info = set_info.get_ssh_connect()        # 0 サーバアドレス 1 SSHポート 2 ユーザ名 3 パスワード 4 認証鍵 5 アクセスポート
    mysql_info = set_info.get_mysql_connect()    # 0 ホスト名 1 ユーザ名 2 パスワード 3 データベース 4 テーブル 5 エンコード 6 接続ポート
    mysql_columns_set = set_info.get_columns_info().split(',')
    output_file = "/home/natsumotopi/mainsys/data/infos/1/" + data[0] + ".csv"

    # mysql構文の整理と格納
    columns_count = len(mysql_columns_set)
    for i in range(int(columns_count)):
        if i == 0:
            mysql_columns =  ' (' + mysql_columns_set[i]
            mysql_value = 'values (%s'
            i = i + 1
        else:
            mysql_columns = mysql_columns + ', ' + mysql_columns_set[i]
            mysql_value = mysql_value + ', %s'
            i = i + 1
    mysql_columns = mysql_columns + ') '
    insert_data = mysql_value + ')'
    sql = 'insert into ' + mysql_info[3] + '.' + mysql_info[4] + mysql_columns + insert_data


def sql_sshtunnel_connect():
    """
    接続とデータベース登録を行う関数
    """
    global data
    global ssh_info
    global mysql_info
    global mysql_columns
    global mysql_value
    # 構文準備
    #print(sql)
    # SSHポートフォワーディング
    with SSHTunnelForwarder(
            (str(ssh_info[0]), int(ssh_info[1])),
            ssh_password='pm#corporaet1',    # ここ変数にすると確実にエラーが起きる
            ssh_pkey=str(ssh_info[4]),
            ssh_username=str(ssh_info[2]),
            remote_bind_address=(str(ssh_info[0]), 3306), # ここ変数にすると確実にエラーが起きる
            local_bind_address=(str(mysql_info[0]), 3306), # ここ変数にすると確実にエラーが起きる
        ) as server:
        conn = MySQLdb.connect(
            host=str(mysql_info[0]),
            user=str(mysql_info[1]),
            password=str(mysql_info[2]),
            db=str(mysql_info[3]),
            charset=str(mysql_info[5]),
            port=int(mysql_info[6]),
        )
        dt_now = datetime.datetime.now()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (data[0], data[1], data[2], data[3], data[4]))
            conn.commit()
        except:     # エラー時処理呼び出し
            conn.close()
            print("[" + dt_now.strftime('%Y-%m-%d %H:%M:%S') + "] Connection Error.")
            err.main()
            sys.exit()
        finally:    # 終了処理
            conn.close()



def debug_print():
    """
    確認用に情報出力する関数
    """
    print(data)
    print(ssh_info)
    print(mysql_info)
    print(mysql_columns)
    print(mysql_value)
    print(sql)


def csv_write():
    """
    csvファイルに取得情報を書き込む関数
    """
    global output_file
    w_data = str(data[0]) + "," + str(data[1]) + "," + str(data[2]) + "," + str(data[3]) + "\n"
    dt_now = datetime.datetime.now()
    with open(output_file, mode='a') as f:
        try:           # データ書き込み
            f.write(w_data)
        except:        # 書き込み失敗時
            print("[" + dt_now.strftime('%Y-%m-%d %H:%M:%S') + "] data export Error.")


def main():
    get_infomation()
    #debug_print()
    csv_write()
    sql_sshtunnel_connect()


if __name__ == '__main__':
    main()
