#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
プログレス管理システム - Phase 2C-4
統合メッセージ処理の詳細進捗表示とユーザビリティ向上
"""

import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass

@dataclass
class ProgressStep:
    """プログレス処理ステップ"""
    id: str
    name: str
    description: str
    weight: float = 1.0  # 全体に占める重み
    status: str = "pending"  # pending, running, completed, error
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error_message: Optional[str] = None
    sub_progress: float = 0.0  # サブ進捗(0-100)

class ProgressManager:
    """プログレス管理クラス"""
    
    def __init__(self, update_callback: Optional[Callable] = None):
        """
        初期化
        
        Args:
            update_callback: プログレス更新時のコールバック関数
        """
        self.update_callback = update_callback
        self.steps: List[ProgressStep] = []
        self.current_step_index: int = -1
        self.total_progress: float = 0.0
        self.is_running: bool = False
        self.is_cancelled: bool = False
        self.start_time: Optional[float] = None
        self.lock = threading.Lock()
        
        print("📊 ProgressManager初期化完了")
    
    def add_step(self, step_id: str, name: str, description: str, weight: float = 1.0):
        """処理ステップを追加"""
        step = ProgressStep(
            id=step_id,
            name=name,
            description=description,
            weight=weight
        )
        self.steps.append(step)
        self._notify_update()
    
    def start_processing(self):
        """処理開始"""
        with self.lock:
            self.is_running = True
            self.is_cancelled = False
            self.start_time = time.time()
            self.current_step_index = -1
            self.total_progress = 0.0
            
            # 全ステップをpendingに初期化
            for step in self.steps:
                step.status = "pending"
                step.start_time = None
                step.end_time = None
                step.error_message = None
                step.sub_progress = 0.0
        
        print(f"🚀 プログレス処理開始: {len(self.steps)}ステップ")
        self._notify_update()
    
    def start_step(self, step_id: str) -> bool:
        """ステップ開始"""
        if self.is_cancelled:
            return False
            
        with self.lock:
            # ステップを見つける
            step_index = -1
            for i, step in enumerate(self.steps):
                if step.id == step_id:
                    step_index = i
                    break
            
            if step_index == -1:
                print(f"⚠️ ステップが見つかりません: {step_id}")
                return False
            
            # 前のステップを完了にする
            if self.current_step_index >= 0:
                prev_step = self.steps[self.current_step_index]
                if prev_step.status == "running":
                    prev_step.status = "completed"
                    prev_step.end_time = time.time()
            
            # 現在のステップを開始
            self.current_step_index = step_index
            current_step = self.steps[step_index]
            current_step.status = "running"
            current_step.start_time = time.time()
            current_step.sub_progress = 0.0
            
            print(f"🔄 ステップ開始: {current_step.name}")
            self._update_total_progress()
            self._notify_update()
            return True
    
    def update_step_progress(self, step_id: str, progress: float, message: str = ""):
        """ステップの進捗を更新"""
        if self.is_cancelled:
            return
            
        with self.lock:
            for step in self.steps:
                if step.id == step_id and step.status == "running":
                    step.sub_progress = max(0.0, min(100.0, progress))
                    if message:
                        step.description = message
                    break
            
            self._update_total_progress()
            self._notify_update()
    
    def complete_step(self, step_id: str, message: str = ""):
        """ステップ完了"""
        with self.lock:
            for step in self.steps:
                if step.id == step_id:
                    step.status = "completed"
                    step.end_time = time.time()
                    step.sub_progress = 100.0
                    if message:
                        step.description = message
                    break
            
            self._update_total_progress()
            self._notify_update()
            
            print(f"✅ ステップ完了: {step_id}")
    
    def error_step(self, step_id: str, error_message: str):
        """ステップエラー"""
        with self.lock:
            for step in self.steps:
                if step.id == step_id:
                    step.status = "error"
                    step.end_time = time.time()
                    step.error_message = error_message
                    break
            
            self._update_total_progress()
            self._notify_update()
            
            print(f"❌ ステップエラー: {step_id} - {error_message}")
    
    def cancel_processing(self):
        """処理キャンセル"""
        with self.lock:
            self.is_cancelled = True
            self.is_running = False
            
            # 実行中のステップをキャンセル状態に
            if self.current_step_index >= 0:
                current_step = self.steps[self.current_step_index]
                if current_step.status == "running":
                    current_step.status = "error"
                    current_step.error_message = "ユーザーによりキャンセル"
                    current_step.end_time = time.time()
        
        print("🛑 プログレス処理キャンセル")
        self._notify_update()
    
    def complete_processing(self):
        """処理完了"""
        with self.lock:
            self.is_running = False
            
            # 最後のステップを完了に
            if self.current_step_index >= 0:
                current_step = self.steps[self.current_step_index]
                if current_step.status == "running":
                    current_step.status = "completed"
                    current_step.end_time = time.time()
                    current_step.sub_progress = 100.0
            
            self.total_progress = 100.0
        
        print("🎉 プログレス処理完了")
        self._notify_update()
    
    def _update_total_progress(self):
        """全体進捗を計算"""
        if not self.steps:
            self.total_progress = 0.0
            return
        
        total_weight = sum(step.weight for step in self.steps)
        completed_weight = 0.0
        
        for step in self.steps:
            if step.status == "completed":
                completed_weight += step.weight
            elif step.status == "running":
                step_progress = step.sub_progress / 100.0
                completed_weight += step.weight * step_progress
        
        self.total_progress = (completed_weight / total_weight) * 100.0
    
    def _notify_update(self):
        """更新通知（デッドロック回避版）"""
        if self.update_callback:
            try:
                # ロックを取らずに最小限の情報でステータス作成
                status = {
                    'total_progress': self.total_progress,
                    'is_running': self.is_running,
                    'is_cancelled': self.is_cancelled,
                    'current_step': {
                        'name': f"処理中({self.current_step_index + 1}/{len(self.steps)})" if 0 <= self.current_step_index < len(self.steps) else "待機中",
                        'description': "処理実行中",
                        'sub_progress': 0.0,
                        'status': "running" if self.is_running else "pending"
                    } if self.is_running else None,
                    'elapsed_time': time.time() - self.start_time if self.start_time else 0.0,
                    'estimated_remaining': 0.0
                }
                self.update_callback(status)
            except Exception as e:
                print(f"⚠️ プログレス更新コールバックエラー: {e}")
        
    
    def get_status(self) -> Dict:
        """現在の状態を取得（簡素版）"""
        try:
            # ロック使用を最小限に
            current_step = None
            if 0 <= self.current_step_index < len(self.steps):
                current_step = self.steps[self.current_step_index]
            
            elapsed_time = 0.0
            if self.start_time:
                elapsed_time = time.time() - self.start_time
            
            # 推定残り時間計算
            estimated_remaining = 0.0
            if self.total_progress > 0 and self.is_running:
                estimated_total_time = elapsed_time / (self.total_progress / 100.0)
                estimated_remaining = max(0.0, estimated_total_time - elapsed_time)
            
            return {
                'total_progress': self.total_progress,
                'is_running': self.is_running,
                'is_cancelled': self.is_cancelled,
                'current_step': {
                    'index': self.current_step_index,
                    'name': current_step.name if current_step else "",
                    'description': current_step.description if current_step else "",
                    'sub_progress': current_step.sub_progress if current_step else 0.0,
                    'status': current_step.status if current_step else "pending"
                } if current_step else None,
                'elapsed_time': elapsed_time,
                'estimated_remaining': estimated_remaining
            }
        except Exception as e:
            print(f"❌ get_status エラー: {e}")
            return {
                'total_progress': 0.0,
                'is_running': False,
                'is_cancelled': False,
                'current_step': None,
                'elapsed_time': 0.0,
                'estimated_remaining': 0.0
            }
    
    def get_summary(self) -> str:
        """処理サマリーを取得"""
        status = self.get_status()
        
        if status['is_running']:
            current_step = status['current_step']
            if current_step:
                remaining_str = ""
                if status['estimated_remaining'] > 0:
                    remaining_str = f" (残り約{status['estimated_remaining']:.1f}秒)"
                return f"🔄 {current_step['name']} ({status['total_progress']:.1f}%){remaining_str}"
            else:
                return f"🔄 処理中... ({status['total_progress']:.1f}%)"
        elif status['is_cancelled']:
            return "🛑 処理がキャンセルされました"
        elif status['stats']['error_steps'] > 0:
            return f"⚠️ 処理完了（{status['stats']['error_steps']}件のエラー）"
        else:
            return "✅ 処理完了"