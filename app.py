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

# テキスト正規化関数（修正版）
def normalize_text(text):
    text = unicodedata.normalize('NFKC', text)
    # unidecodeは日本語を削除してしまうので、英数字のみに適用
    # または、日本語を保持したい場合は使用しない
    # text = unidecode(text)  # この行をコメントアウト
    text = text.lower()
    # 日本語（ひらがな、カタカナ、漢字）、英数字、アンダースコアのみを残す
    text = re.sub(r'[^\w\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', '', text)
    # 空白文字も除去
    text = re.sub(r'\s+', '', text)
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
        st.success('完全一致しました！')
    elif similarity >= 0.8:
        st.info('高い類似度です。')
    elif similarity >= 0.5:
        st.warning('中程度の類似度です。')
    else:
        st.error('類似度が低いです。')