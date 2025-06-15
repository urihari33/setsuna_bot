#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows専用音声システム
PyAudio・WASAPI・Windows Speech APIを活用した高性能音声処理
"""

from .voice_input import WindowsVoiceInput
from .device_manager import WindowsAudioDeviceManager
from .permissions import WindowsPermissionManager

__version__ = "1.0.0"
__all__ = ["WindowsVoiceInput", "WindowsAudioDeviceManager", "WindowsPermissionManager"]