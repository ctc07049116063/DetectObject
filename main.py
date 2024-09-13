from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time
import json
import streamlit as st

KEY = st.secrets.KEY
ENDPOINT = st.secrets.ENDPOINT
# クライアント認証
computervision_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(KEY))

# 画像の説明（タグ情報）を取得する
def get_tags(filepath):
    # 画像を開く
    local_image = open(filepath, "rb")

    # 画像の説明を取得するAPI呼び出し
    tags_result = computervision_client.tag_image_in_stream(local_image)
    # tags：タグを取得する（captions：説明文の取得も可能）
    tags = tags_result.tags
    tags_name = []
    for tag in tags:
        tags_name.append(tag.name)
    
    # 取得したタグを返却
    return tags_name

# 物体を検出する
def detect_objects(filepath):
    # 画像を開く
    local_image = open(filepath, "rb")

    # 物体を検出するAPI呼び出し
    detect_objects_results = computervision_client.detect_objects_in_stream(local_image)
    # 矩形の座標情報を取得する（x, y, w, h)
    objects = detect_objects_results.objects
    return objects

import streamlit as st
from PIL import ImageDraw
from PIL import ImageFont
import tempfile
from pathlib import Path

# タイトル
st.title('物体検出アプリ')

# ファイルアップローダーを呼び出し
uploaded_file = st.file_uploader('画像を選択してください。', type=['jpg','png'])
# ファイルが選択されたら描画処理を行う
if uploaded_file is not None:
    # streamlitではファイルパスの取得ができないため、一時ファイルを作成しそのパスからリソースを得る
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        # tempファイルのパスを取得
        img_path = Path(tmp_file.name)
        img_path.write_bytes(uploaded_file.getvalue())
        # 物体検出を行う
        objects = detect_objects(img_path)

    # 画像ファイルを開く
    img = Image.open(uploaded_file)

    # 矩形情報を描画する
    draw = ImageDraw.Draw(img)
    for object in objects:
        # 矩形座標
        x = object.rectangle.x
        y = object.rectangle.y
        w = object.rectangle.w
        h = object.rectangle.h
        # 物体の説明
        caption = object.object_property

        # 説明の書式指定
        textsize = 50
        font = ImageFont.truetype(font='./Helvetica 400.ttf', size=textsize)
        text_w = draw.textlength(caption, font=font)
        text_h = textsize

        # 物体の矩形描画
        draw.rectangle([(x, y), (x+w, y+h)], fill=None, outline='green', width=5)
        # 矩形に付加する情報の描画
        draw.rectangle([(x, y), (x+text_w, y+text_h)], fill='green')
        draw.text((x, y), caption, fil='white', font=font)
    # 画像の描画
    st.image(img)

    # タグ情報取得
    tags_name = get_tags(img_path)
    # カンマ区切りでタグを表示する
    tags_name = ', '.join(tags_name)
    st.markdown('**認識されたコンテンツタグ**')
    st.markdown(f'> {tags_name}')  
    
    # tempファイルを削除する
    tmp_file.close()
    os.unlink(tmp_file.name)