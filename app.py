import streamlit as st
from PIL import Image
import numpy as np
import easyocr
import unicodedata
import re
import Levenshtein
from unidecode import unidecode

# EasyOCR リーダー（日本語・英語対応）, キャッシュ推奨
@st.cache_resource
def get_reader():
    return easyocr.Reader(['ja', 'en'])

# テキスト正規化関数（不要な記号除去・大文字小文字正規化・仮名正規化も可）
def normalize_text(text):
    text = unicodedata.normalize('NFKC', text)
    text = unidecode(text)        # 英数字は半角化
    text = text.lower()
    text = re.sub(r'[^\\wぁ-んァ-ン一-龥]', '', text)  # 日本語・英字以外除去
    return text

# OCR実行
def ocr_image_easyocr(image):
    # PIL.Image → np.array 変換
    img_arr = np.array(image.convert('RGB'))
    results = get_reader().readtext(img_arr, detail=0, paragraph=True)
    return ''.join(results)

# 類似度計算（Levenshtein距離ベース）
def calc_similarity(text1, text2):
    if not text1 or not text2:
        return 0.0
    return 1 - Levenshtein.distance(text1, text2) / max(len(text1), len(text2))

st.title('画像OCR（手書き対応）テキスト比較アプリ')
st.write('2つの画像をアップロードし、OCRで抽出したテキストが一致するか判定します。')

img1 = st.file_uploader('画像1をアップロード', type=['png', 'jpg', 'jpeg'], key='img1')
img2 = st.file_uploader('画像2をアップロード', type=['png', 'jpg', 'jpeg'], key='img2')

if img1 and img2:
    image1 = Image.open(img1)
    image2 = Image.open(img2)
    st.image([image1, image2], caption=['画像1', '画像2'], width=200)

    text1 = ocr_image_easyocr(image1)
    text2 = ocr_image_easyocr(image2)

    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)

    similarity = calc_similarity(norm1, norm2)

    st.subheader('OCR抽出結果')
    st.write('画像1:', text1)
    st.write('画像2:', text2)
    st.write('---')
    st.subheader('正規化後テキスト')
    st.write('画像1:', norm1)
    st.write('画像2:', norm2)
    st.write('---')
    st.subheader('類似度スコア')
    st.write(f'{similarity:.2f}')

    if similarity == 1.0:
        st.success('一致しました！')
    else:
        st.warning('一致しませんでした。')

