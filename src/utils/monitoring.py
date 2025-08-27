"""
監視システム
アプリケーションのパフォーマンスとエラーを追跡
"""

import time
import json
import os
import streamlit as st
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import traceback


class MonitoringSystem:
    """監視システムクラス"""
    
    def __init__(self):
        self.log_file = "app_monitoring.log"
        self.metrics_file = "app_metrics.json"
        self.error_threshold = 5  # 5分間に5回以上のエラーでアラート
        self.performance_threshold = 3.0  # 3秒以上の処理時間でアラート
    
    def _init_session_state(self):
        """セッション状態を初期化"""
        if 'monitoring_data' not in st.session_state:
            st.session_state.monitoring_data = {
                'errors': [],
                'performance': [],
                'user_actions': [],
                'feature_usage': {}
            }
    
    def log_error(self, error: Exception, context: str = "", user_id: Optional[str] = None):
        """エラーをログに記録"""
        self._init_session_state()
        
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'user_id': user_id,
            'traceback': traceback.format_exc()
        }
        
        # セッション状態に追加
        st.session_state.monitoring_data['errors'].append(error_data)
        
        # ファイルに記録
        self._write_to_log(f"ERROR: {json.dumps(error_data, ensure_ascii=False)}")
        
        # アラートチェック
        self._check_error_threshold()
    
    def log_performance(self, operation: str, duration: float, context: str = ""):
        """パフォーマンスをログに記録"""
        self._init_session_state()
        
        perf_data = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'duration': duration,
            'context': context
        }
        
        # セッション状態に追加
        st.session_state.monitoring_data['performance'].append(perf_data)
        
        # ファイルに記録
        self._write_to_log(f"PERFORMANCE: {json.dumps(perf_data, ensure_ascii=False)}")
        
        # アラートチェック
        if duration > self.performance_threshold:
            self._log_performance_alert(operation, duration)
    
    def log_user_action(self, action: str, user_id: Optional[str] = None, details: Dict[str, Any] = None):
        """ユーザーアクションをログに記録"""
        self._init_session_state()
        
        action_data = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'user_id': user_id,
            'details': details or {}
        }
        
        # セッション状態に追加
        st.session_state.monitoring_data['user_actions'].append(action_data)
        
        # ファイルに記録
        self._write_to_log(f"USER_ACTION: {json.dumps(action_data, ensure_ascii=False)}")
    
    def log_feature_usage(self, feature_name: str, user_id: Optional[str] = None):
        """機能使用をログに記録"""
        self._init_session_state()
        
        if 'feature_usage' not in st.session_state.monitoring_data:
            st.session_state.monitoring_data['feature_usage'] = {}
        
        if feature_name not in st.session_state.monitoring_data['feature_usage']:
            st.session_state.monitoring_data['feature_usage'][feature_name] = {
                'count': 0,
                'users': set(),
                'last_used': None
            }
        
        feature_data = st.session_state.monitoring_data['feature_usage'][feature_name]
        feature_data['count'] += 1
        if user_id:
            feature_data['users'].add(user_id)
        feature_data['last_used'] = datetime.now().isoformat()
        
        # ファイルに記録
        usage_data = {
            'timestamp': datetime.now().isoformat(),
            'feature': feature_name,
            'user_id': user_id,
            'total_count': feature_data['count']
        }
        self._write_to_log(f"FEATURE_USAGE: {json.dumps(usage_data, ensure_ascii=False)}")
    
    def _write_to_log(self, message: str):
        """ログファイルに書き込み"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"{message}\n")
        except Exception as e:
            # ログ書き込みに失敗した場合のフォールバック
            print(f"Log write failed: {e}")
    
    def _check_error_threshold(self):
        """エラー閾値チェック"""
        self._init_session_state()
        
        recent_errors = [
            error for error in st.session_state.monitoring_data['errors']
            if datetime.fromisoformat(error['timestamp']) > datetime.now() - timedelta(minutes=5)
        ]
        
        if len(recent_errors) >= self.error_threshold:
            self._log_alert("ERROR_THRESHOLD", f"5分間に{len(recent_errors)}回のエラーが発生")
    
    def _log_performance_alert(self, operation: str, duration: float):
        """パフォーマンスアラートをログ"""
        self._log_alert("PERFORMANCE_ALERT", f"{operation}が{duration:.2f}秒で完了（閾値: {self.performance_threshold}秒）")
    
    def _log_alert(self, alert_type: str, message: str):
        """アラートをログ"""
        alert_data = {
            'timestamp': datetime.now().isoformat(),
            'alert_type': alert_type,
            'message': message
        }
        self._write_to_log(f"ALERT: {json.dumps(alert_data, ensure_ascii=False)}")
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """エラーサマリーを取得"""
        self._init_session_state()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_errors = [
            error for error in st.session_state.monitoring_data['errors']
            if datetime.fromisoformat(error['timestamp']) > cutoff_time
        ]
        
        error_types = {}
        for error in recent_errors:
            error_type = error['error_type']
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            'total_errors': len(recent_errors),
            'error_types': error_types,
            'recent_errors': recent_errors[-10:]  # 最新10件
        }
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """パフォーマンスサマリーを取得"""
        self._init_session_state()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_perf = [
            perf for perf in st.session_state.monitoring_data['performance']
            if datetime.fromisoformat(perf['timestamp']) > cutoff_time
        ]
        
        if not recent_perf:
            return {'total_operations': 0, 'avg_duration': 0, 'slow_operations': []}
        
        durations = [perf['duration'] for perf in recent_perf]
        slow_ops = [perf for perf in recent_perf if perf['duration'] > self.performance_threshold]
        
        return {
            'total_operations': len(recent_perf),
            'avg_duration': sum(durations) / len(durations),
            'max_duration': max(durations),
            'min_duration': min(durations),
            'slow_operations': slow_ops
        }
    
    def get_feature_usage_summary(self) -> Dict[str, Any]:
        """機能使用サマリーを取得"""
        self._init_session_state()
        
        feature_usage = st.session_state.monitoring_data.get('feature_usage', {})
        
        summary = {}
        for feature_name, usage_data in feature_usage.items():
            summary[feature_name] = {
                'total_usage': usage_data['count'],
                'unique_users': len(usage_data['users']),
                'last_used': usage_data['last_used']
            }
        
        return summary
    
    def render_monitoring_dashboard(self):
        """監視ダッシュボードを表示"""
        st.subheader("📊 監視ダッシュボード")
        
        # エラーサマリー
        error_summary = self.get_error_summary()
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("24時間のエラー数", error_summary['total_errors'])
            if error_summary['error_types']:
                st.write("**エラータイプ別**")
                for error_type, count in error_summary['error_types'].items():
                    st.write(f"- {error_type}: {count}回")
        
        with col2:
            if error_summary['recent_errors']:
                st.write("**最新エラー**")
                for error in error_summary['recent_errors'][-3:]:
                    st.error(f"{error['error_type']}: {error['error_message'][:50]}...")
        
        st.divider()
        
        # パフォーマンスサマリー
        perf_summary = self.get_performance_summary()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("総操作数", perf_summary['total_operations'])
        with col2:
            st.metric("平均処理時間", f"{perf_summary['avg_duration']:.2f}秒")
        with col3:
            st.metric("最大処理時間", f"{perf_summary['max_duration']:.2f}秒")
        
        if perf_summary['slow_operations']:
            st.warning(f"⚠️ {len(perf_summary['slow_operations'])}件の遅い操作を検出")
        
        st.divider()
        
        # 機能使用サマリー
        feature_summary = self.get_feature_usage_summary()
        if feature_summary:
            st.write("**機能使用状況**")
            for feature_name, usage in feature_summary.items():
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**{feature_name}**")
                with col2:
                    st.write(f"使用回数: {usage['total_usage']}")
                with col3:
                    st.write(f"ユーザー数: {usage['unique_users']}")
        
        # ログファイルダウンロード
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            st.download_button(
                label="📥 ログファイルをダウンロード",
                data=log_content,
                file_name="app_monitoring.log",
                mime="text/plain"
            )


# グローバルインスタンス（遅延初期化）
_monitoring_instance = None


def _get_monitoring():
    """監視システムインスタンスを取得（遅延初期化）"""
    global _monitoring_instance
    if _monitoring_instance is None:
        _monitoring_instance = MonitoringSystem()
    return _monitoring_instance


def log_error(error: Exception, context: str = "", user_id: Optional[str] = None):
    """エラーをログに記録（簡易関数）"""
    try:
        monitoring = _get_monitoring()
        monitoring.log_error(error, context, user_id)
    except Exception:
        # 監視システムが利用できない場合は無視
        pass


def log_performance(operation: str, duration: float, context: str = ""):
    """パフォーマンスをログに記録（簡易関数）"""
    try:
        monitoring = _get_monitoring()
        monitoring.log_performance(operation, duration, context)
    except Exception:
        # 監視システムが利用できない場合は無視
        pass


def log_user_action(action: str, user_id: Optional[str] = None, details: Dict[str, Any] = None):
    """ユーザーアクションをログに記録（簡易関数）"""
    try:
        monitoring = _get_monitoring()
        monitoring.log_user_action(action, user_id, details)
    except Exception:
        # 監視システムが利用できない場合は無視
        pass


def log_feature_usage(feature_name: str, user_id: Optional[str] = None):
    """機能使用をログに記録（簡易関数）"""
    try:
        monitoring = _get_monitoring()
        monitoring.log_feature_usage(feature_name, user_id)
    except Exception:
        # 監視システムが利用できない場合は無視
        pass


def performance_monitor(operation: str, context: str = ""):
    """パフォーマンス監視デコレータ"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                log_performance(operation, duration, context)
                return result
            except Exception as e:
                duration = time.time() - start_time
                log_performance(operation, duration, context)
                log_error(e, f"{operation} - {context}")
                raise
        return wrapper
    return decorator
