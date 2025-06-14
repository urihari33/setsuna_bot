import tkinter as tk
import threading
from setsuna_hotkey_mode import main as hotkey_main
from voicevox_speaker import voice_settings
from setsuna_logger import log_system

# --- UI更新関数 ---
def update_speed(val):
    voice_settings["speedScale"] = float(val)

def update_pitch(val):
    voice_settings["pitchScale"] = float(val)

def update_intonation(val):
    voice_settings["intonationScale"] = float(val)

# --- UI構築 ---
root = tk.Tk()
root.title("片無せつな 音声設定UI")

slider_frame = tk.Frame(root)
slider_frame.pack(pady=15)

speed_slider = tk.Scale(slider_frame, from_=0.5, to=2.0, resolution=0.1, label="話す速さ",
         orient=tk.HORIZONTAL, command=update_speed)
speed_slider.set(voice_settings["speedScale"])
speed_slider.pack(side=tk.LEFT, padx=5)

pitch_slider = tk.Scale(slider_frame, from_=-1.0, to=1.0, resolution=0.1, label="ピッチ",
         orient=tk.HORIZONTAL, command=update_pitch)
pitch_slider.set(voice_settings["pitchScale"])
pitch_slider.pack(side=tk.LEFT, padx=5)

intonation_slider = tk.Scale(slider_frame, from_=0.0, to=2.0, resolution=0.1, label="イントネーション",
         orient=tk.HORIZONTAL, command=update_intonation)
intonation_slider.set(voice_settings["intonationScale"])
intonation_slider.pack(side=tk.LEFT, padx=5)


# --- ホットキー録音スレッド開始 ---
log_system("UI started, launching hotkey mode")
hotkey_thread = threading.Thread(target=hotkey_main, daemon=True)
hotkey_thread.start()

# --- 起動 ---
log_system("UI mainloop started")
root.mainloop()
log_system("UI mainloop ended")
