#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setsuna Bot Minimal GUI - English Version
Status display, voice parameter adjustment, simple operations
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
import os

# Add core module path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class SetsunaGUIEnglish:
    def __init__(self):
        """Initialize Setsuna Bot GUI"""
        # Create main window
        self.root = tk.Tk()
        self.root.title("Setsuna Bot - Voice Dialogue System")
        self.root.geometry("500x600")
        self.root.resizable(True, True)
        
        # Use safe fonts
        self.default_font = ("Arial", 10)
        self.title_font = ("Arial", 16, "bold")
        
        # System components (lazy initialization)
        self.voice_output = None
        self.setsuna_chat = None
        self.voice_input = None
        
        # State management
        self.is_initialized = False
        self.is_talking = False
        self.conversation_count = 0
        
        # Initialize GUI elements
        self._create_widgets()
        self._setup_layout()
        
        # Start initialization
        self._initialize_system()
    
    def _create_widgets(self):
        """Create GUI elements"""
        # ===== Title Area =====
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = ttk.Label(
            title_frame, 
            text="Setsuna Bot", 
            font=self.title_font
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Voice Dialogue System v2.0",
            font=self.default_font
        )
        subtitle_label.pack()
        
        # ===== Status Area =====
        status_frame = ttk.LabelFrame(self.root, text="Status")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # System status
        self.system_status_var = tk.StringVar(value="Initializing...")
        ttk.Label(status_frame, text="System Status:", font=self.default_font).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.system_status_label = ttk.Label(status_frame, textvariable=self.system_status_var, font=self.default_font)
        self.system_status_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Conversation count
        self.conversation_count_var = tk.StringVar(value="0 times")
        ttk.Label(status_frame, text="Conversations:", font=self.default_font).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(status_frame, textvariable=self.conversation_count_var, font=self.default_font).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # ===== Voice Parameters Area =====
        voice_frame = ttk.LabelFrame(self.root, text="Voice Settings")
        voice_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Speed slider
        ttk.Label(voice_frame, text="Speed:", font=self.default_font).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.speed_var = tk.DoubleVar(value=1.2)
        self.speed_scale = ttk.Scale(
            voice_frame, 
            from_=0.5, to=2.0, 
            variable=self.speed_var,
            orient=tk.HORIZONTAL,
            command=self._on_voice_parameter_change
        )
        self.speed_scale.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        self.speed_value_label = ttk.Label(voice_frame, text="1.2x", font=self.default_font)
        self.speed_value_label.grid(row=0, column=2, padx=5, pady=5)
        
        # Pitch slider
        ttk.Label(voice_frame, text="Pitch:", font=self.default_font).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.pitch_var = tk.DoubleVar(value=0.0)
        self.pitch_scale = ttk.Scale(
            voice_frame,
            from_=-0.15, to=0.15,
            variable=self.pitch_var,
            orient=tk.HORIZONTAL,
            command=self._on_voice_parameter_change
        )
        self.pitch_scale.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.pitch_value_label = ttk.Label(voice_frame, text="0.0", font=self.default_font)
        self.pitch_value_label.grid(row=1, column=2, padx=5, pady=5)
        
        # Intonation slider
        ttk.Label(voice_frame, text="Intonation:", font=self.default_font).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.intonation_var = tk.DoubleVar(value=1.0)
        self.intonation_scale = ttk.Scale(
            voice_frame,
            from_=0.5, to=2.0,
            variable=self.intonation_var,
            orient=tk.HORIZONTAL,
            command=self._on_voice_parameter_change
        )
        self.intonation_scale.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        self.intonation_value_label = ttk.Label(voice_frame, text="1.0", font=self.default_font)
        self.intonation_value_label.grid(row=2, column=2, padx=5, pady=5)
        
        # Column resize settings
        voice_frame.columnconfigure(1, weight=1)
        
        # ===== Control Area =====
        control_frame = ttk.LabelFrame(self.root, text="Control Panel")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Voice test button
        self.test_button = ttk.Button(
            control_frame,
            text="Voice Test",
            command=self._test_voice,
            state=tk.DISABLED
        )
        self.test_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Text chat button
        self.chat_button = ttk.Button(
            control_frame,
            text="Text Chat",
            command=self._start_text_chat,
            state=tk.DISABLED
        )
        self.chat_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Reset settings button
        self.reset_button = ttk.Button(
            control_frame,
            text="Reset Settings",
            command=self._reset_settings
        )
        self.reset_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # ===== Log Area =====
        log_frame = ttk.LabelFrame(self.root, text="Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Log text area
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD, font=self.default_font)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
    
    def _setup_layout(self):
        """Setup layout"""
        # Window close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Initial log messages
        self._log("Setsuna Bot GUI starting...")
        self._log("System initialization in progress...")
    
    def _initialize_system(self):
        """Initialize system components"""
        def init_worker():
            try:
                self._log("Initializing voice output system...")
                from voice_output import VoiceOutput
                self.voice_output = VoiceOutput()
                
                self._log("Initializing chat system...")
                from setsuna_chat import SetsunaChat
                self.setsuna_chat = SetsunaChat()
                
                self._log("Initializing voice input system...")
                try:
                    from voice_input import VoiceInput
                    self.voice_input = VoiceInput()
                except:
                    from voice_input_mock import VoiceInput
                    self.voice_input = VoiceInput()
                    self._log("Using mock voice input")
                
                # Update UI
                self.root.after(0, self._on_initialization_complete)
                
            except Exception as e:
                error_msg = f"Initialization error: {e}"
                self._log(error_msg)
                self.root.after(0, lambda: self._on_initialization_error(str(e)))
        
        # Run initialization in separate thread
        threading.Thread(target=init_worker, daemon=True).start()
    
    def _on_initialization_complete(self):
        """Handle initialization completion"""
        self.is_initialized = True
        self.system_status_var.set("Ready")
        
        # Enable buttons
        self.test_button.config(state=tk.NORMAL)
        self.chat_button.config(state=tk.NORMAL)
        
        self._log("Setsuna Bot initialization complete!")
        self._log("Voice parameters can be adjusted")
        self._log("Click Text Chat button to start conversation")
        
        # Apply initial voice parameters
        self._apply_voice_parameters()
    
    def _on_initialization_error(self, error):
        """Handle initialization error"""
        self.system_status_var.set("Initialization failed")
        messagebox.showerror("Initialization Error", f"System initialization failed:\n{error}")
    
    def _on_voice_parameter_change(self, value=None):
        """Handle voice parameter changes"""
        # Update labels
        self.speed_value_label.config(text=f"{self.speed_var.get():.1f}x")
        self.pitch_value_label.config(text=f"{self.pitch_var.get():.2f}")
        self.intonation_value_label.config(text=f"{self.intonation_var.get():.1f}")
        
        # Apply to voice system
        if self.is_initialized and self.voice_output:
            self._apply_voice_parameters()
    
    def _apply_voice_parameters(self):
        """Apply voice parameters to voice system"""
        try:
            self.voice_output.update_settings(
                speed=self.speed_var.get(),
                pitch=self.pitch_var.get(),
                intonation=self.intonation_var.get()
            )
            self._log(f"Voice settings updated: Speed {self.speed_var.get():.1f}x, Pitch {self.pitch_var.get():.2f}, Intonation {self.intonation_var.get():.1f}")
        except Exception as e:
            self._log(f"Voice settings error: {e}")
    
    def _test_voice(self):
        """Execute voice test"""
        if not self.is_initialized:
            return
        
        def test_worker():
            try:
                self.root.after(0, lambda: self.system_status_var.set("Voice testing"))
                self._log("Executing voice test...")
                
                test_text = "Hello, this is Setsuna. Testing voice settings."
                self.voice_output.speak(test_text)
                
                self.root.after(0, lambda: self.system_status_var.set("Ready"))
                self._log("Voice test complete")
                
            except Exception as e:
                error_msg = f"Voice test error: {e}"
                self._log(error_msg)
                self.root.after(0, lambda: self.system_status_var.set("Error"))
        
        threading.Thread(target=test_worker, daemon=True).start()
    
    def _start_text_chat(self):
        """Start text chat"""
        if not self.is_initialized:
            return
        
        # Open simple text chat window
        self._open_text_chat_window()
    
    def _open_text_chat_window(self):
        """Open text chat window"""
        chat_window = tk.Toplevel(self.root)
        chat_window.title("Text Chat with Setsuna")
        chat_window.geometry("600x400")
        
        # Chat display area
        chat_frame = ttk.Frame(chat_window)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        chat_display = tk.Text(chat_frame, wrap=tk.WORD, height=15, font=self.default_font)
        chat_scrollbar = ttk.Scrollbar(chat_frame, orient=tk.VERTICAL, command=chat_display.yview)
        chat_display.configure(yscrollcommand=chat_scrollbar.set)
        
        chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Input area
        input_frame = ttk.Frame(chat_window)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        input_entry = ttk.Entry(input_frame, font=self.default_font)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        send_button = ttk.Button(input_frame, text="Send")
        send_button.pack(side=tk.RIGHT)
        
        # Initial message
        chat_display.insert(tk.END, "Setsuna: Hello! What would you like to talk about?\n\n")
        chat_display.config(state=tk.DISABLED)
        
        def send_message():
            user_input = input_entry.get().strip()
            if not user_input:
                return
            
            # Display user message
            chat_display.config(state=tk.NORMAL)
            chat_display.insert(tk.END, f"You: {user_input}\n")
            chat_display.config(state=tk.DISABLED)
            chat_display.see(tk.END)
            
            input_entry.delete(0, tk.END)
            
            # Generate response
            def response_worker():
                try:
                    response = self.setsuna_chat.get_response(user_input)
                    
                    # Display response
                    chat_window.after(0, lambda: self._display_response(chat_display, response))
                    
                    # Play voice
                    self.voice_output.speak(response)
                    
                    # Update statistics
                    self.conversation_count += 1
                    self.root.after(0, lambda: self.conversation_count_var.set(f"{self.conversation_count} times"))
                    
                except Exception as e:
                    error_msg = f"Response error: {e}"
                    chat_window.after(0, lambda: self._display_response(chat_display, error_msg))
            
            threading.Thread(target=response_worker, daemon=True).start()
        
        # Event bindings
        send_button.config(command=send_message)
        input_entry.bind("<Return>", lambda e: send_message())
        
        # Set focus
        input_entry.focus()
    
    def _display_response(self, chat_display, response):
        """Display chat response"""
        chat_display.config(state=tk.NORMAL)
        chat_display.insert(tk.END, f"Setsuna: {response}\n\n")
        chat_display.config(state=tk.DISABLED)
        chat_display.see(tk.END)
    
    def _reset_settings(self):
        """Reset settings"""
        self.speed_var.set(1.2)
        self.pitch_var.set(0.0)
        self.intonation_var.set(1.0)
        
        if self.is_initialized:
            self._apply_voice_parameters()
        
        self._log("Voice settings reset")
    
    def _log(self, message):
        """Add log message"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
    
    def _on_closing(self):
        """Handle window closing"""
        self._log("Closing Setsuna Bot GUI")
        self.root.destroy()
    
    def run(self):
        """Run GUI"""
        self.root.mainloop()

# Usage example
if __name__ == "__main__":
    print("Setsuna Bot Minimal GUI (English) starting...")
    
    try:
        gui = SetsunaGUIEnglish()
        gui.run()
    except Exception as e:
        print(f"GUI startup error: {e}")
        print("GUI may be limited in WSL2 environment")