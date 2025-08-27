"""
OCR Web アプリケーション
Streamlit × Gemini APIを使用した画像テキスト抽出ツール
"""

import os
import streamlit as st
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

from src.ui import (
    setup_page_config,
    render_header,
    render_sidebar,
    render_upload_section,
    render_ocr_section,
    render_result_section,
    render_footer,
    render_gamification_section
)
from src.utils.feature_flags import is_feature_enabled, _get_feature_flags
from src.utils.monitoring import log_user_action, log_feature_usage, _get_monitoring


def main():
    """メインアプリケーション"""
    # ページ設定
    setup_page_config()
    
    # ヘッダー表示
    render_header()
    
    # サイドバー表示
    api_key, max_retries = render_sidebar()
    
    # 機能フラグと監視システムの初期化
    try:
        log_user_action("app_started", details={"version": "3.1.0"})
    except Exception as e:
        # 監視システムが利用できない場合は無視
        pass
    
    # メインコンテンツ
    try:
        # 画像アップロードセクション
        images = render_upload_section()
        
        if images:
            # OCR処理セクション
            results = render_ocr_section(images, api_key, max_retries)
            
            # 結果表示セクション
            if results:
                render_result_section(results)
        
        # ゲーミフィケーションセクション
        render_gamification_section()
        
        # 管理者パネルの表示（機能フラグが有効な場合）
        try:
            if is_feature_enabled("admin_panel"):
                with st.expander("🔧 管理者パネル"):
                    feature_flags = _get_feature_flags()
                    feature_flags.render_admin_panel()
                    monitoring = _get_monitoring()
                    monitoring.render_monitoring_dashboard()
        except Exception as e:
            # 管理者パネルが利用できない場合は無視
            pass
        
    except Exception as e:
        try:
            log_user_action("app_error", details={"error": str(e)})
        except Exception:
            pass  # 監視システムが利用できない場合は無視
        st.error(f"アプリケーションエラー: {str(e)}")
        st.exception(e)
    
    # フッター表示
    render_footer()


if __name__ == "__main__":
    main()
