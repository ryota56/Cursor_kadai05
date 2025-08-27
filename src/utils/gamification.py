"""
ゲーミフィケーション機能モジュール
実績システム、チャレンジ、季節テーマを管理
"""

import streamlit as st
import json
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import random


@dataclass
class Achievement:
    """実績データクラス"""
    id: str
    name: str
    description: str
    icon: str
    category: str
    unlocked: bool = False
    unlocked_date: Optional[str] = None
    progress: int = 0
    max_progress: int = 1
    rarity: str = "common"  # common, rare, epic, legendary


@dataclass
class Challenge:
    """チャレンジデータクラス"""
    id: str
    name: str
    description: str
    icon: str
    category: str
    completed: bool = False
    completed_date: Optional[str] = None
    progress: int = 0
    max_progress: int = 1
    reward_points: int = 10
    daily: bool = False
    weekly: bool = False


@dataclass
class UserStats:
    """ユーザー統計データクラス"""
    total_images_processed: int = 0
    total_characters_extracted: int = 0
    total_processing_time: float = 0.0
    successful_ocr_count: int = 0
    failed_ocr_count: int = 0
    consecutive_days: int = 0
    last_activity_date: Optional[str] = None
    total_points: int = 0
    level: int = 1
    experience: int = 0


class GamificationSystem:
    """ゲーミフィケーションシステム"""
    
    def __init__(self):
        self._init_session_state()
        self.achievements = self._load_achievements()
        self.challenges = self._load_challenges()
        self.seasonal_themes = self._load_seasonal_themes()
    
    def _init_session_state(self):
        """セッション状態を初期化"""
        if 'gamification_data' not in st.session_state:
            st.session_state.gamification_data = {
                'user_stats': asdict(UserStats()),
                'achievements': {},
                'challenges': {},
                'unlocked_achievements': [],
                'completed_challenges': [],
                'current_theme': 'default'
            }
    
    def _load_achievements(self) -> Dict[str, Achievement]:
        """実績データを読み込み"""
        achievements_data = {
            # 基本実績
            "first_ocr": Achievement(
                id="first_ocr",
                name="初回OCR",
                description="初めての画像テキスト抽出を完了",
                icon="🎯",
                category="basic",
                rarity="common"
            ),
            "speed_demon": Achievement(
                id="speed_demon",
                name="スピードデーモン",
                description="1秒以内でOCR処理を完了",
                icon="⚡",
                category="performance",
                rarity="rare"
            ),
            "text_master": Achievement(
                id="text_master",
                name="テキストマスター",
                description="1000文字以上のテキストを抽出",
                icon="📝",
                category="content",
                rarity="epic"
            ),
            "multilingual": Achievement(
                id="multilingual",
                name="多言語対応",
                description="3つの異なる言語でテキストを抽出",
                icon="🌍",
                category="language",
                rarity="rare"
            ),
            "batch_processor": Achievement(
                id="batch_processor",
                name="バッチ処理マスター",
                description="一度に10枚以上の画像を処理",
                icon="📦",
                category="efficiency",
                rarity="epic"
            ),
            "perfectionist": Achievement(
                id="perfectionist",
                name="完璧主義者",
                description="連続で10回成功したOCR処理",
                icon="✨",
                category="quality",
                rarity="legendary"
            ),
            "daily_streak": Achievement(
                id="daily_streak",
                name="継続は力なり",
                description="7日連続でOCRを使用",
                icon="🔥",
                category="consistency",
                rarity="rare"
            ),
            "file_explorer": Achievement(
                id="file_explorer",
                name="ファイル探検家",
                description="5つの異なるファイル形式を処理",
                icon="🔍",
                category="exploration",
                rarity="common"
            ),
            "efficiency_expert": Achievement(
                id="efficiency_expert",
                name="効率化の達人",
                description="合計処理時間が1時間を超える",
                icon="⏱️",
                category="time",
                rarity="epic"
            ),
            "character_collector": Achievement(
                id="character_collector",
                name="文字コレクター",
                description="合計10,000文字を抽出",
                icon="📚",
                category="content",
                rarity="legendary"
            )
        }
        return achievements_data
    
    def _load_challenges(self) -> Dict[str, Challenge]:
        """チャレンジデータを読み込み"""
        today = datetime.date.today()
        challenges_data = {
            # デイリーチャレンジ
            "daily_ocr": Challenge(
                id="daily_ocr",
                name="デイリーOCR",
                description="今日は画像を1枚処理しよう",
                icon="📅",
                category="daily",
                daily=True,
                reward_points=5
            ),
            "daily_multilingual": Challenge(
                id="daily_multilingual",
                name="多言語チャレンジ",
                description="今日は2つの異なる言語でテキストを抽出",
                icon="🌐",
                category="daily",
                daily=True,
                reward_points=10
            ),
            "daily_efficiency": Challenge(
                id="daily_efficiency",
                name="効率チャレンジ",
                description="今日は5枚以上の画像を処理",
                icon="🚀",
                category="daily",
                daily=True,
                reward_points=15
            ),
            # ウィークリーチャレンジ
            "weekly_streak": Challenge(
                id="weekly_streak",
                name="週間継続",
                description="今週は5日間連続でOCRを使用",
                icon="📈",
                category="weekly",
                weekly=True,
                reward_points=50
            ),
            "weekly_master": Challenge(
                id="weekly_master",
                name="週間マスター",
                description="今週は合計1000文字を抽出",
                icon="👑",
                category="weekly",
                weekly=True,
                reward_points=75
            )
        }
        return challenges_data
    
    def _load_seasonal_themes(self) -> Dict[str, Dict[str, Any]]:
        """季節テーマデータを読み込み"""
        current_month = datetime.datetime.now().month
        
        themes = {
            "spring": {
                "name": "春のテーマ",
                "colors": {
                    "primary": "#4ade80",
                    "secondary": "#f0fdf4",
                    "accent": "#22c55e"
                },
                "months": [3, 4, 5],
                "icon": "🌸"
            },
            "summer": {
                "name": "夏のテーマ",
                "colors": {
                    "primary": "#f59e0b",
                    "secondary": "#fffbeb",
                    "accent": "#d97706"
                },
                "months": [6, 7, 8],
                "icon": "☀️"
            },
            "autumn": {
                "name": "秋のテーマ",
                "colors": {
                    "primary": "#f97316",
                    "secondary": "#fff7ed",
                    "accent": "#ea580c"
                },
                "months": [9, 10, 11],
                "icon": "🍁"
            },
            "winter": {
                "name": "冬のテーマ",
                "colors": {
                    "primary": "#3b82f6",
                    "secondary": "#eff6ff",
                    "accent": "#2563eb"
                },
                "months": [12, 1, 2],
                "icon": "❄️"
            }
        }
        
        # 現在の季節を判定
        for season, theme in themes.items():
            if current_month in theme["months"]:
                return {season: theme}
        
        return {"default": {"name": "デフォルトテーマ", "colors": {}, "icon": "📷"}}
    
    def get_user_stats(self) -> UserStats:
        """ユーザー統計を取得"""
        stats_data = st.session_state.gamification_data['user_stats']
        return UserStats(**stats_data)
    
    def update_user_stats(self, **kwargs):
        """ユーザー統計を更新"""
        stats = self.get_user_stats()
        for key, value in kwargs.items():
            if hasattr(stats, key):
                setattr(stats, key, value)
        
        # レベルアップチェック
        self._check_level_up(stats)
        
        # セッション状態を更新
        st.session_state.gamification_data['user_stats'] = asdict(stats)
    
    def _check_level_up(self, stats: UserStats):
        """レベルアップをチェック"""
        required_exp = stats.level * 100  # レベルごとに100ポイント必要
        
        if stats.experience >= required_exp:
            stats.level += 1
            stats.experience -= required_exp
            self._show_level_up_notification(stats.level)
    
    def _show_level_up_notification(self, new_level: int):
        """レベルアップ通知を表示"""
        st.session_state.show_level_up = True
        st.session_state.new_level = new_level
    
    def check_achievements(self, action: str, **kwargs):
        """実績をチェック"""
        stats = self.get_user_stats()
        
        for achievement_id, achievement in self.achievements.items():
            if achievement.unlocked:
                continue
            
            if self._check_achievement_condition(achievement_id, action, stats, **kwargs):
                self._unlock_achievement(achievement_id)
    
    def _check_achievement_condition(self, achievement_id: str, action: str, stats: UserStats, **kwargs) -> bool:
        """実績条件をチェック"""
        if achievement_id == "first_ocr":
            return stats.total_images_processed >= 1
        
        elif achievement_id == "speed_demon":
            processing_time = kwargs.get('processing_time', 0)
            return processing_time <= 1.0
        
        elif achievement_id == "text_master":
            text_length = kwargs.get('text_length', 0)
            return text_length >= 1000
        
        elif achievement_id == "multilingual":
            languages = kwargs.get('languages', set())
            return len(languages) >= 3
        
        elif achievement_id == "batch_processor":
            batch_size = kwargs.get('batch_size', 0)
            return batch_size >= 10
        
        elif achievement_id == "perfectionist":
            return stats.successful_ocr_count >= 10 and stats.failed_ocr_count == 0
        
        elif achievement_id == "daily_streak":
            return stats.consecutive_days >= 7
        
        elif achievement_id == "file_explorer":
            file_types = kwargs.get('file_types', set())
            return len(file_types) >= 5
        
        elif achievement_id == "efficiency_expert":
            return stats.total_processing_time >= 3600  # 1時間
        
        elif achievement_id == "character_collector":
            return stats.total_characters_extracted >= 10000
        
        return False
    
    def _unlock_achievement(self, achievement_id: str):
        """実績を解除"""
        achievement = self.achievements[achievement_id]
        achievement.unlocked = True
        achievement.unlocked_date = datetime.datetime.now().isoformat()
        
        # セッション状態を更新
        st.session_state.gamification_data['achievements'][achievement_id] = asdict(achievement)
        st.session_state.gamification_data['unlocked_achievements'].append(achievement_id)
        
        # ポイントを追加
        points = self._get_achievement_points(achievement.rarity)
        self.update_user_stats(total_points=self.get_user_stats().total_points + points)
        
        # 通知を表示
        self._show_achievement_notification(achievement, points)
    
    def _get_achievement_points(self, rarity: str) -> int:
        """実績のポイントを取得"""
        points_map = {
            "common": 10,
            "rare": 25,
            "epic": 50,
            "legendary": 100
        }
        return points_map.get(rarity, 10)
    
    def _show_achievement_notification(self, achievement: Achievement, points: int):
        """実績解除通知を表示"""
        st.session_state.show_achievement = True
        st.session_state.achievement_data = {
            'name': achievement.name,
            'description': achievement.description,
            'icon': achievement.icon,
            'points': points
        }
    
    def check_challenges(self, action: str, **kwargs):
        """チャレンジをチェック"""
        today = datetime.date.today()
        
        for challenge_id, challenge in self.challenges.items():
            if challenge.completed:
                continue
            
            # デイリーチャレンジのリセット
            if challenge.daily and challenge.completed_date:
                completed_date = datetime.date.fromisoformat(challenge.completed_date)
                if completed_date < today:
                    challenge.completed = False
                    challenge.completed_date = None
                    challenge.progress = 0
            
            # ウィークリーチャレンジのリセット
            if challenge.weekly and challenge.completed_date:
                completed_date = datetime.date.fromisoformat(challenge.completed_date)
                days_diff = (today - completed_date).days
                if days_diff >= 7:
                    challenge.completed = False
                    challenge.completed_date = None
                    challenge.progress = 0
            
            if self._check_challenge_condition(challenge_id, action, **kwargs):
                self._complete_challenge(challenge_id)
    
    def _check_challenge_condition(self, challenge_id: str, action: str, **kwargs) -> bool:
        """チャレンジ条件をチェック"""
        if challenge_id == "daily_ocr":
            return kwargs.get('images_processed', 0) >= 1
        
        elif challenge_id == "daily_multilingual":
            languages = kwargs.get('languages', set())
            return len(languages) >= 2
        
        elif challenge_id == "daily_efficiency":
            return kwargs.get('images_processed', 0) >= 5
        
        elif challenge_id == "weekly_streak":
            stats = self.get_user_stats()
            return stats.consecutive_days >= 5
        
        elif challenge_id == "weekly_master":
            stats = self.get_user_stats()
            return stats.total_characters_extracted >= 1000
        
        return False
    
    def _complete_challenge(self, challenge_id: str):
        """チャレンジを完了"""
        challenge = self.challenges[challenge_id]
        challenge.completed = True
        challenge.completed_date = datetime.datetime.now().isoformat()
        challenge.progress = challenge.max_progress
        
        # セッション状態を更新
        st.session_state.gamification_data['challenges'][challenge_id] = asdict(challenge)
        st.session_state.gamification_data['completed_challenges'].append(challenge_id)
        
        # ポイントを追加
        self.update_user_stats(total_points=self.get_user_stats().total_points + challenge.reward_points)
        
        # 通知を表示
        self._show_challenge_notification(challenge)
    
    def _show_challenge_notification(self, challenge: Challenge):
        """チャレンジ完了通知を表示"""
        st.session_state.show_challenge = True
        st.session_state.challenge_data = {
            'name': challenge.name,
            'description': challenge.description,
            'icon': challenge.icon,
            'points': challenge.reward_points
        }
    
    def get_current_theme(self) -> Dict[str, Any]:
        """現在のテーマを取得"""
        return list(self.seasonal_themes.values())[0]
    
    def render_achievements_panel(self):
        """実績パネルを表示"""
        st.subheader("🏆 実績")
        
        stats = self.get_user_stats()
        unlocked_count = len(st.session_state.gamification_data['unlocked_achievements'])
        total_count = len(self.achievements)
        
        st.metric("実績進捗", f"{unlocked_count}/{total_count}")
        
        # 実績一覧
        for achievement in self.achievements.values():
            with st.expander(f"{achievement.icon} {achievement.name}"):
                st.write(f"**説明**: {achievement.description}")
                st.write(f"**カテゴリ**: {achievement.category}")
                st.write(f"**レアリティ**: {achievement.rarity}")
                
                if achievement.unlocked:
                    st.success(f"✅ 解除済み ({achievement.unlocked_date})")
                else:
                    st.info("🔒 未解除")
    
    def render_challenges_panel(self):
        """チャレンジパネルを表示"""
        st.subheader("🎯 チャレンジ")
        
        # デイリーチャレンジ
        st.write("**📅 デイリーチャレンジ**")
        for challenge in self.challenges.values():
            if challenge.daily:
                with st.expander(f"{challenge.icon} {challenge.name}"):
                    st.write(f"**説明**: {challenge.description}")
                    st.write(f"**報酬**: {challenge.reward_points}ポイント")
                    
                    if challenge.completed:
                        st.success(f"✅ 完了 ({challenge.completed_date})")
                    else:
                        progress = challenge.progress / challenge.max_progress
                        st.progress(progress)
                        st.write(f"進捗: {challenge.progress}/{challenge.max_progress}")
        
        # ウィークリーチャレンジ
        st.write("**📈 ウィークリーチャレンジ**")
        for challenge in self.challenges.values():
            if challenge.weekly:
                with st.expander(f"{challenge.icon} {challenge.name}"):
                    st.write(f"**説明**: {challenge.description}")
                    st.write(f"**報酬**: {challenge.reward_points}ポイント")
                    
                    if challenge.completed:
                        st.success(f"✅ 完了 ({challenge.completed_date})")
                    else:
                        progress = challenge.progress / challenge.max_progress
                        st.progress(progress)
                        st.write(f"進捗: {challenge.progress}/{challenge.max_progress}")
    
    def render_stats_panel(self):
        """統計パネルを表示"""
        st.subheader("📊 統計")
        
        stats = self.get_user_stats()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("レベル", stats.level)
            st.metric("経験値", f"{stats.experience}/{(stats.level + 1) * 100}")
            st.metric("総ポイント", stats.total_points)
            st.metric("連続日数", stats.consecutive_days)
        
        with col2:
            st.metric("処理画像数", stats.total_images_processed)
            st.metric("抽出文字数", stats.total_characters_extracted)
            st.metric("成功回数", stats.successful_ocr_count)
            st.metric("失敗回数", stats.failed_ocr_count)
    
    def render_notifications(self):
        """通知を表示"""
        # レベルアップ通知
        if st.session_state.get('show_level_up', False):
            new_level = st.session_state.get('new_level', 1)
            st.success(f"🎉 レベルアップ！ レベル {new_level} に到達しました！")
            st.session_state.show_level_up = False
        
        # 実績解除通知
        if st.session_state.get('show_achievement', False):
            achievement_data = st.session_state.get('achievement_data', {})
            st.success(
                f"🏆 実績解除！ {achievement_data.get('icon', '')} "
                f"**{achievement_data.get('name', '')}** "
                f"({achievement_data.get('points', 0)}ポイント)"
            )
            st.info(achievement_data.get('description', ''))
            st.session_state.show_achievement = False
        
        # チャレンジ完了通知
        if st.session_state.get('show_challenge', False):
            challenge_data = st.session_state.get('challenge_data', {})
            st.success(
                f"🎯 チャレンジ完了！ {challenge_data.get('icon', '')} "
                f"**{challenge_data.get('name', '')}** "
                f"({challenge_data.get('points', 0)}ポイント)"
            )
            st.info(challenge_data.get('description', ''))
            st.session_state.show_challenge = False


# グローバルインスタンス
_gamification_instance = None

def _get_gamification():
    """ゲーミフィケーションインスタンスを取得（遅延初期化）"""
    global _gamification_instance
    if _gamification_instance is None:
        _gamification_instance = GamificationSystem()
    return _gamification_instance

def update_stats(action: str, **kwargs):
    """統計を更新（簡易関数）"""
    try:
        gamification = _get_gamification()
        gamification.check_achievements(action, **kwargs)
        gamification.check_challenges(action, **kwargs)
    except Exception:
        pass  # ゲーミフィケーションが利用できない場合は無視

def render_gamification_panel():
    """ゲーミフィケーションパネルを表示（簡易関数）"""
    try:
        gamification = _get_gamification()
        gamification.render_notifications()
        
        with st.expander("🎮 ゲーミフィケーション"):
            tab1, tab2, tab3 = st.tabs(["📊 統計", "🏆 実績", "🎯 チャレンジ"])
            
            with tab1:
                gamification.render_stats_panel()
            
            with tab2:
                gamification.render_achievements_panel()
            
            with tab3:
                gamification.render_challenges_panel()
    except Exception:
        pass  # ゲーミフィケーションが利用できない場合は無視
