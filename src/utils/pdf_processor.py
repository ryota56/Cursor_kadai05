"""
PDF処理モジュール
PDFファイルの画像変換とテキスト抽出を担当
"""

import os
import io
from typing import List, Optional, Dict, Any
from PIL import Image
import streamlit as st

try:
    from pdf2image import convert_from_bytes
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False


class PDFProcessor:
    """PDF処理クラス"""
    
    def __init__(self):
        """PDFProcessorの初期化"""
        self.supported_formats = {'.pdf'}
        self.max_pages = 50  # 最大ページ数制限
        self.max_file_size = 50 * 1024 * 1024  # 50MB制限
    
    def is_supported_format(self, filename: str) -> bool:
        """PDF形式が対応しているかチェック"""
        file_ext = os.path.splitext(filename.lower())[1]
        return file_ext in self.supported_formats
    
    def validate_pdf_file(self, uploaded_file) -> Dict[str, Any]:
        """
        PDFファイルの検証
        
        Args:
            uploaded_file: Streamlitのアップロードファイルオブジェクト
            
        Returns:
            検証結果の辞書
        """
        result = {
            'valid': False,
            'error': None,
            'info': {}
        }
        
        try:
            # ファイルサイズチェック
            if uploaded_file.size > self.max_file_size:
                result['error'] = f"PDFファイルサイズが制限（{self.max_file_size // (1024*1024)}MB）を超過しています"
                return result
            
            # ファイル名チェック
            if not self.is_supported_format(uploaded_file.name):
                result['error'] = "対応していないファイル形式です"
                return result
            
            # PDF内容の検証
            if not self._validate_pdf_content(uploaded_file):
                result['error'] = "無効なPDFファイルです"
                return result
            
            # PDF情報の取得
            pdf_info = self._get_pdf_info(uploaded_file)
            if pdf_info:
                result['info'] = pdf_info
                result['valid'] = True
            else:
                result['error'] = "PDF情報の取得に失敗しました"
            
        except Exception as e:
            result['error'] = f"PDF検証中にエラーが発生しました: {str(e)}"
        
        return result
    
    def _validate_pdf_content(self, uploaded_file) -> bool:
        """PDF内容の検証"""
        try:
            uploaded_file.seek(0)
            header = uploaded_file.read(1024)
            uploaded_file.seek(0)
            
            # PDFマジックナンバーのチェック
            return header.startswith(b'%PDF')
            
        except Exception:
            return False
    
    def _get_pdf_info(self, uploaded_file) -> Optional[Dict[str, Any]]:
        """PDF情報の取得"""
        if not PYPDF2_AVAILABLE:
            return None
        
        try:
            uploaded_file.seek(0)
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            
            info = {
                'pages': len(pdf_reader.pages),
                'title': '',
                'author': '',
                'subject': '',
                'creator': ''
            }
            
            # メタデータの取得
            if pdf_reader.metadata:
                info['title'] = pdf_reader.metadata.get('/Title', '')
                info['author'] = pdf_reader.metadata.get('/Author', '')
                info['subject'] = pdf_reader.metadata.get('/Subject', '')
                info['creator'] = pdf_reader.metadata.get('/Creator', '')
            
            uploaded_file.seek(0)
            return info
            
        except Exception:
            return None
    
    def convert_pdf_to_images(self, uploaded_file, max_pages: Optional[int] = None) -> List[Image.Image]:
        """
        PDFを画像に変換
        
        Args:
            uploaded_file: PDFファイル
            max_pages: 変換する最大ページ数（Noneの場合は全ページ）
            
        Returns:
            画像のリスト
        """
        if not PDF2IMAGE_AVAILABLE:
            st.error("PDF2Imageライブラリがインストールされていません。PDF機能を使用するには 'pip install pdf2image' を実行してください。")
            return []
        
        try:
            uploaded_file.seek(0)
            pdf_bytes = uploaded_file.read()
            uploaded_file.seek(0)
            
            # ページ数の制限
            if max_pages is None:
                max_pages = self.max_pages
            
            # PDFを画像に変換
            images = convert_from_bytes(
                pdf_bytes,
                dpi=200,  # 解像度
                first_page=1,
                last_page=max_pages,
                fmt='JPEG',
                thread_count=1  # スレッド数を制限
            )
            
            # 画像の前処理
            processed_images = []
            for i, image in enumerate(images):
                # RGBに変換
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # リサイズ（長辺2048px）
                image = self._resize_image(image, max_size=2048)
                
                processed_images.append(image)
            
            return processed_images
            
        except Exception as e:
            st.error(f"PDF変換に失敗しました: {str(e)}")
            return []
    
    def _resize_image(self, image: Image.Image, max_size: int = 2048) -> Image.Image:
        """画像のリサイズ"""
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
    
    def extract_text_from_pdf(self, uploaded_file) -> Optional[str]:
        """
        PDFからテキストを抽出（PyPDF2使用）
        
        Args:
            uploaded_file: PDFファイル
            
        Returns:
            抽出されたテキスト
        """
        if not PYPDF2_AVAILABLE:
            return None
        
        try:
            uploaded_file.seek(0)
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            uploaded_file.seek(0)
            
            text_parts = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            return '\n\n'.join(text_parts)
            
        except Exception as e:
            st.error(f"PDFテキスト抽出に失敗しました: {str(e)}")
            return None


# グローバルなPDFプロセッサーインスタンス
pdf_processor = PDFProcessor()
