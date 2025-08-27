"""
Streamlit UIモジュール
ユーザーインターフェースの構築を担当
"""

import os
import streamlit as st
from typing import Optional, Dict, Any
from PIL import Image
import json
import io

from .utils.image_io import load_and_preprocess_image, get_image_info, is_supported_format, resize_image_for_display
from .utils.security import security_validator, validate_batch_upload
from .ocr import OCRProcessor
from .utils.feature_flags import is_feature_enabled
from .utils.gamification import update_stats, render_gamification_panel


def setup_page_config():
    """ページ設定を初期化"""
    st.set_page_config(
        page_title="OCR Web - 画像テキスト抽出",
        page_icon="📷",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 機能フラグに基づいてデザインを選択
    enhanced_design = is_feature_enabled("enhanced_design")
    
    if enhanced_design:
        # 新しいデザインシステム（フェーズ2 + フェーズ3 + フェーズ4）
        micro_interactions = is_feature_enabled("micro_interactions")
        gamification = is_feature_enabled("gamification")
        
        # フェーズ4: 季節テーマの適用
        seasonal_colors = {
            "primary": "#6366f1",
            "primary-hover": "#4f46e5",
            "secondary": "#f8fafc",
            "accent": "#06b6d4"
        }
        
        if gamification:
            try:
                from .utils.gamification import _get_gamification
                gamification_system = _get_gamification()
                current_theme = gamification_system.get_current_theme()
                if current_theme and 'colors' in current_theme and current_theme['colors']:
                    seasonal_colors.update(current_theme['colors'])
            except Exception:
                pass  # ゲーミフィケーションが利用できない場合はデフォルトカラーを使用
        
        # 季節テーマのCSSを適用
        css_content = f"""
        <style>
        /* 新しいカラーシステム（フェーズ4: 季節テーマ対応） */
        :root {{
            --primary-color: {seasonal_colors['primary']};
            --primary-hover: {seasonal_colors['primary-hover']};
            --secondary-color: {seasonal_colors['secondary']};
            --accent-color: {seasonal_colors['accent']};
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --error-color: #ef4444;
            --text-primary: #ffffff;
            --text-secondary: #e2e8f0;
            --border-color: #374151;
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.3);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.4);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.4);
            --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.4);
        }}
        """
        
        st.markdown(css_content, unsafe_allow_html=True)
        
        st.markdown("""
        <style>
        /* 新しいタイポグラフィ */
        .main .block-container {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--text-primary);
            background-color: #000000;
        }
        
        /* ページ全体の背景色設定 */
        .main {
            background-color: #000000;
        }
        
        .stApp {
            background-color: #000000;
        }
        
        /* サイドバーの背景色設定 */
        .css-1d391kg {
            background-color: #000000;
        }
        
        /* メインコンテンツエリアの背景色設定 */
        .main .block-container > div {
            background-color: #000000;
        }
        
        /* Streamlit基本要素のテキスト色統一 */
        .main p, .main div, .main span, .main label {
            color: var(--text-primary);
            background-color: #000000;
        }
        
        /* ダークテーマ対応のテキスト色調整 - 安全なアプローチ */
        @media (prefers-color-scheme: dark) {
            /* 基本的なテキスト色の確保 */
            .main h1, .main h2, .main h3 {
                color: #ffffff !important;
            }
            
            /* ファイルアップローダーの基本テキスト */
            .stFileUploader > div > div > div > div {
                color: #ffffff !important;
            }
            
            /* ファイル名とサイズのテキスト */
            .stFileUploader > div > div > div > div > div {
                color: #ffffff !important;
            }
            
            /* ファイル削除ボタン */
            .stFileUploader > div > div > div > div > div > button {
                color: #ffffff !important;
                background-color: rgba(239, 68, 68, 0.8) !important;
            }
            
            .stFileUploader > div > div > div > div > div > button:hover {
                background-color: rgba(239, 68, 68, 1) !important;
            }
            
            /* メトリクスのテキスト */
            .stMetric > div > div > div > div {
                color: #ffffff !important;
            }
            
            .stMetric > div > div > div > div > div {
                color: #ffffff !important;
            }
            
            /* プレースホルダーテキスト */
            .stTextArea > div > div > textarea::placeholder {
                color: #94a3b8 !important;
            }
            
            .stTextInput > div > div > input::placeholder {
                color: #94a3b8 !important;
            }
        }
        
        /* サイドバーのテキスト色 */
        .css-1d391kg {
            color: var(--text-primary);
        }
        
        /* ファイルアップローダーのテキスト色 */
        .stFileUploader p, .stFileUploader div, .stFileUploader span {
            color: var(--text-primary);
        }
        
        /* エクスパンダーのテキスト色 */
        .stExpander p, .stExpander div, .stExpander span {
            color: var(--text-primary);
        }
        
        /* ヘッダーとタイトルの改善 */
        .main h1 {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 1rem;
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .main h2 {
            font-size: 1.875rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.75rem;
        }
        
        .main h3 {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
        }
        
        /* ボタンの新しいデザイン（フェーズ3強化） */
        .stButton > button {
            background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
            border: none;
            border-radius: 12px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 14px;
            color: white;
            box-shadow: var(--shadow-sm);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            cursor: pointer;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: var(--shadow-xl);
            background: linear-gradient(135deg, var(--primary-hover), var(--primary-color));
        }
        
        .stButton > button:active {
            transform: translateY(-1px) scale(0.98);
            box-shadow: var(--shadow-md);
        }
        
        /* ボタンのリップル効果（フェーズ3強化） */
        .stButton > button::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.4);
            transform: translate(-50%, -50%);
            transition: width 0.4s ease-out, height 0.4s ease-out;
        }
        
        .stButton > button:active::before {
            width: 400px;
            height: 400px;
        }
        
        /* フェーズ3: マイクロインタラクション強化 */
        .stButton > button:focus {
            outline: 2px solid var(--primary-color);
            outline-offset: 2px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4); }
            50% { box-shadow: 0 0 0 10px rgba(99, 102, 241, 0); }
        }
        
        /* カードデザイン（フェーズ3強化） */
        .stExpander {
            background: rgba(0, 0, 0, 0.95);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            box-shadow: var(--shadow-sm);
            margin-bottom: 1rem;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
        }
        
        .stExpander:hover {
            box-shadow: var(--shadow-lg);
            transform: translateY(-2px);
            border-color: var(--primary-color);
        }
        
        .stExpander:active {
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }
        
        /* エクスパンダーヘッダーの改善（フェーズ3） */
        .stExpander > div > div > div > div {
            transition: all 0.3s ease;
            cursor: pointer;
            color: var(--text-primary);
        }
        
        .stExpander > div > div > div > div:hover {
            background: rgba(0, 0, 0, 0.95);
            color: var(--text-primary);
        }
        
        /* ダークテーマでのホバー効果調整 - 安全なアプローチ */
        @media (prefers-color-scheme: dark) {
            /* ファイルアップローダーのホバー効果 */
            .stFileUploader > div > div:hover {
                border-color: var(--primary-color);
                box-shadow: var(--shadow-md);
            }
            
            /* ボタンのホバー効果 */
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: var(--shadow-lg);
            }
        }
        
        /* タブの改善（フェーズ3強化） */
        .stTabs > div > div > div > div > div {
            background: rgba(0, 0, 0, 0.9);
            border-radius: 8px 8px 0 0;
            border: 1px solid var(--border-color);
            border-bottom: none;
            padding: 8px 16px;
            font-weight: 500;
            color: var(--text-primary);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
        }
        
        .stTabs > div > div > div > div > div:hover {
            background: rgba(99, 102, 241, 0.2);
            transform: translateY(-1px);
            color: var(--text-primary);
        }
        
        .stTabs > div > div > div > div > div[aria-selected="true"] {
            background: var(--primary-color);
            color: white;
            border-color: var(--primary-color);
            transform: translateY(-1px);
            box-shadow: var(--shadow-sm);
        }
        
        /* ファイルアップローダーの改善（フェーズ3強化） */
        .stFileUploader > div > div {
            border: 2px dashed var(--border-color);
            border-radius: 12px;
            background: rgba(0, 0, 0, 0.9);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            color: var(--text-primary);
        }
        
        .stFileUploader > div > div:hover {
            border-color: var(--primary-color);
            background: rgba(99, 102, 241, 0.1);
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
            color: var(--text-primary);
        }
        
        .stFileUploader > div > div:active {
            transform: translateY(0);
            box-shadow: var(--shadow-sm);
        }
        
        /* ファイルアップローダーのドラッグ効果（フェーズ3） */
        .stFileUploader > div > div.dragover {
            border-color: var(--success-color);
            background: rgba(16, 185, 129, 0.1);
            transform: scale(1.02);
        }
        
        /* テキストエリアの改善（フェーズ3強化） */
        .stTextArea > div > div > textarea {
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 12px;
            font-size: 14px;
            line-height: 1.6;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            background: #1a1a1a;
            color: var(--text-primary);
        }
        
        .stTextArea > div > div > textarea:hover {
            border-color: var(--primary-color);
            box-shadow: var(--shadow-sm);
        }
        
        .stTextArea > div > div > textarea:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
            outline: none;
            transform: translateY(-1px);
        }
        
        /* ダークテーマでのフォーカス効果調整 - 安全なアプローチ */
        @media (prefers-color-scheme: dark) {
            /* フォーカス効果の強化 */
            .stTextArea > div > div > textarea:focus {
                border-color: var(--primary-color);
                box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.3);
            }
            
            .stSelectbox > div > div > select:focus {
                border-color: var(--primary-color);
                box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.3);
            }
            
            .stTextInput > div > div > input:focus {
                border-color: var(--primary-color);
                box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.3);
            }
        }
        
        /* セレクトボックスの改善（フェーズ3強化） */
        .stSelectbox > div > div > select {
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            background: #1a1a1a;
            color: var(--text-primary);
            cursor: pointer;
        }
        
        .stSelectbox > div > div > select:hover {
            border-color: var(--primary-color);
            box-shadow: var(--shadow-sm);
        }
        
        .stSelectbox > div > div > select:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
            outline: none;
            transform: translateY(-1px);
        }
        
        /* テキスト入力フィールドの改善（フェーズ3） */
        .stTextInput > div > div > input {
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            background: #1a1a1a;
            color: var(--text-primary);
        }
        
        .stTextInput > div > div > input:hover {
            border-color: var(--primary-color);
            box-shadow: var(--shadow-sm);
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
            outline: none;
            transform: translateY(-1px);
        }
        
        /* スライダーの改善 */
        .stSlider > div > div > div > div {
            background: var(--primary-color);
            border-radius: 4px;
        }
        
        .stSlider > div > div > div > div > div {
            background: var(--primary-color);
            border-radius: 50%;
            box-shadow: var(--shadow-sm);
        }
        
        /* メトリクスの改善（フェーズ3強化） */
        .stMetric > div > div > div {
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
            color: white;
            padding: 16px;
            border-radius: 12px;
            box-shadow: var(--shadow-sm);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .stMetric > div > div > div:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }
        
        .stMetric > div > div > div::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s;
        }
        
        .stMetric > div > div > div:hover::before {
            left: 100%;
        }
        
        /* 重複したタブスタイルを削除 - 上記で統合済み */
        
        /* アラートの改善 */
        .stAlert {
            border-radius: 12px;
            border: none;
            padding: 16px;
            margin: 1rem 0;
            box-shadow: var(--shadow-sm);
        }
        
        .stAlert[data-baseweb="notification"] {
            border-left: 4px solid var(--success-color);
        }
        
        /* ローディングスピナーの改善（フェーズ3強化） */
        .stSpinner > div {
            border: 3px solid var(--border-color);
            border-top: 3px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            box-shadow: var(--shadow-sm);
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* フェーズ3: 高度なローディング状態 */
        .loading-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            background: linear-gradient(135deg, #1a1a1a, #000000);
            border-radius: 16px;
            box-shadow: var(--shadow-sm);
            animation: fadeInUp 0.6s ease-out;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* プログレスバーの改善（フェーズ3） */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
            border-radius: 4px;
            box-shadow: var(--shadow-sm);
        }
        
        /* スケルトンローディング（フェーズ3） */
        .skeleton {
            background: linear-gradient(90deg, var(--border-color) 25%, var(--secondary-color) 50%, var(--border-color) 75%);
            background-size: 200% 100%;
            animation: skeleton-loading 1.5s infinite;
            border-radius: 4px;
        }
        
        @keyframes skeleton-loading {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        
        /* レスポンシブデザインの改善 */
        @media (max-width: 768px) {
            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                max-width: 100%;
            }
            
            .main h1 {
                font-size: 2rem;
            }
            
            .main h2 {
                font-size: 1.5rem;
            }
            
            .stButton > button {
                width: 100%;
                min-height: 48px;
                font-size: 16px;
            }
        }
        
        /* 画像のレスポンシブ対応強化 */
        .stImage > img {
            max-width: 100% !important;
            height: auto !important;
            object-fit: contain;
            border-radius: 8px;
            box-shadow: var(--shadow-sm);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .stImage > img:hover {
            transform: scale(1.02);
            box-shadow: var(--shadow-md);
        }
        
        /* 画像コンテナのレスポンシブ対応 */
        .stImage {
            width: 100% !important;
            max-width: 100% !important;
            overflow: hidden;
            border-radius: 8px;
            background: rgba(0, 0, 0, 0.1);
        }
        
        /* モバイルでの画像表示最適化 */
        @media (max-width: 768px) {
            .stImage > img {
                max-width: 100% !important;
                width: 100% !important;
                height: auto !important;
                object-fit: contain;
            }
            
            .stImage {
                width: 100% !important;
                max-width: 100% !important;
                margin: 0 auto;
            }
        }
        
        /* タブレットでの画像表示最適化 */
        @media (min-width: 769px) and (max-width: 1024px) {
            .stImage > img {
                max-width: 100% !important;
                height: auto !important;
                object-fit: contain;
            }
        }
        
        /* デスクトップでの画像表示最適化 */
        @media (min-width: 1025px) {
            .stImage > img {
                max-width: 100% !important;
                height: auto !important;
                object-fit: contain;
            }
        }
        
        /* アニメーション（フェーズ3強化） */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .main .block-container > div {
            animation: fadeIn 0.6s ease-out;
        }
        
        /* フェーズ3: 高度なアニメーション効果 */
        @keyframes bounce {
            0%, 20%, 53%, 80%, 100% { transform: translate3d(0,0,0); }
            40%, 43% { transform: translate3d(0,-8px,0); }
            70% { transform: translate3d(0,-4px,0); }
            90% { transform: translate3d(0,-2px,0); }
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            10%, 30%, 50%, 70%, 90% { transform: translateX(-2px); }
            20%, 40%, 60%, 80% { transform: translateX(2px); }
        }
        
        /* 成功時のアニメーション */
        .success-animation {
            animation: bounce 0.6s ease-out;
        }
        
        /* エラー時のアニメーション */
        .error-animation {
            animation: shake 0.5s ease-in-out;
        }
        
        /* フェーズ4: ゲーミフィケーションアニメーション */
        @keyframes achievement-unlock {
            0% { transform: scale(0) rotate(0deg); opacity: 0; }
            50% { transform: scale(1.2) rotate(180deg); opacity: 1; }
            100% { transform: scale(1) rotate(360deg); opacity: 1; }
        }
        
        @keyframes level-up {
            0% { transform: translateY(0) scale(1); }
            50% { transform: translateY(-20px) scale(1.1); }
            100% { transform: translateY(0) scale(1); }
        }
        
        @keyframes challenge-complete {
            0% { transform: scale(1); }
            25% { transform: scale(1.1); }
            50% { transform: scale(0.9); }
            75% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .achievement-unlock {
            animation: achievement-unlock 1s ease-out;
        }
        
        .level-up {
            animation: level-up 0.8s ease-out;
        }
        
        .challenge-complete {
            animation: challenge-complete 0.6s ease-out;
        }
        
        /* フェーズ4: ゲーミフィケーション要素のスタイル */
        .gamification-panel {
            background: linear-gradient(135deg, #1a1a1a, #000000);
            border-radius: 16px;
            padding: 1rem;
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border-color);
        }
        
        /* 画像の動的リサイズ対応 */
        .responsive-image-container {
            position: relative;
            width: 100%;
            max-width: 100%;
            overflow: hidden;
            border-radius: 8px;
            background: rgba(0, 0, 0, 0.1);
        }
        
        .responsive-image-container img {
            width: 100% !important;
            height: auto !important;
            max-width: 100% !important;
            object-fit: contain;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .responsive-image-container img:hover {
            transform: scale(1.02);
        }
        
        /* 画像のズーム機能 */
        .image-zoom-container {
            position: relative;
            overflow: hidden;
            border-radius: 8px;
            cursor: zoom-in;
        }
        
        .image-zoom-container img {
            transition: transform 0.3s ease;
        }
        
        .image-zoom-container:hover img {
            transform: scale(1.1);
        }
        
        /* ダークテーマでのゲーミフィケーション要素調整 - 安全なアプローチ */
        @media (prefers-color-scheme: dark) {
            .gamification-panel {
                background: linear-gradient(135deg, #1a1a1a, #000000);
                border-color: var(--border-color);
                color: var(--text-primary);
            }
            
            .achievement-card {
                background: #1a1a1a;
                border-color: var(--border-color);
                color: var(--text-primary);
            }
            
            .challenge-card {
                background: #1a1a1a;
                border-color: var(--border-color);
                color: var(--text-primary);
            }
            
            .stats-card {
                background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
                color: #ffffff;
            }
        }
        
        .achievement-card {
            background: #1a1a1a;
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            box-shadow: var(--shadow-sm);
            border-left: 4px solid var(--primary-color);
            transition: all 0.3s ease;
        }
        
        .achievement-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }
        
        .achievement-card.unlocked {
            border-left-color: var(--success-color);
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), #1a1a1a);
        }
        
        .challenge-card {
            background: #1a1a1a;
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            box-shadow: var(--shadow-sm);
            border-left: 4px solid var(--warning-color);
            transition: all 0.3s ease;
        }
        
        .challenge-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }
        
        .challenge-card.completed {
            border-left-color: var(--success-color);
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), #1a1a1a);
        }
        
        .stats-card {
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
            color: white;
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            box-shadow: var(--shadow-md);
            text-align: center;
        }
        
        .level-indicator {
            background: linear-gradient(135deg, var(--warning-color), var(--accent-color));
            color: white;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            font-weight: bold;
            margin: 0 auto;
            box-shadow: var(--shadow-lg);
        }
        
        /* ホバー効果の改善 */
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }
        
        /* フォーカス状態の改善 */
        .stButton > button:focus {
            outline: 2px solid var(--primary-color);
            outline-offset: 2px;
        }
        
        /* カスタムスクロールバー */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #1a1a1a;
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-secondary);
        }
        
        /* コピーボタンのレスポンシブ対応強化 */
        .copy-button-container {
            margin: 10px 0;
            width: 100%;
        }
        
        .copy-button-container button {
            width: 100% !important;
            min-width: 200px !important;
            max-width: 400px !important;
            padding: 12px 16px !important;
            background: linear-gradient(135deg, #4CAF50, #45a049) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            cursor: pointer !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
            display: block !important;
            margin: 0 auto !important;
        }
        
        .copy-button-container button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
        }
        
        .copy-button-container button:active {
            transform: translateY(0) !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        }
        
        /* モバイルでのコピーボタン最適化 */
        @media (max-width: 768px) {
            .copy-button-container button {
                min-width: 150px !important;
                font-size: 13px !important;
                padding: 10px 12px !important;
            }
        }
        
        /* タブレットでのコピーボタン最適化 */
        @media (min-width: 769px) and (max-width: 1024px) {
            .copy-button-container button {
                min-width: 180px !important;
                font-size: 14px !important;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # フェーズ3: マイクロインタラクション用JavaScript
        if micro_interactions:
            st.markdown("""
            <script>
            // フェーズ3: マイクロインタラクション機能
            
            // ページ読み込み時のアニメーション
            document.addEventListener('DOMContentLoaded', function() {
                // 要素のフェードインアニメーション
                const elements = document.querySelectorAll('.stButton, .stExpander, .stMetric');
                elements.forEach((element, index) => {
                    element.style.opacity = '0';
                    element.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        element.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
                        element.style.opacity = '1';
                        element.style.transform = 'translateY(0)';
                    }, index * 100);
                });
                
                // ボタンクリック時のリップル効果
                document.addEventListener('click', function(e) {
                    if (e.target.tagName === 'BUTTON') {
                        const ripple = document.createElement('span');
                        const rect = e.target.getBoundingClientRect();
                        const size = Math.max(rect.width, rect.height);
                        const x = e.clientX - rect.left - size / 2;
                        const y = e.clientY - rect.top - size / 2;
                        
                        ripple.style.width = ripple.style.height = size + 'px';
                        ripple.style.left = x + 'px';
                        ripple.style.top = y + 'px';
                        ripple.classList.add('ripple');
                        
                        e.target.appendChild(ripple);
                        
                        setTimeout(() => {
                            ripple.remove();
                        }, 600);
                    }
                });
                
                // ファイルアップローダーのドラッグ効果
                const fileUploaders = document.querySelectorAll('.stFileUploader > div > div');
                fileUploaders.forEach(uploader => {
                    uploader.addEventListener('dragover', function(e) {
                        e.preventDefault();
                        this.classList.add('dragover');
                    });
                    
                    uploader.addEventListener('dragleave', function(e) {
                        e.preventDefault();
                        this.classList.remove('dragover');
                    });
                    
                    uploader.addEventListener('drop', function(e) {
                        e.preventDefault();
                        this.classList.remove('dragover');
                        this.classList.add('success-animation');
                        setTimeout(() => {
                            this.classList.remove('success-animation');
                        }, 600);
                    });
                });
                
                // フォーム要素のフォーカス効果
                const formElements = document.querySelectorAll('input, textarea, select');
                formElements.forEach(element => {
                    element.addEventListener('focus', function() {
                        this.parentElement.style.transform = 'translateY(-1px)';
                    });
                    
                    element.addEventListener('blur', function() {
                        this.parentElement.style.transform = 'translateY(0)';
                    });
                });
                
                // 成功・エラーメッセージのアニメーション
                const observer = new MutationObserver(function(mutations) {
                    mutations.forEach(function(mutation) {
                        mutation.addedNodes.forEach(function(node) {
                            if (node.nodeType === 1) { // Element node
                                if (node.classList && node.classList.contains('stAlert')) {
                                    if (node.textContent.includes('成功') || node.textContent.includes('完了')) {
                                        node.classList.add('success-animation');
                                    } else if (node.textContent.includes('エラー') || node.textContent.includes('失敗')) {
                                        node.classList.add('error-animation');
                                    }
                                }
                            }
                        });
                    });
                });
                
                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });
                
                // 画像の動的リサイズ機能
                setupResponsiveImages();
                
                // 動的に追加される画像にも対応
                const imageObserver = new MutationObserver(function(mutations) {
                    mutations.forEach(function(mutation) {
                        mutation.addedNodes.forEach(function(node) {
                            if (node.nodeType === 1 && node.classList && node.classList.contains('stImage')) {
                                const img = node.querySelector('img');
                                if (img) {
                                    img.onload = function() {
                                        resizeImageToFit(img);
                                    };
                                    if (img.complete) {
                                        resizeImageToFit(img);
                                    }
                                }
                            }
                        });
                    });
                });
                
                imageObserver.observe(document.body, {
                    childList: true,
                    subtree: true
                });
            });
            
            // 画像の動的リサイズ機能
            function setupResponsiveImages() {
                const images = document.querySelectorAll('.stImage img');
                
                images.forEach(img => {
                    // 画像の読み込み完了時にリサイズ
                    img.onload = function() {
                        resizeImageToFit(img);
                    };
                    
                    // 既に読み込み済みの場合は即座にリサイズ
                    if (img.complete) {
                        resizeImageToFit(img);
                    }
                    
                    // ウィンドウリサイズ時に再リサイズ
                    window.addEventListener('resize', function() {
                        resizeImageToFit(img);
                    });
                });
            }
            
            function resizeImageToFit(img) {
                const container = img.closest('.stImage') || img.parentElement;
                if (!container) return;
                
                const containerWidth = container.offsetWidth;
                const containerHeight = container.offsetHeight;
                const imgWidth = img.naturalWidth;
                const imgHeight = img.naturalHeight;
                
                // アスペクト比を保持してリサイズ
                const aspectRatio = imgWidth / imgHeight;
                const containerAspectRatio = containerWidth / containerHeight;
                
                let newWidth, newHeight;
                
                if (aspectRatio > containerAspectRatio) {
                    // 幅に合わせる
                    newWidth = containerWidth;
                    newHeight = containerWidth / aspectRatio;
                } else {
                    // 高さに合わせる
                    newHeight = containerHeight;
                    newWidth = containerHeight * aspectRatio;
                }
                
                // 最小サイズの制限
                newWidth = Math.max(newWidth, 100);
                newHeight = Math.max(newHeight, 100);
                
                img.style.width = newWidth + 'px';
                img.style.height = newHeight + 'px';
                img.style.maxWidth = '100%';
                img.style.maxHeight = '100%';
                img.style.objectFit = 'contain';
            }
            
            // リップル効果のCSS
            const style = document.createElement('style');
            style.textContent = `
                .ripple {
                    position: absolute;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.6);
                    transform: scale(0);
                    animation: ripple-animation 0.6s linear;
                    pointer-events: none;
                }
                
                @keyframes ripple-animation {
                    to {
                        transform: scale(4);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
            </script>
            """, unsafe_allow_html=True)
    else:
        # 従来のデザインシステム
        st.markdown("""
        <style>
        /* モバイルファーストのレスポンシブデザイン */
        @media (max-width: 768px) {
            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                max-width: 100%;
                background-color: #000000;
                color: #ffffff;
            }
            
            .stButton > button {
                width: 100%;
                min-height: 44px;
                font-size: 16px;
            }
            
            .stTextArea > div > div > textarea {
                font-size: 16px;
                background-color: #1a1a1a;
                color: #ffffff;
            }
            
            .stSelectbox > div > div > select {
                font-size: 16px;
                background-color: #1a1a1a;
                color: #ffffff;
            }
            
            .stSlider > div > div > div > div {
                min-height: 44px;
            }
            
            .stFileUploader > div > div > div > div {
                min-height: 44px;
            }
            
            .stMetric > div > div > div {
                font-size: 14px;
            }
            
            .stTabs > div > div > div > div > div {
                font-size: 14px;
            }
        }
        
        /* タブレット対応 */
        @media (min-width: 769px) and (max-width: 1024px) {
            .main .block-container {
                padding-left: 2rem;
                padding-right: 2rem;
            }
            
            .stButton > button {
                min-height: 40px;
                font-size: 15px;
            }
        }
        
        /* デスクトップ最適化 */
        @media (min-width: 1025px) {
            .main .block-container {
                padding-left: 3rem;
                padding-right: 3rem;
            }
        }
        
        /* タッチフレンドリーな要素 */
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: all 0.2s ease;
        }
        
        /* 画像のレスポンシブ対応（従来デザイン） */
        .stImage > img {
            max-width: 100% !important;
            height: auto !important;
            object-fit: contain;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        
        .stImage > img:hover {
            transform: scale(1.02);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        /* 画像コンテナのレスポンシブ対応（従来デザイン） */
        .stImage {
            width: 100% !important;
            max-width: 100% !important;
            overflow: hidden;
            border-radius: 8px;
            background: rgba(0, 0, 0, 0.05);
        }
        
        /* モバイルでの画像表示最適化（従来デザイン） */
        @media (max-width: 768px) {
            .stImage > img {
                max-width: 100% !important;
                width: 100% !important;
                height: auto !important;
                object-fit: contain;
            }
            
            .stImage {
                width: 100% !important;
                max-width: 100% !important;
                margin: 0 auto;
            }
        }
        
        /* アクセシビリティ改善 */
        .stButton > button:focus {
            outline: 2px solid #4CAF50;
            outline-offset: 2px;
        }
        
        /* ローディング状態の改善 */
        .stSpinner > div {
            border-width: 3px;
        }
        
        /* エラー表示の改善 */
        .stAlert {
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        /* 成功表示の改善 */
        .stAlert[data-baseweb="notification"] {
            border-radius: 8px;
            border-left: 4px solid;
        }
        </style>
        """, unsafe_allow_html=True)


def render_header():
    """ヘッダーを表示"""
    st.title("📷 OCR Web - 画像テキスト抽出")
    st.markdown("画像をアップロードして、Gemini APIでテキストを抽出します")
    st.divider()


def render_sidebar():
    """サイドバーを表示"""
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # APIキー設定（環境変数/Secretsからのみ読み込み）
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            api_key = st.secrets.get("GEMINI_API_KEY", "")
        
        # APIキーの状態表示
        if api_key:
            if api_key == "your-api-key-here":
                st.error("⚠️ プレースホルダーのAPIキーが設定されています。実際のAPIキーに変更してください。")
            else:
                st.success("✅ APIキーが設定されています")
        else:
            st.error("❌ APIキーが設定されていません")
            st.markdown("""
            **Streamlit Cloud Secrets設定が必要です**:
            
            1. Streamlit Cloud Dashboard にアクセス
            2. アプリの Settings → Secrets を開く
            3. 以下を追加:
            ```
            GEMINI_API_KEY = "実際のAPIキー"
            ```
            """)
        
        # APIキーの検証
        if api_key and api_key != "your-api-key-here":
            if st.button("🔍 APIキーを検証", use_container_width=True):
                with st.spinner("APIキーを検証中..."):
                    try:
                        import google.generativeai as genai
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-2.0-flash-exp')
                        response = model.generate_content("Hello")
                        st.success("✅ APIキーが有効です")
                    except Exception as e:
                        st.error(f"❌ APIキーが無効です: {str(e)}")
        elif api_key == "your-api-key-here":
            st.warning("⚠️ プレースホルダーのAPIキーが設定されています。実際のAPIキーに変更してください。")
        
        # 処理オプション
        st.subheader("処理オプション")
        max_retries = st.slider("最大リトライ回数", 1, 5, 3, help="OCR処理が失敗した場合の最大リトライ回数を設定します")
        
        # 現在の値をメトリクス形式で表示
        col1, col2 = st.columns(2)
        with col1:
            st.metric("最大リトライ回数", f"{max_retries}回")
        with col2:
            st.metric("推奨設定", "3回", delta="標準")
        
        # ヘルプ
        with st.expander("ℹ️ ヘルプ"):
            st.markdown("""
            **APIキー設定方法**:
            1. [Google AI Studio](https://aistudio.google.com/) でAPIキーを取得
            2. Streamlit Cloud Secrets または環境変数 `GEMINI_API_KEY` に設定
            
            **Streamlit Cloud Secrets 設定**:
            1. Streamlit Cloud Dashboard → アプリ → Settings → Secrets
            2. 以下を追加:
            ```
            GEMINI_API_KEY = "実際のAPIキー"
            ```
            
            **APIキー取得手順**:
            1. https://aistudio.google.com/ にアクセス
            2. Googleアカウントでログイン
            3. 「Get API key」をクリック
            4. 新しいAPIキーを作成または既存のキーを選択
            5. コピーしたAPIキーをStreamlit Cloud Secretsに設定
            
            **対応形式**: PNG, JPEG, WEBP, HEIC/HEIF
            
            **制限事項**:
            - ファイルサイズ: 最大20MB
            - 処理時間: 最大60秒
            - 画像サイズ: 自動リサイズ（長辺2048px）
            
            **使用方法**:
            1. 画像ファイルをアップロード
            2. 「OCR実行」ボタンをクリック
            3. 結果を編集・コピー・保存
            """)
        
        return api_key, max_retries


def render_upload_section() -> Optional[list]:
    """アップロードセクションを表示"""
    st.header("📤 画像アップロード")
    
    uploaded_files = st.file_uploader(
        "画像ファイルを選択してください",
        type=['png', 'jpg', 'jpeg', 'webp', 'heic', 'heif'],
        accept_multiple_files=True,
        help="対応形式: PNG, JPEG, WEBP, HEIC/HEIF（複数選択可能）"
    )
    
    if uploaded_files is not None and len(uploaded_files) > 0:
        # セキュリティ検証
        validation_results = validate_batch_upload(uploaded_files)
        
        if validation_results['errors']:
            for error in validation_results['errors']:
                st.error(error)
        
        if validation_results['invalid_files']:
            for invalid_file in validation_results['invalid_files']:
                st.warning(f"{invalid_file['file'].name}: {invalid_file['error']}")
        
        valid_files = validation_results['valid_files']
        
        if not valid_files:
            st.error("処理可能なファイルがありません")
            return None
        
        # 複数画像の処理
        images = []
        image_infos = []
        
        # スケルトンローディング表示
        loading_placeholder = st.empty()
        with loading_placeholder.container():
            st.markdown("🔄 画像を読み込み中...")
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        for i, uploaded_file in enumerate(valid_files):
            status_text.text(f"画像 {i+1}/{len(valid_files)} を処理中...")
            
            # 画像読み込みと前処理
            image = load_and_preprocess_image(uploaded_file)
            if image:
                images.append(image)
                image_infos.append({
                    'name': uploaded_file.name,
                    'info': get_image_info(image)
                })
            
            # 進捗更新
            progress_bar.progress((i + 1) / len(valid_files))
        
        # ローディング表示をクリア
        loading_placeholder.empty()
        
        if images:
            # 複数画像のプレビュー表示
            st.subheader("プレビュー")
            
            if len(images) == 1:
                # 単一画像の従来表示
                info = image_infos[0]['info']
                
                # レスポンシブレイアウト
                cols = st.columns([1, 1, 1])
                
                with cols[0]:
                    st.metric("サイズ", f"{info['size'][0]} × {info['size'][1]}")
                with cols[1]:
                    st.metric("形式", info['format'])
                with cols[2]:
                    st.metric("モード", info['mode'])
                
                # 画像表示（レスポンシブ対応強化）
                st.image(
                    images[0], 
                    caption=image_infos[0]['name'], 
                    use_container_width=True,
                    clamp=True
                )
            else:
                # 複数画像のタブ表示
                tabs = st.tabs([f"画像 {i+1}: {info['name']}" for i, info in enumerate(image_infos)])
                
                for i, (tab, image, info) in enumerate(zip(tabs, images, image_infos)):
                    with tab:
                        # レスポンシブレイアウト
                        cols = st.columns([1, 1, 1])
                        
                        with cols[0]:
                            st.metric("サイズ", f"{info['info']['size'][0]} × {info['info']['size'][1]}")
                        with cols[1]:
                            st.metric("形式", info['info']['format'])
                        with cols[2]:
                            st.metric("モード", info['info']['mode'])
                        
                        # 画像表示（レスポンシブ対応強化）
                        st.image(
                            image, 
                            caption=info['name'], 
                            use_container_width=True,
                            clamp=True
                        )
            
            # セッション状態に画像情報を保存
            st.session_state.uploaded_images = images
            st.session_state.image_infos = image_infos
            
            return images
    
    return None


def render_ocr_section(images: list, api_key: str, max_retries: int):
    """OCR処理セクションを表示"""
    st.header("🔍 OCR処理")
    
    if not api_key:
        st.error("APIキーが設定されていません")
        return None
    
    if st.button("🚀 OCR実行", type="primary", use_container_width=True):
        if not images:
            st.error("処理する画像がありません")
            return None
        
        # レート制限チェック
        if not security_validator.check_rate_limit():
            st.error("リクエストが多すぎます。しばらく待ってから再試行してください。")
            return None
        
        # 複数画像の処理
        results = []
        failed_images = []
        
        # 進捗バーの表示
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            processor = OCRProcessor(api_key)
            
            for i, image in enumerate(images):
                status_text.text(f"画像 {i+1}/{len(images)} を処理中...")
                
                try:
                    result = processor.process_image(image, max_retries)
                    results.append(result)
                    
                    # 進捗更新
                    progress_bar.progress((i + 1) / len(images))
                    
                except Exception as e:
                    failed_images.append(i + 1)
                    results.append({
                        'text': '',
                        'language': 'unknown',
                        'success': False,
                        'error': str(e),
                        'processing_time': 0
                    })
                    st.warning(f"画像 {i+1} の処理に失敗: {str(e)}")
            
            # 処理完了
            progress_bar.empty()
            status_text.empty()
            
            # 結果をセッション状態に保存
            st.session_state.ocr_results = results
            st.session_state.processor = processor
            
            # 成功・失敗の統計
            successful_count = sum(1 for r in results if r.get('success'))
            total_count = len(results)
            
            if successful_count == total_count:
                st.success(f"全{total_count}枚の処理が完了しました！")
            elif successful_count > 0:
                st.success(f"{successful_count}/{total_count}枚の処理が完了しました")
                if failed_images:
                    st.warning(f"画像 {', '.join(map(str, failed_images))} の処理に失敗しました")
            else:
                st.error("すべての画像の処理に失敗しました")
            
            # フェーズ4: ゲーミフィケーション統計更新
            gamification_enabled = is_feature_enabled("gamification")
            if gamification_enabled:
                try:
                    # 統計データを収集
                    total_chars = sum(len(r.get('text', '')) for r in results if r.get('success'))
                    total_time = sum(r.get('processing_time', 0) for r in results)
                    languages = set(r.get('language', 'unknown') for r in results if r.get('success'))
                    file_types = set()
                    
                    # ファイルタイプを収集（画像情報から）
                    if hasattr(st.session_state, 'image_infos'):
                        for info in st.session_state.image_infos:
                            if 'info' in info and 'format' in info['info']:
                                file_types.add(info['info']['format'].lower())
                    
                    # ゲーミフィケーション統計を更新
                    update_stats("ocr_completed", 
                               images_processed=total_count,
                               text_length=total_chars,
                               processing_time=total_time,
                               languages=languages,
                               batch_size=total_count,
                               file_types=file_types)
                except Exception:
                    pass  # ゲーミフィケーションが利用できない場合は無視
            
        except Exception as e:
            st.error(f"OCR処理に失敗しました: {str(e)}")
            return None
    
    return st.session_state.get('ocr_results')


def render_result_section(results: list):
    """結果表示セクションを表示"""
    if not results:
        return
    
    st.header("📝 抽出結果")
    
    # 複数結果の比較表示
    if len(results) > 1:
        st.subheader("📊 処理結果サマリー")
        comparison_data = []
        for i, result in enumerate(results):
            comparison_data.append({
                "画像": f"画像 {i+1}",
                "文字数": len(result.get('text', '')),
                "言語": result.get('language', 'unknown'),
                "処理時間": f"{result.get('processing_time', 0):.2f}秒",
                "ステータス": "✅ 成功" if result.get('success') else "❌ 失敗"
            })
        st.dataframe(comparison_data, use_container_width=True)
    
    # 結果の詳細表示
    if len(results) == 1:
        # 単一結果の従来表示
        result = results[0]
        render_single_result(result)
    else:
        # 複数結果のタブ表示
        tabs = st.tabs([f"結果 {i+1}" for i in range(len(results))])
        
        for i, (tab, result) in enumerate(zip(tabs, results)):
            with tab:
                render_single_result(result, i)
    
    # 一括操作ボタン
    if len(results) > 1:
        st.subheader("📦 一括操作")
        col1, col2 = st.columns(2)
        
        with col1:
            # 1回のクリックでZIPダウンロードを実行
            zip_data = create_zip_data(results)
            if zip_data:
                st.download_button(
                    label="📥 全結果をZIPでダウンロード",
                    data=zip_data,
                    file_name="ocr_results.zip",
                    use_container_width=True
                )
            else:
                st.warning("ZIPファイルを作成できませんでした")
        
        with col2:
            if st.button("📋 全テキストをコピー", use_container_width=True):
                all_text = "\n\n".join([f"=== 画像 {i+1} ===\n{r.get('text', '')}" 
                                       for i, r in enumerate(results) if r.get('success')])
                
                if all_text.strip():
                    # セッション状態で全テキストコピー表示を管理
                    st.session_state["copy_all_text"] = all_text
                    st.session_state["show_copy_all"] = True
                    st.success("✅ 全テキストのコピー準備が完了しました！")
                    st.rerun()
                else:
                    st.warning("コピーするテキストがありません")
        
        # 全テキストコピー表示（セッション状態で管理）
        if st.session_state.get("show_copy_all", False):
            st.subheader("📋 全テキストコピー")
            
            # テキストエリアを表示
            st.text_area(
                "全テキスト（コピー用）",
                value=st.session_state.get("copy_all_text", ""),
                height=250,
                key="copy_all_area",
                help="全テキストを選択してコピーしてください"
            )
            
            # コピーボタンを別途表示（レスポンシブ対応）
            all_text = st.session_state.get("copy_all_text", "")
            safe_all_text = all_text.replace('"', '\\"').replace('\n', '\\n')
            copy_all_button_html = f"""
            <div class="copy-button-container">
                <button onclick="copyAllText()">
                    📋 全テキストワンクリックコピー
                </button>
            </div>
            <script>
            async function copyAllText() {{
                const text = "{safe_all_text}";
                
                // モダンなClipboard APIを試行
                if (navigator.clipboard && window.isSecureContext) {{
                    try {{
                        await navigator.clipboard.writeText(text);
                        alert('✅ 全テキストがクリップボードにコピーされました！');
                        return;
                    }} catch (err) {{
                        console.log('Clipboard API failed, trying fallback...');
                    }}
                }}
                
                // フォールバック: 古い方法
                try {{
                    const textArea = document.createElement('textarea');
                    textArea.value = text;
                    textArea.style.position = 'fixed';
                    textArea.style.left = '-999999px';
                    textArea.style.top = '-999999px';
                    document.body.appendChild(textArea);
                    textArea.focus();
                    textArea.select();
                    
                    const successful = document.execCommand('copy');
                    document.body.removeChild(textArea);
                    
                    if (successful) {{
                        alert('✅ 全テキストがクリップボードにコピーされました！');
                    }} else {{
                        alert('❌ 全テキストのコピーに失敗しました。手動でコピーしてください。');
                    }}
                }} catch (err) {{
                    alert('❌ 全テキストのコピーに失敗しました。手動でコピーしてください。');
                }}
            }}
            </script>
            """
            
            st.components.v1.html(copy_all_button_html, height=70)
            
            st.info("💡 上記のテキストエリアから全テキストを選択して Ctrl+C (Mac: Cmd+C) でコピーしてください")
            
            # ダウンロードオプション
            st.download_button(
                label="📥 ダウンロード",
                data=st.session_state.get("copy_all_text", ""),
                file_name="all_ocr_results.txt",
                mime="text/plain",
                key="download_all_text",
                use_container_width=True
            )
        
        # 全テキストコピー方法の詳細説明
        with st.expander("📋 全テキストコピー方法の詳細説明"):
            st.markdown("""
            **最も確実なコピー方法**:
            1. **📋 全テキストワンクリックコピー**ボタンをクリック
            2. ブラウザのアラートでコピー成功を確認
            3. 他のアプリでペースト（Ctrl+V）
            
            **注意**: 
            - モダンなClipboard APIとフォールバック機能を使用しています
            - HTTPS環境では最新のAPI、HTTP環境では従来のAPIを使用します
            - コピー成功時はブラウザのアラートで通知されます
            """)
        



def render_single_result(result: Dict[str, Any], index: int = 0):
    """単一結果の表示"""
    # 言語情報表示
    if result.get('success'):
        language = result.get('language', 'unknown')
        processor = st.session_state.get('processor')
        if processor:
            languages = processor.get_supported_languages()
            language_name = languages.get(language, language)
            st.info(f"検出言語: {language_name} ({language})")
    
    # テキスト表示・編集（サニタイゼーション適用）
    text_content = result.get('text', '')
    sanitized_text = security_validator.sanitize_input(text_content)
    
    # 編集可能なテキストエリア
    edited_text = st.text_area(
        f"抽出されたテキスト (画像 {index + 1})" if index > 0 else "抽出されたテキスト",
        value=sanitized_text,
        height=300,
        help="テキストを編集できます"
    )
    
    # 操作ボタン
    if st.button(f"📋 コピー", key=f"copy_{index}", use_container_width=True):
        # コピー機能を呼び出し（画像インデックスを渡す）
        copy_to_clipboard(edited_text, f"copy_success_{index}", index + 1)
    
    # エラー情報表示
    if not result.get('success'):
        st.error(f"エラー: {result.get('error', '不明なエラー')}")
    
    # 注意事項表示
    if 'note' in result:
        st.warning(result['note'])


def create_zip_data(results: list) -> bytes:
    """全結果のZIPデータを作成"""
    if not results:
        return None
    
    try:
        import zipfile
        import io
        
        # 成功した結果のみをフィルタリング
        successful_results = [r for r in results if r.get('success') and r.get('text', '').strip()]
        
        if not successful_results:
            return None
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for i, result in enumerate(successful_results):
                text = result.get('text', '')
                file_data = text.encode('utf-8')
                file_name = f"ocr_result_{i + 1}.txt"
                zip_file.writestr(file_name, file_data)
            
            # サマリーファイルも追加
            summary_data = create_summary_file(results)
            zip_file.writestr(f"summary.txt", summary_data)
        
        # ZIPファイルのサイズを確認
        zip_size = len(zip_buffer.getvalue())
        if zip_size == 0:
            return None
        
        return zip_buffer.getvalue()
        
    except Exception as e:
        st.error(f"ZIPファイル作成に失敗しました: {str(e)}")
        return None


def save_all_results(results: list):
    """全結果をZIPファイルで一括保存（後方互換性）"""
    zip_data = create_zip_data(results)
    if zip_data:
        st.download_button(
            label="📥 全結果をZIPでダウンロード",
            data=zip_data,
            file_name="ocr_results.zip",
            use_container_width=True
        )
    else:
        st.warning("ZIPファイルを作成できませんでした")


def create_summary_file(results: list) -> bytes:
    """結果サマリーファイルを作成"""
    summary_lines = []
    summary_lines.append("OCR処理結果サマリー")
    summary_lines.append("=" * 30)
    summary_lines.append("")
    
    for i, result in enumerate(results):
        summary_lines.append(f"画像 {i + 1}:")
        summary_lines.append(f"  ステータス: {'成功' if result.get('success') else '失敗'}")
        summary_lines.append(f"  言語: {result.get('language', 'unknown')}")
        summary_lines.append(f"  文字数: {len(result.get('text', ''))}")
        summary_lines.append(f"  処理時間: {result.get('processing_time', 0):.2f}秒")
        if not result.get('success'):
            summary_lines.append(f"  エラー: {result.get('error', '不明なエラー')}")
        summary_lines.append("")
    
    summary_text = "\n".join(summary_lines)
    return summary_text.encode('utf-8')


def clear_session_state():
    """セッション状態をクリア"""
    # 既存の単一結果
    if 'ocr_result' in st.session_state:
        del st.session_state.ocr_result
    
    # 新しい複数結果
    if 'ocr_results' in st.session_state:
        del st.session_state.ocr_results
    if 'uploaded_images' in st.session_state:
        del st.session_state.uploaded_images
    if 'image_infos' in st.session_state:
        del st.session_state.image_infos
    
    # プロセッサー
    if 'processor' in st.session_state:
        del st.session_state.processor
    
    # コピー関連のセッション状態をクリア
    copy_keys = [key for key in st.session_state.keys() if key.startswith(('copy_text_', 'show_copy_', 'copy_all_text', 'show_copy_all'))]
    for key in copy_keys:
        del st.session_state[key]


def copy_to_clipboard(text: str, success_key: str, image_index: int = 1):
    """テキストをコピー用に表示（モダンなClipboard API版）"""
    if not text.strip():
        st.warning("コピーするテキストがありません")
        return
    
    # ユニークなキーを生成（タイムスタンプを含める）
    import time
    timestamp = int(time.time() * 1000)  # ミリ秒単位のタイムスタンプ
    unique_key = f"{success_key}_{timestamp}"
    
    # セッション状態でコピー表示を管理
    copy_display_key = f"show_copy_{unique_key}"
    
    # プレーンテキストとして表示
    display_text = text
    
    # テキストエリアを表示
    st.text_area(
        "コピー対象テキスト",
        value=display_text,
        height=200,
        key=f"copy_area_{unique_key}",
        help="テキストを選択してコピーしてください"
    )
    
    # コピーボタンを別途表示（レスポンシブ対応）
    safe_text = display_text.replace('"', '\\"').replace('\n', '\\n')
    copy_button_html = f"""
    <div class="copy-button-container">
        <button onclick="copyText_{unique_key}()">
            📋 ワンクリックコピー
        </button>
    </div>
    <script>
    async function copyText_{unique_key}() {{
        const text = "{safe_text}";
        
        // モダンなClipboard APIを試行
        if (navigator.clipboard && window.isSecureContext) {{
            try {{
                await navigator.clipboard.writeText(text);
                alert('✅ テキストがクリップボードにコピーされました！');
                return;
            }} catch (err) {{
                console.log('Clipboard API failed, trying fallback...');
            }}
        }}
        
        // フォールバック: 古い方法
        try {{
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            const successful = document.execCommand('copy');
            document.body.removeChild(textArea);
            
            if (successful) {{
                alert('✅ テキストがクリップボードにコピーされました！');
            }} else {{
                alert('❌ コピーに失敗しました。手動でコピーしてください。');
            }}
        }} catch (err) {{
            alert('❌ コピーに失敗しました。手動でコピーしてください。');
        }}
    }}
    </script>
    """
    
    st.components.v1.html(copy_button_html, height=70)
    
    # ダウンロードオプション
    st.download_button(
        label="📥 ダウンロード",
        data=display_text,
        file_name=f"ocr_result_{image_index}.txt",
        mime="text/plain",
        key=f"download_{unique_key}",
        use_container_width=True
    )
    
    # コピー方法の詳細説明
    with st.expander("📋 コピー方法の詳細説明"):
        st.markdown("""
        **最も確実なコピー方法**:
        1. **📋 ワンクリックコピー**ボタンをクリック
        2. ブラウザのアラートでコピー成功を確認
        3. 他のアプリでペースト（Ctrl+V）
        
        **注意**: 
        - モダンなClipboard APIとフォールバック機能を使用しています
        - HTTPS環境では最新のAPI、HTTP環境では従来のAPIを使用します
        - コピー成功時はブラウザのアラートで通知されます
        """)


def render_footer():
    """フッターを表示"""
    st.divider()
    st.markdown(
        "---\n"
        "**OCR Web** - Powered by Streamlit & Gemini API\n"
        "© 2024 - 画像テキスト抽出ツール"
    )


def render_gamification_section():
    """ゲーミフィケーションセクションを表示"""
    gamification = is_feature_enabled("gamification")
    
    if gamification:
        try:
            render_gamification_panel()
        except Exception:
            pass  # ゲーミフィケーションが利用できない場合は無視
