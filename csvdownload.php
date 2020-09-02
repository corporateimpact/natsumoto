<?php

// タイムアウト時間を変更する
ini_set("max_execution_time", 600);

$dateStr = date("Y/m/d");
$dl_date_from = $dateStr;
if (isset($_POST['date_from'])) {
  if ($_POST['date_from'] != "") {
    $dateStr = str_replace("/", "", $_POST['date_from']);
    $dl_date_from = $_POST['date_from'];
    $timeStr = "000000";
  }
}
if (isset($_GET['date_from'])) {
  if ($_GET['date_from'] != "") {
    $dateStr = str_replace("/", "", $_GET['date_from']);
    $dl_date_from = $_GET['date_from'];
    $timeStr = "000000";
  }
}

$dateStr = date("Y/m/d");
$dl_date_to = $dateStr;
if (isset($_POST['date_to'])) {
  if ($_POST['date_to'] != "") {
    $dateStr = str_replace("/", "", $_POST['date_to']);
    $dl_date_to = $_POST['date_to'];
    $timeStr = "000000";
  }
}
if (isset($_GET['date_to'])) {
  if ($_GET['date_to'] != "") {
    $dateStr = str_replace("/", "", $_GET['date_to']);
    $dl_date_to = $_GET['date_to'];
    $timeStr = "000000";
  }
}


//送信されたfromとtoの日付をチェック
if ($dl_date_to < $dl_date_from) {
  $dummy_date = $dl_date_from;
  $dl_date_from = $dl_date_to;
  $dl_date_to = $dummy_date;
}


//ＣＳＶ出力
header("Content-Type: application/octet-stream");
header("Content-Disposition: attachment; filename=" . str_replace("/", "", $dl_date_from) . "-" . str_replace("/", "", $dl_date_to) . ".csv");

$mysqli = new mysqli('localhost', 'root', 'pm#corporate1', 'natsumoto');
$mysqli->set_charset('utf8');

//測定値テーブル抽出クエリ
$sql = "SELECT natsumoto_data.days, natsumoto_data.times, natsumoto_data.water_temp, natsumoto_data.natsumoto_temp, amedas_temp.air_temp FROM natsumoto_data LEFT JOIN amedas_temp ON natsumoto_data.days = amedas_temp.days AND natsumoto_data.times = amedas_temp.times WHERE natsumoto_data.day BETWEEN '" . $dl_date_from . "' AND '" . $dl_date_to . "' ORDER BY natsumoto_data.days, natsumoto_data.times";

$res = $mysqli->query($sql);

// bomをつける
$bom = "\xEF\xBB\xBF";

// ヘッダー作成
$header_str = "\"日付\",\"時刻\",\"水温\",\"夏本外気温\",\"新町気温\"\r\n";

// ヘッダにbomを付与して出力
echo $bom . $header_str;

// または↓でSJISエンコード
// echo mb_convert_encoding($header_str, "SJIS", "UTF-8");


while ($row = $res->fetch_array()) {
  print("\"" . $row[0] . "\",\""  //日付
    . $row[1] . "\",\""  //時刻
    . $row[2] . "\",\""  //水温
    . $row[3] . "\",\""  //外気温
    . $row[4] . "\"\r\n"); //新町気温
}



$mysqli->close();
