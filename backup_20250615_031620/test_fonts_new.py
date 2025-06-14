#!/usr/bin/env python3
import tkinter as tk
import tkinter.font as tkFont

root = tk.Tk()
root.withdraw()

print('=== Tkinterフォント更新後テスト ===')
families = tkFont.families()
jp_fonts = [f for f in families if any(jp in f.lower() for jp in ['meiryo', 'yugoth', 'gothic', 'yu'])]
print(f'日本語フォント: {jp_fonts}')

# テストフォント
test_fonts = ['Meiryo', 'Yu Gothic', 'MS Gothic', 'Yu Gothic Medium']
for font_name in test_fonts:
    try:
        font = tkFont.Font(family=font_name, size=12)
        actual = font.actual()
        if actual['family'] != 'fixed':
            print(f'✅ {font_name}: {actual["family"]}')
        else:
            print(f'❌ {font_name}: フォールバック -> fixed')
    except Exception as e:
        print(f'❌ {font_name}: エラー - {e}')

root.destroy()