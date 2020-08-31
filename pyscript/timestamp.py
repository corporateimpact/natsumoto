from PIL import ImageFont, ImageDraw, Image
import os, sys, glob

# フォントのパスとサイズを指定 --- (*1)
font_path = "mikachan.otf"
font_size = 40
text_pos = (10, 10)
text_color = (50, 0, 0)
# 出力パスの指定
out_path = "./out"
if not os.path.exists(out_path): os.mkdir(out_path)

# コマンドラインを得る --- (*2)
if len(sys.argv) < 3:
    print("textout_all.py フォルダパス テキスト")
    quit()
dir_path = sys.argv[1]
label = sys.argv[2]

# フォントを読み込む --- (*3)
font = ImageFont.truetype(font_path, font_size)

# ファイルの一覧を得る --- (*4)
files = glob.glob(dir_path + "/*.jpg")
# 連続で画像にテキストを書き込む --- (*5)
for f in files:
    print("textout: " + f)
    image = Image.open(f)
    draw = ImageDraw.Draw(image)
    # 白抜き文字を出力 --- (*6)
    for i in range(-3, 4):
        for j in range(-3, 4):
            x = text_pos[0] + i
            y = text_pos[1] + j
            draw.text((x, y), label, fill=(255,255,255), font=font)
    draw.text(text_pos, label, fill=text_color, font=font)
    path = out_path + "/" + os.path.basename(f)
    image.save(path)