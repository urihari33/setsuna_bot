#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつなBot Streamlit デモ
日本語表示テスト用プロトタイプ
"""

import streamlit as st
import time
import sys
import os

# せつなBotコアモジュールのパス追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    # ページ設定
    st.set_page_config(
        page_title="せつなBot - Streamlit版",
        page_icon="🤖",
        layout="wide"
    )
    
    # タイトル
    st.title("🤖 せつなBot - 音声対話システム")
    st.markdown("---")
    
    # サイドバー - 設定パネル
    with st.sidebar:
        st.header("🎛️ 音声設定")
        
        # 音声パラメータ
        speed = st.slider("話速", 0.5, 2.0, 1.2, 0.1)
        pitch = st.slider("音程", -0.15, 0.15, 0.0, 0.01)
        intonation = st.slider("抑揚", 0.5, 2.0, 1.0, 0.1)
        
        st.markdown("---")
        
        # システム状態
        st.header("📊 システム状態")
        status_placeholder = st.empty()
        conv_count_placeholder = st.empty()
        
        # 初期状態表示
        status_placeholder.success("✅ 待機中")
        conv_count_placeholder.info(f"対話回数: 0回")
    
    # メインエリア
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 チャット")
        
        # チャット履歴表示エリア
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = [
                {"role": "assistant", "content": "こんにちは！せつなです。何かお話ししましょうか？"}
            ]
        
        # チャット履歴表示
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"**👤 あなた:** {message['content']}")
                else:
                    st.markdown(f"**🤖 せつな:** {message['content']}")
        
        # 入力フォーム
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("メッセージを入力:", placeholder="こんにちは！")
            submitted = st.form_submit_button("送信", use_container_width=True)
            
            if submitted and user_input:
                # ユーザーメッセージを追加
                st.session_state.chat_history.append({
                    "role": "user", 
                    "content": user_input
                })
                
                # せつなの応答（簡易版）
                response = generate_response(user_input)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })
                
                # 対話回数更新
                conv_count = len([m for m in st.session_state.chat_history if m["role"] == "user"])
                conv_count_placeholder.info(f"対話回数: {conv_count}回")
                
                st.rerun()
    
    with col2:
        st.header("🔧 操作パネル")
        
        # 音声テストボタン
        if st.button("🔊 音声テスト", use_container_width=True):
            status_placeholder.warning("🔊 音声テスト中...")
            with st.spinner("音声テスト実行中..."):
                time.sleep(2)  # 音声テストシミュレーション
            status_placeholder.success("✅ 音声テスト完了")
            st.success("音声テストが完了しました！")
        
        # 設定リセットボタン
        if st.button("🔄 設定リセット", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        
        st.markdown("---")
        
        # 現在の設定表示
        st.subheader("📋 現在の設定")
        st.text(f"話速: {speed:.1f}x")
        st.text(f"音程: {pitch:.2f}")
        st.text(f"抑揚: {intonation:.1f}")
        
        st.markdown("---")
        
        # 日本語表示テスト
        st.subheader("🎌 日本語表示テスト")
        test_texts = [
            "せつなBot",
            "システム状態",
            "対話回数",
            "音声設定",
            "こんにちは！"
        ]
        
        for text in test_texts:
            st.write(f"✅ {text}")

def generate_response(user_input):
    """簡易的な応答生成（デモ用）"""
    responses = {
        "こんにちは": "こんにちは！元気ですか？",
        "おはよう": "おはようございます！今日も良い一日にしましょう！",
        "ありがとう": "どういたしまして！いつでもお手伝いします。",
        "さようなら": "また今度お話ししましょうね！",
    }
    
    # キーワードマッチ
    for keyword, response in responses.items():
        if keyword in user_input:
            return response
    
    # デフォルト応答
    return f"「{user_input}」についてお話しするのは楽しいですね！他に何かありますか？"

if __name__ == "__main__":
    main()