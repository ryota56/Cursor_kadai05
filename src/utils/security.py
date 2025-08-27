"""
セキュリティ機能モジュール
ファイルアップロードのセキュリティ検証と入力サニタイゼーションを担当
"""

import os
import hashlib
import mimetypes
import time
import re
from typing import Optional, Dict, Any, List
import streamlit as st
from PIL import Image
import io


class SecurityValidator:
    """セキュリティ検証クラス"""
    
    def __init__(self):
        """セキュリティ設定の初期化"""
        # ファイルサイズ制限（20MB）
        self.max_file_size = 20 * 1024 * 1024
        
        # 許可されたファイル形式
        self.allowed_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.heic', '.heif'}
        
        # 許可されたMIMEタイプ
        self.allowed_mime_types = {
            'image/png', 'image/jpeg', 'image/webp', 'image/heic', 'image/heif'
        }
        
        # 危険なファイルパターン
        self.dangerous_patterns = [
            '..', '\\', '/', 'script', 'javascript', 'vbscript', 'data:'
        ]
        
        # レート制限設定
        self.rate_limit_requests = 10  # 1分間に許可されるリクエスト数
        self.rate_limit_window = 60    # 秒単位のウィンドウ
    
    def validate_file_upload(self, uploaded_file) -> Dict[str, Any]:
        """
        ファイルアップロードのセキュリティ検証
        
        Args:
            uploaded_file: Streamlitのアップロードファイルオブジェクト
            
        Returns:
            検証結果の辞書
        """
        result = {
            'valid': False,
            'error': None,
            'file_info': {}
        }
        
        try:
            # ファイル名の検証
            if not self._validate_filename(uploaded_file.name):
                result['error'] = "無効なファイル名です"
                return result
            
            # ファイルサイズの検証
            if uploaded_file.size > self.max_file_size:
                result['error'] = f"ファイルサイズが制限（{self.max_file_size // (1024*1024)}MB）を超過しています"
                return result
            
            # ファイル拡張子の検証
            if not self._validate_extension(uploaded_file.name):
                result['error'] = "対応していないファイル形式です"
                return result
            
            # MIMEタイプの検証
            if not self._validate_mime_type(uploaded_file):
                result['error'] = "無効なファイルタイプです"
                return result
            
            # ファイル内容の検証
            if not self._validate_file_content(uploaded_file):
                result['error'] = "ファイル内容が無効です"
                return result
            
            # ファイル情報を収集
            result['file_info'] = {
                'name': uploaded_file.name,
                'size': uploaded_file.size,
                'type': uploaded_file.type,
                'hash': self._calculate_file_hash(uploaded_file)
            }
            
            result['valid'] = True
            
        except Exception as e:
            result['error'] = f"ファイル検証中にエラーが発生しました: {str(e)}"
        
        return result
    
    def _validate_filename(self, filename: str) -> bool:
        """ファイル名の検証"""
        if not filename or len(filename) > 255:
            return False
        
        # 危険なパターンのチェック
        filename_lower = filename.lower()
        for pattern in self.dangerous_patterns:
            if pattern in filename_lower:
                return False
        
        return True
    
    def _validate_extension(self, filename: str) -> bool:
        """ファイル拡張子の検証"""
        file_ext = os.path.splitext(filename.lower())[1]
        return file_ext in self.allowed_extensions
    
    def _validate_mime_type(self, uploaded_file) -> bool:
        """MIMEタイプの検証"""
        # ファイルの先頭バイトを読み取ってMIMEタイプを判定
        try:
            uploaded_file.seek(0)
            header = uploaded_file.read(512)
            uploaded_file.seek(0)
            
            # 画像ファイルのマジックナンバーをチェック
            if header.startswith(b'\xff\xd8\xff'):  # JPEG
                return True
            elif header.startswith(b'\x89PNG\r\n\x1a\n'):  # PNG
                return True
            elif header.startswith(b'RIFF') and b'WEBP' in header[:20]:  # WEBP
                return True
            elif header.startswith(b'\x00\x00\x00\x20ftypheic'):  # HEIC
                return True
            elif header.startswith(b'\x00\x00\x00\x20ftypheif'):  # HEIF
                return True
            
            return False
            
        except Exception:
            return False
    
    def _validate_file_content(self, uploaded_file) -> bool:
        """ファイル内容の検証"""
        try:
            uploaded_file.seek(0)
            
            # PILで画像として開けるかテスト
            image = Image.open(uploaded_file)
            image.verify()  # 画像の整合性をチェック
            
            uploaded_file.seek(0)
            return True
            
        except Exception:
            return False
    
    def _calculate_file_hash(self, uploaded_file) -> str:
        """ファイルのハッシュ値を計算"""
        try:
            uploaded_file.seek(0)
            file_content = uploaded_file.read()
            uploaded_file.seek(0)
            
            return hashlib.sha256(file_content).hexdigest()
            
        except Exception:
            return ""
    
    def sanitize_input(self, text: str) -> str:
        """
        テキスト入力のサニタイゼーション
        
        Args:
            text: サニタイズするテキスト
            
        Returns:
            サニタイズされたテキスト
        """
        if not text:
            return ""
        
        # HTMLエスケープ
        import html
        sanitized = html.escape(text)
        
        # 改行文字の正規化
        sanitized = sanitized.replace('\r\n', '\n').replace('\r', '\n')
        
        # 連続する改行を制限
        sanitized = re.sub(r'\n{3,}', '\n\n', sanitized)
        
        return sanitized
    
    def check_rate_limit(self, user_id: str = "default") -> bool:
        """
        レート制限のチェック
        
        Args:
            user_id: ユーザーID（セッション識別子）
            
        Returns:
            リクエストが許可される場合はTrue
        """
        current_time = st.session_state.get('rate_limit_time', 0)
        request_count = st.session_state.get('rate_limit_count', 0)
        
        # 時間ウィンドウのリセット
        if current_time + self.rate_limit_window < time.time():
            st.session_state.rate_limit_time = time.time()
            st.session_state.rate_limit_count = 1
            return True
        
        # リクエスト数のチェック
        if request_count >= self.rate_limit_requests:
            return False
        
        # リクエスト数を増加
        st.session_state.rate_limit_count = request_count + 1
        return True


def validate_batch_upload(files: List) -> Dict[str, Any]:
    """
    バッチアップロードの検証
    
    Args:
        files: アップロードされたファイルのリスト
        
    Returns:
        検証結果の辞書
    """
    validator = SecurityValidator()
    results = {
        'valid_files': [],
        'invalid_files': [],
        'total_size': 0,
        'errors': []
    }
    
    # ファイル数の制限
    if len(files) > 50:  # 最大50ファイル
        results['errors'].append("ファイル数が制限（50個）を超過しています")
        return results
    
    for file in files:
        validation_result = validator.validate_file_upload(file)
        
        if validation_result['valid']:
            results['valid_files'].append(file)
            results['total_size'] += file.size
        else:
            results['invalid_files'].append({
                'file': file,
                'error': validation_result['error']
            })
    
    # 合計サイズの制限
    max_total_size = 100 * 1024 * 1024  # 100MB
    if results['total_size'] > max_total_size:
        results['errors'].append(f"合計ファイルサイズが制限（{max_total_size // (1024*1024)}MB）を超過しています")
    
    return results


# グローバルなセキュリティバリデーターインスタンス
security_validator = SecurityValidator()
