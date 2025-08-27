"""
画像入出力処理モジュール
画像の読み込み、リサイズ、形式変換を担当
"""

import io
from typing import Optional, Tuple
from PIL import Image, ImageOps
import streamlit as st


def load_and_preprocess_image(uploaded_file) -> Optional[Image.Image]:
    """
    アップロードされた画像を読み込み、前処理を行う
    
    Args:
        uploaded_file: Streamlitのアップロードファイルオブジェクト
        
    Returns:
        前処理済みのPIL Imageオブジェクト、失敗時はNone
    """
    try:
        # 画像を読み込み
        image = Image.open(uploaded_file)
        
        # EXIF情報に基づいて自動回転
        image = ImageOps.exif_transpose(image)
        
        # RGBに変換（RGBA等の場合）
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # リサイズ（長辺2048px）
        image = resize_image(image, max_size=2048)
        
        return image
        
    except Exception as e:
        st.error(f"画像の読み込みに失敗しました: {str(e)}")
        return None


def resize_image(image: Image.Image, max_size: int = 2048) -> Image.Image:
    """
    画像を指定サイズ以下にリサイズ
    
    Args:
        image: PIL Imageオブジェクト
        max_size: 最大サイズ（長辺）
        
    Returns:
        リサイズされた画像
    """
    width, height = image.size
    
    if width <= max_size and height <= max_size:
        return image
    
    # アスペクト比を保持してリサイズ
    if width > height:
        new_width = max_size
        new_height = int(height * max_size / width)
    else:
        new_height = max_size
        new_width = int(width * max_size / height)
    
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)


def resize_image_for_display(image: Image.Image, target_width: int = None, target_height: int = None) -> Image.Image:
    """
    表示用に画像をリサイズ（レスポンシブ対応）
    
    Args:
        image: PIL Imageオブジェクト
        target_width: 目標幅（指定しない場合は自動計算）
        target_height: 目標高さ（指定しない場合は自動計算）
        
    Returns:
        リサイズされた画像
    """
    width, height = image.size
    
    # デフォルトの最大表示サイズ（画面サイズに応じて調整）
    max_display_width = 800
    max_display_height = 600
    
    # アスペクト比を保持してリサイズ
    if target_width and target_height:
        # 両方指定された場合は、アスペクト比を保持してフィット
        aspect_ratio = width / height
        target_aspect_ratio = target_width / target_height
        
        if aspect_ratio > target_aspect_ratio:
            # 幅に合わせる
            new_width = target_width
            new_height = int(target_width / aspect_ratio)
        else:
            # 高さに合わせる
            new_height = target_height
            new_width = int(target_height * aspect_ratio)
    elif target_width:
        # 幅のみ指定
        new_width = min(target_width, max_display_width)
        new_height = int(height * new_width / width)
    elif target_height:
        # 高さのみ指定
        new_height = min(target_height, max_display_height)
        new_width = int(width * new_height / height)
    else:
        # デフォルトサイズ
        if width > height:
            new_width = max_display_width
            new_height = int(height * max_display_width / width)
        else:
            new_height = max_display_height
            new_width = int(width * max_display_height / height)
    
    # 最小サイズの制限
    new_width = max(new_width, 100)
    new_height = max(new_height, 100)
    
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)


def image_to_bytes(image: Image.Image, format: str = 'JPEG') -> bytes:
    """
    画像をバイトデータに変換
    
    Args:
        image: PIL Imageオブジェクト
        format: 出力形式
        
    Returns:
        画像のバイトデータ
    """
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    return buffer.getvalue()


def get_image_info(image: Image.Image) -> dict:
    """
    画像の基本情報を取得
    
    Args:
        image: PIL Imageオブジェクト
        
    Returns:
        画像情報の辞書
    """
    return {
        'size': image.size,
        'mode': image.mode,
        'format': getattr(image, 'format', 'Unknown')
    }


def is_supported_format(filename: str) -> bool:
    """
    ファイル形式が対応しているかチェック
    
    Args:
        filename: ファイル名
        
    Returns:
        対応している場合はTrue
    """
    supported_formats = {'.png', '.jpg', '.jpeg', '.webp', '.heic', '.heif'}
    file_ext = filename.lower().split('.')[-1]
    return f'.{file_ext}' in supported_formats
