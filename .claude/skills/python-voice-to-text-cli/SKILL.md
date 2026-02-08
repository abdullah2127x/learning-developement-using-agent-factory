---
name: python-voice-to-text-cli
description: |
  Converts microphone input to text using Python speech recognition libraries.
  This Python-specific skill should be used when users need to capture voice input and convert
  it to text for CLI applications, particularly for creating voice-enabled
  todo lists and other interactive command-line tools.
---

# Python Voice-to-Text CLI

Convert microphone input to text using Python speech recognition libraries.

## What This Skill Does

This skill enables real-time voice-to-text conversion in Python CLI applications:
- Capture audio from microphone input
- Convert speech to text using various backends
- Handle different audio quality conditions
- Provide error handling for common speech recognition issues

## When to Use This Skill

Use this skill when building Python CLI applications that need reliable voice input with fallback options, including:
- Python applications requiring both online and offline voice recognition
- Python systems needing high accuracy when online and basic functionality when offline
- Voice-enabled Python applications that must work in various network conditions
- Interactive command-line tools with resilient voice commands using Python

## Core Principles

### Python-Based Implementation
Specifically designed for Python CLI applications with Python speech recognition libraries.

### Real-time Processing
Process audio in real-time for responsive voice-to-text functionality.

### Backend Flexibility
Support multiple speech recognition backends for different environments and requirements.

### Error Resilience
Handle common speech recognition failures gracefully with appropriate feedback.

### Cross-Platform Compatibility
Work across different operating systems and audio hardware configurations.

## Recommended Libraries and Tools

### Python Libraries
- `SpeechRecognition`: Primary speech recognition library
- `pyaudio`: Audio input/output handling
- `sounddevice`: Alternative audio input library
- `webrtcvad`: Voice activity detection (optional)
- `vosk`: Offline speech recognition models (for privacy)

### Installation Patterns
```bash
# Basic setup
pip install SpeechRecognition pyaudio

# Alternative audio backend
pip install sounddevice

# Offline recognition
pip install vosk
```

### Basic Usage Pattern
```python
import speech_recognition as sr

# Initialize recognizer
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Adjust for ambient noise
with microphone as source:
    recognizer.adjust_for_ambient_noise(source)

# Listen and convert
with microphone as source:
    audio = recognizer.listen(source)
    text = recognizer.recognize_google(audio)
```

## Implementation Patterns

### Internet-First with Offline Fallback
```python
import speech_recognition as sr
import socket

def check_internet_connection():
    """Check if internet connection is available"""
    try:
        # Try to connect to Google's DNS server
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def listen_with_fallback():
    # Check internet connectivity first
    internet_available = check_internet_connection()
    if internet_available:
        print("Internet connection detected")
    else:
        print("No internet connection detected, using offline recognition")

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening...")
        audio = recognizer.listen(source, timeout=5)

    if internet_available:
        try:
            # Try online recognition first (Google)
            text = recognizer.recognize_google(audio)
            print(f"Online recognition successful: {text}")
            return text
        except sr.RequestError:
            print("Online service unavailable, trying offline...")
            try:
                # Fallback to offline recognition (Sphinx)
                text = recognizer.recognize_sphinx(audio)
                print(f"Offline recognition successful: {text}")
                return text
            except:
                return "Both online and offline services failed"
        except sr.UnknownValueError:
            print("Online couldn't understand, trying offline...")
            try:
                text = recognizer.recognize_sphinx(audio)
                print(f"Offline recognition successful: {text}")
                return text
            except:
                return "Could not understand audio with any service"
    else:
        # No internet, try offline recognition directly
        try:
            text = recognizer.recognize_sphinx(audio)
            print(f"Offline recognition successful: {text}")
            return text
        except:
            return "Offline recognition unavailable"
```

### Recognition Backends
- Google Web Speech API (online, high accuracy) - Primary service
- Sphinx (offline, basic accuracy) - Fallback service when online unavailable

## Scripts Available

### `scripts/voice_to_text_internet_fallback.py`
Python-based voice-to-text with online-first approach and offline fallback. Prioritizes online recognition (Google) with offline recognition (Sphinx) as fallback when internet is unavailable or server returns an error. Features continuous listening for up to 30 seconds, ESC key to stop at any time, and smart error handling. This is a Python-only implementation.

## Common Voice-to-Text Patterns

### Internet-First Recognition
```
1. Try online recognition (Google API)
2. If successful, return result
3. If online fails, try offline recognition (Sphinx)
4. Return result from offline service
```

### Fallback Handling
```
- Online recognition: Higher accuracy, requires internet
- Offline recognition: Basic accuracy, works without internet
- Automatic switching between services based on availability
```

### Error Resilience
```
- Network failure → Switch to offline service
- Recognition failure → Try alternative service
- Audio quality issues → Adjust and retry both services
```

## Troubleshooting

### Common Issues and Solutions

1. **"No input device found"**
   - Ensure microphone is properly connected
   - Check audio permissions in your environment
   - Install pyaudio: `pip install pyaudio`
   - On Linux: `sudo apt-get install portaudio19-dev python3-pyaudio`

2. **"Could not understand audio"**
   - Speak clearly and at appropriate volume
   - Reduce background noise
   - Adjust ambient noise settings
   - Try different recognition backends

3. **"RequestError" - API Connection Issues**
   - Check internet connection
   - Verify API keys for specific backends
   - Consider offline alternatives for privacy

4. **Audio Quality Issues**
   - Use high-quality microphone when possible
   - Implement noise reduction algorithms
   - Adjust microphone sensitivity settings

## References

For specific implementation details, see:
- `references/audio-setup.md` - Audio device configuration and troubleshooting
- `references/recognition-backends.md` - Comparison of online and offline speech recognition backends
- `references/error-handling.md` - Best practices for handling speech recognition errors and fallback scenarios