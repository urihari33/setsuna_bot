"""
ダイアログ修正パッチ

マウスホイールエラーを修正したダイアログコード
"""

# PlaylistAddDialog の修正版 create_widgets メソッド
def create_widgets_fixed(self):
    """ウィジェットを作成"""
    # スクロール可能なフレームを作成
    self.canvas = tk.Canvas(self.dialog)
    scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=self.canvas.yview)
    self.scrollable_frame = ttk.Frame(self.canvas)
    
    self.scrollable_frame.bind(
        "<Configure>",
        lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    )
    
    self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
    self.canvas.configure(yscrollcommand=scrollbar.set)
    
    # パックレイアウト
    self.canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # メインフレーム
    main_frame = ttk.Frame(self.scrollable_frame, padding="20")
    main_frame.pack(fill='both', expand=True)
    
    # マウスホイールスクロール対応（修正版）
    def _on_mousewheel(event):
        try:
            if self.canvas.winfo_exists():
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except (tk.TclError, AttributeError):
            pass  # ダイアログが閉じられている場合は無視
    
    # ダイアログとcanvasにのみバインド
    self.canvas.bind("<MouseWheel>", _on_mousewheel)
    self.dialog.bind("<MouseWheel>", _on_mousewheel)
    
    # 残りのウィジェット作成は元のコードと同じ...


# cleanup_and_close メソッドの追加
def cleanup_and_close(self):
    """ダイアログのクリーンアップと終了"""
    try:
        # マウスホイールイベントのバインドを解除
        if hasattr(self, 'canvas') and self.canvas.winfo_exists():
            self.canvas.unbind("<MouseWheel>")
        self.dialog.unbind("<MouseWheel>")
        self.dialog.destroy()
    except (tk.TclError, AttributeError):
        try:
            self.dialog.destroy()
        except:
            pass