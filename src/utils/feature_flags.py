"""
機能フラグシステム
新機能の安全な制御と段階的ロールアウトを担当
"""

import os
import json
import streamlit as st
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta


class FeatureFlags:
    """機能フラグ管理クラス"""
    
    def __init__(self):
        self.flags_file = "feature_flags.json"
        self.flags = self._load_flags()
        self.user_preferences = self._load_user_preferences()
    
    def _load_flags(self) -> Dict[str, Any]:
        """機能フラグを読み込み"""
        default_flags = {
            "enhanced_design": {
                "enabled": False,
                "description": "Enhanced visual design features",
                "risk_level": "low",
                "phase": 2,
                "dependencies": []
            },
            "micro_interactions": {
                "enabled": False,
                "description": "Micro-interactions and animations",
                "risk_level": "medium",
                "phase": 3,
                "dependencies": ["enhanced_design"]
            },
            "gamification": {
                "enabled": False,
                "description": "Achievement and challenge system",
                "risk_level": "medium",
                "phase": 4,
                "dependencies": ["enhanced_design", "micro_interactions"]
            },
            "advanced_export": {
                "enabled": True,
                "description": "Advanced export features (CSV, Excel)",
                "risk_level": "low",
                "phase": 2,
                "dependencies": []
            },
            "pdf_support": {
                "enabled": True,
                "description": "PDF file processing support",
                "risk_level": "medium",
                "phase": 2,
                "dependencies": []
            },
            "responsive_design": {
                "enabled": True,
                "description": "Responsive design improvements",
                "risk_level": "low",
                "phase": 1,
                "dependencies": []
            },
            "security_enhancements": {
                "enabled": True,
                "description": "Security and validation features",
                "risk_level": "low",
                "phase": 1,
                "dependencies": []
            }
        }
        
        try:
            if os.path.exists(self.flags_file):
                with open(self.flags_file, 'r', encoding='utf-8') as f:
                    saved_flags = json.load(f)
                    # デフォルトフラグとマージ
                    for key, value in default_flags.items():
                        if key not in saved_flags:
                            saved_flags[key] = value
                    return saved_flags
            else:
                # 初回作成
                self._save_flags(default_flags)
                return default_flags
        except Exception as e:
            st.error(f"機能フラグの読み込みに失敗: {str(e)}")
            return default_flags
    
    def _save_flags(self, flags: Dict[str, Any]):
        """機能フラグを保存"""
        try:
            with open(self.flags_file, 'w', encoding='utf-8') as f:
                json.dump(flags, f, indent=2, ensure_ascii=False)
        except Exception as e:
            st.error(f"機能フラグの保存に失敗: {str(e)}")
    
    def _load_user_preferences(self) -> Dict[str, Any]:
        """ユーザー設定を読み込み"""
        try:
            if 'feature_preferences' not in st.session_state:
                st.session_state.feature_preferences = {}
            return st.session_state.feature_preferences
        except Exception:
            # Streamlitコンテキスト外での実行時は空の辞書を返す
            return {}
    
    def is_enabled(self, flag_name: str, user_id: Optional[str] = None) -> bool:
        """機能フラグが有効かチェック"""
        if flag_name not in self.flags:
            return False
        
        flag = self.flags[flag_name]
        
        # グローバル設定をチェック
        if not flag.get('enabled', False):
            return False
        
        # ユーザー設定をチェック
        if user_id and user_id in self.user_preferences:
            user_flags = self.user_preferences[user_id]
            if flag_name in user_flags:
                return user_flags[flag_name]
        
        # 環境変数でのオーバーライド
        env_flag = os.getenv(f"FEATURE_{flag_name.upper()}")
        if env_flag is not None:
            return env_flag.lower() in ['true', '1', 'yes', 'on']
        
        return flag.get('enabled', False)
    
    def enable_flag(self, flag_name: str, user_id: Optional[str] = None):
        """機能フラグを有効化"""
        if flag_name not in self.flags:
            try:
                st.error(f"不明な機能フラグ: {flag_name}")
            except Exception:
                print(f"不明な機能フラグ: {flag_name}")
            return
        
        if user_id:
            # ユーザー固有の設定
            if user_id not in self.user_preferences:
                self.user_preferences[user_id] = {}
            self.user_preferences[user_id][flag_name] = True
            try:
                st.session_state.feature_preferences = self.user_preferences
            except Exception:
                pass  # Streamlitコンテキスト外での実行時は無視
        else:
            # グローバル設定
            self.flags[flag_name]['enabled'] = True
            self._save_flags(self.flags)
    
    def disable_flag(self, flag_name: str, user_id: Optional[str] = None):
        """機能フラグを無効化"""
        if flag_name not in self.flags:
            try:
                st.error(f"不明な機能フラグ: {flag_name}")
            except Exception:
                print(f"不明な機能フラグ: {flag_name}")
            return
        
        if user_id:
            # ユーザー固有の設定
            if user_id not in self.user_preferences:
                self.user_preferences[user_id] = {}
            self.user_preferences[user_id][flag_name] = False
            try:
                st.session_state.feature_preferences = self.user_preferences
            except Exception:
                pass  # Streamlitコンテキスト外での実行時は無視
        else:
            # グローバル設定
            self.flags[flag_name]['enabled'] = False
            self._save_flags(self.flags)
    
    def get_flag_info(self, flag_name: str) -> Optional[Dict[str, Any]]:
        """機能フラグの情報を取得"""
        return self.flags.get(flag_name)
    
    def get_all_flags(self) -> Dict[str, Any]:
        """すべての機能フラグを取得"""
        return self.flags.copy()
    
    def get_enabled_flags(self) -> List[str]:
        """有効な機能フラグのリストを取得"""
        return [name for name, flag in self.flags.items() 
                if flag.get('enabled', False)]
    
    def check_dependencies(self, flag_name: str) -> List[str]:
        """依存関係をチェック"""
        if flag_name not in self.flags:
            return []
        
        flag = self.flags[flag_name]
        dependencies = flag.get('dependencies', [])
        missing_deps = []
        
        for dep in dependencies:
            if not self.is_enabled(dep):
                missing_deps.append(dep)
        
        return missing_deps
    
    def render_admin_panel(self):
        """管理者パネルを表示"""
        st.subheader("🔧 機能フラグ管理")
        
        # グローバル設定
        st.write("**グローバル設定**")
        for flag_name, flag_info in self.flags.items():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{flag_name}**")
                st.caption(flag_info.get('description', ''))
                st.write(f"リスクレベル: {flag_info.get('risk_level', 'unknown')}")
                st.write(f"フェーズ: {flag_info.get('phase', 'unknown')}")
            
            with col2:
                current_state = flag_info.get('enabled', False)
                if st.button(f"{'🟢 有効' if current_state else '🔴 無効'}", 
                           key=f"toggle_{flag_name}"):
                    if current_state:
                        self.disable_flag(flag_name)
                    else:
                        # 依存関係チェック
                        missing_deps = self.check_dependencies(flag_name)
                        if missing_deps:
                            st.error(f"依存関係が不足: {', '.join(missing_deps)}")
                        else:
                            self.enable_flag(flag_name)
                    st.rerun()
            
            with col3:
                if flag_info.get('dependencies'):
                    st.write(f"依存: {', '.join(flag_info['dependencies'])}")
            
            st.divider()
        
        # 統計情報
        st.subheader("📊 統計情報")
        enabled_count = len(self.get_enabled_flags())
        total_count = len(self.flags)
        st.metric("有効な機能", f"{enabled_count}/{total_count}")
        
        # エクスポート/インポート
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 設定をエクスポート"):
                st.download_button(
                    label="設定ファイルをダウンロード",
                    data=json.dumps(self.flags, indent=2, ensure_ascii=False),
                    file_name="feature_flags_backup.json",
                    mime="application/json"
                )
        
        with col2:
            uploaded_file = st.file_uploader(
                "設定ファイルをインポート",
                type=['json'],
                key="import_flags"
            )
            if uploaded_file:
                try:
                    imported_flags = json.load(uploaded_file)
                    self.flags.update(imported_flags)
                    self._save_flags(self.flags)
                    st.success("設定をインポートしました")
                    st.rerun()
                except Exception as e:
                    st.error(f"インポートに失敗: {str(e)}")


# グローバルインスタンス（遅延初期化）
_feature_flags_instance = None


def _get_feature_flags():
    """機能フラグインスタンスを取得（遅延初期化）"""
    global _feature_flags_instance
    if _feature_flags_instance is None:
        _feature_flags_instance = FeatureFlags()
    return _feature_flags_instance


def is_feature_enabled(flag_name: str, user_id: Optional[str] = None) -> bool:
    """機能フラグが有効かチェック（簡易関数）"""
    try:
        feature_flags = _get_feature_flags()
        return feature_flags.is_enabled(flag_name, user_id)
    except Exception:
        # 機能フラグシステムが利用できない場合はFalseを返す
        return False


def get_feature_info(flag_name: str) -> Optional[Dict[str, Any]]:
    """機能フラグの情報を取得（簡易関数）"""
    try:
        feature_flags = _get_feature_flags()
        return feature_flags.get_flag_info(flag_name)
    except Exception:
        # 機能フラグシステムが利用できない場合はNoneを返す
        return None
