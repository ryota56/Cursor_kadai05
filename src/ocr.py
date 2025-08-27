"""
OCR処理モジュール
Gemini APIを使用した画像テキスト抽出機能
"""

import time
import logging
from typing import Optional, Dict, Any
import google.generativeai as genai
from PIL import Image
import streamlit as st

from .utils.prompts import get_ocr_prompt, get_user_prompt, parse_ocr_response


class OCRProcessor:
    """OCR処理クラス"""
    
    def __init__(self, api_key: str):
        """
        OCRProcessorの初期化
        
        Args:
            api_key: Gemini APIキー
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        # モデルの初期化
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # ログ設定
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def process_image(self, image: Image.Image, max_retries: int = 3) -> Dict[str, Any]:
        """
        画像のOCR処理を実行
        
        Args:
            image: 処理対象の画像
            max_retries: 最大リトライ回数
            
        Returns:
            OCR結果の辞書
        """
        start_time = time.time()
        
        try:
            # システムプロンプトとユーザープロンプトを設定
            system_prompt = get_ocr_prompt()
            user_prompt = get_user_prompt()
            
            # 画像をバイトデータに変換
            image_bytes = self._image_to_bytes(image)
            
            # ファイルサイズチェック
            if len(image_bytes) > 20 * 1024 * 1024:  # 20MB
                return self._handle_large_file(image, system_prompt, user_prompt)
            
            # インライン送信でOCR実行
            response = self._send_inline_request(image_bytes, system_prompt, user_prompt, max_retries)
            
            # 応答をパース
            result = parse_ocr_response(response.text)
            result['processing_time'] = time.time() - start_time
            
            return result
            
        except Exception as e:
            self.logger.error(f"OCR処理エラー: {str(e)}")
            return {
                'text': '',
                'language': 'unknown',
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def _image_to_bytes(self, image: Image.Image) -> bytes:
        """画像をバイトデータに変換"""
        import io
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=85)
        return buffer.getvalue()
    
    def _send_inline_request(self, image_bytes: bytes, system_prompt: str, 
                           user_prompt: str, max_retries: int) -> Any:
        """インライン送信でOCRリクエスト"""
        
        for attempt in range(max_retries):
            try:
                # 画像データを準備
                image_data = {
                    "mime_type": "image/jpeg",
                    "data": image_bytes
                }
                
                # リクエスト送信
                response = self.model.generate_content(
                    [system_prompt, user_prompt, image_data],
                    generation_config={
                        'temperature': 0.1,
                        'top_p': 0.8,
                        'top_k': 40,
                        'max_output_tokens': 4096,
                    }
                )
                
                return response
                
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指数バックオフ
                    self.logger.warning(f"リトライ {attempt + 1}/{max_retries}: {str(e)}")
                    time.sleep(wait_time)
                else:
                    raise e
    
    def _handle_large_file(self, image: Image.Image, system_prompt: str, 
                          user_prompt: str) -> Dict[str, Any]:
        """大きなファイルの処理（Files API使用）"""
        try:
            # 画像を一時的にリサイズ
            from .utils.image_io import resize_image
            resized_image = resize_image(image, max_size=1024)
            
            # リサイズした画像で処理
            image_bytes = self._image_to_bytes(resized_image)
            response = self._send_inline_request(image_bytes, system_prompt, user_prompt, 1)
            
            result = parse_ocr_response(response.text)
            result['note'] = '画像をリサイズして処理しました'
            
            return result
            
        except Exception as e:
            return {
                'text': '',
                'language': 'unknown',
                'success': False,
                'error': f'大きなファイルの処理に失敗: {str(e)}'
            }
    
    def get_supported_languages(self) -> Dict[str, str]:
        """対応言語の辞書を取得"""
        return {
            'ja': '日本語',
            'en': '英語',
            'zh': '中国語',
            'ko': '韓国語',
            'fr': 'フランス語',
            'de': 'ドイツ語',
            'es': 'スペイン語',
            'it': 'イタリア語',
            'pt': 'ポルトガル語',
            'ru': 'ロシア語'
        }
