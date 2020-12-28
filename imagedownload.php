<?php
$zip = new ZipArchive;
// 表示している日付のアップロード画像をまとめてダウンロードする処理


//テスト用カメラID
$camera_id = 1;
//テスト用日付
$date = date("Ymd");

// 作成するzipファイル名とターゲットになるファイル名の指定
$zip_filename = __DIR__ . '/images/dl/' . $date . '_' . $camera_id . '.zip'
$dl_filename = $date . '_' . $camera_id . '.zip'  //ダウンロードしたときのファイル名
$targetfile = __DIR__. '/images/' . $camera_id . '/' . $date . '/*00.jpg'

$zip->open($zip_filename, ZipArchive::CREATE|ZipArchive::OVERWRITE);
$zip->addFile($targetfile);
$zip->close();


// ファイルタイプを指定
header('Content-Type: application/force-download');

// ファイルサイズを取得し、ダウンロードの進捗を表示
header('Content-Length: '.filesize($zip_filename));

// ファイルのダウンロード、リネームを指示
header('Content-Disposition: attachment; filename="'.$dl_filename.'"');

// ファイルを読み込みダウンロードを実行
readfile($zip_filename);


?>