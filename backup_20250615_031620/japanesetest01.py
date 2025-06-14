# -*- coding: utf-8 -*-
import tkinter as tk
import tkinter.font as tkFont

root = tk.Tk()
root.title("日本語フォントテスト")

# ✅ 実際の日本語を直接書くこと！
label = tk.Label(root, text="こんにちは、せかい", font=("Noto Sans CJK JP", 14))
label.pack(padx=20, pady=20)

root.mainloop()
