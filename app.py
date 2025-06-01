import streamlit as st
from PIL import Image
import pytesseract
import unicodedata
import re
import Levenshtein

# テキスト正規化関数
def normalize_text(text):
    text = unicodedata.normalize('NFKC', text)
    text = text.lower()
    text = re.sub(r'\\s+', '', text)
    text = re.sub(r'[^\\wぁ-んァ-ン一-龥]', '', text)
    return text

# OCR抽出関数
def ocr_image(image):
    return pytesseract.image_to_string(image, lang='jpn+eng')

# 類似度計算
def calc_similarity(text1, text2):
    return 1 - Levenshtein.distance(text1, text2) / max(len(text1), len(text2), 1)

st.title('画像OCRテキスト比較アプリ')
st.write('2つの画像をアップロードし、OCRで抽出したテキストが一致するか判定します。')

img1 = st.file_uploader('画像1をアップロード', type=['png', 'jpg', 'jpeg'], key='img1')
img2 = st.file_uploader('画像2をアップロード', type=['png', 'jpg', 'jpeg'], key='img2')

if img1 and img2:
    image1 = Image.open(img1)
    image2 = Image.open(img2)
    st.image([image1, image2], caption=['画像1', '画像2'], width=200)
    text1 = ocr_image(image1)
    text2 = ocr_image(image2)
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    similarity = calc_similarity(norm1, norm2)
    st.subheader('OCR抽出テキスト（正規化前）')
    st.write('画像1:', text1)
    st.write('画像2:', text2)
    st.subheader('OCR抽出テキスト（正規化後）')
    st.write('画像1:', norm1)
    st.write('画像2:', norm2)
    st.subheader('一致判定')
    if similarity > 0.95:
        st.success(f'2つの画像のテキストは一致しています！（類似度: {similarity:.2f}）')
    else:
        st.warning(f'2つの画像のテキストは一致しません（類似度: {similarity:.2f}）')
