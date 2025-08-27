"""
Gemini API用プロンプトテンプレート
OCR処理用のプロンプトを管理
"""

import json
from typing import Dict, Any


def get_ocr_prompt() -> str:
    """
    OCR処理用のシステムプロンプトを取得
    
    Returns:
        OCR処理用プロンプト
    """
    return """あなたは高精度なOCRエンジンです。

画像からテキストを抽出し、以下の形式でJSONで返してください：

{
  "text": "抽出されたテキスト（改行・空白を適切に整理）",
  "language": "ISO639-1言語コード（ja, en, zh, ko等）"
}

注意事項：
- 改行や空白は適切に整理してください
- 文字の向きや傾きを自動補正してください
- 言語は自動判定し、ISO639-1コードで返してください
- 確信度が低い文字は「?」でマークしてください
- 表やリストは構造を保持してください
- 数式や特殊記号は正確に抽出してください

必ずJSON形式で返してください。"""


def get_user_prompt() -> str:
    """
    ユーザー向けプロンプトを取得
    
    Returns:
        ユーザー向けプロンプト
    """
    return "この画像からテキストを抽出してください。"


def parse_ocr_response(response_text: str) -> Dict[str, Any]:
    """
    OCR応答をパースする
    
    Args:
        response_text: Gemini APIからの応答テキスト
        
    Returns:
        パースされた結果辞書
    """
    try:
        # JSON部分を抽出
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("JSONが見つかりません")
        
        json_str = response_text[start_idx:end_idx]
        result = json.loads(json_str)
        
        # 必須フィールドの確認
        if 'text' not in result or 'language' not in result:
            raise ValueError("必須フィールドが不足しています")
        
        return {
            'text': result['text'],
            'language': result['language'],
            'success': True
        }
        
    except (json.JSONDecodeError, ValueError) as e:
        # JSONパース失敗時のフォールバック
        return {
            'text': response_text.strip(),
            'language': 'unknown',
            'success': False,
            'error': str(e)
        }


def get_error_prompt(error_type: str) -> str:
    """
    エラー時のプロンプトを取得
    
    Args:
        error_type: エラータイプ
        
    Returns:
        エラー用プロンプト
    """
    error_prompts = {
        'timeout': '処理がタイムアウトしました。画像サイズを小さくして再試行してください。',
        'api_error': 'APIエラーが発生しました。しばらく待ってから再試行してください。',
        'invalid_format': '対応していないファイル形式です。PNG、JPEG、WEBP形式をご利用ください。',
        'file_too_large': 'ファイルサイズが大きすぎます。20MB以下のファイルをご利用ください。',
        'no_text_found': 'テキストが見つかりませんでした。別の画像をお試しください。'
    }
    
    return error_prompts.get(error_type, '予期しないエラーが発生しました。')
