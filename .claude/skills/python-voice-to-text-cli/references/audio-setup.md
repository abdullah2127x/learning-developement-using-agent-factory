# Audio Setup for Voice-to-Text

This document covers audio device configuration and troubleshooting for voice-to-text applications.

## Required Dependencies

### Installation
```bash
# Install the main speech recognition library
pip install SpeechRecognition

# Install PyAudio for microphone support (may require additional steps on some systems)
pip install pyaudio

# Alternative audio library (if PyAudio is problematic)
pip install sounddevice
```

### Platform-Specific Installation

#### Windows
```bash
# PyAudio typically installs without issues on Windows
pip install pyaudio
```

#### macOS
```bash
# May need to install portaudio first
brew install portaudio
pip install pyaudio

# Or use conda
conda install pyaudio
```

#### Linux (Ubuntu/Debian)
```bash
# Install system dependencies
sudo apt-get install portaudio19-dev python3-pyaudio

# Then install Python package
pip install pyaudio
```

#### Linux (CentOS/RHEL/Fedora)
```bash
# Install system dependencies
sudo yum install portaudio-devel
# or on newer versions
sudo dnf install portaudio-devel

# Then install Python package
pip install pyaudio
```

## Audio Device Configuration

### Checking Available Audio Devices
```python
import speech_recognition as sr

# List available microphones
print("Available microphones:")
for device_index in range(sr.Microphone.list_working_microphones()):
    m = sr.Microphone(device_index=device_index)
    print(f"  Microphone {device_index}: {m}")
```

### Using Specific Microphone
```python
import speech_recognition as sr

# List available microphones
for device_index in range(sr.Microphone.list_working_microphones()):
    m = sr.Microphone(device_index=device_index)
    print(f"Microphone {device_index}: {m}")

# Use a specific microphone
recognizer = sr.Recognizer()
microphone = sr.Microphone(device_index=1)  # Use the second microphone

with microphone as source:
    recognizer.adjust_for_ambient_noise(source)
    audio = recognizer.listen(source)
```

## Audio Quality Optimization

### Ambient Noise Adjustment
```python
import speech_recognition as sr

recognizer = sr.Recognizer()
microphone = sr.Microphone()

with microphone as source:
    # Adjust for ambient noise (use 1-2 seconds for duration)
    recognizer.adjust_for_ambient_noise(source, duration=2)

    # Listen with specific parameters
    audio = recognizer.listen(
        source,
        timeout=5,          # Maximum time to listen (seconds)
        phrase_time_limit=10 # Maximum time for a phrase (seconds)
    )
```

### Audio Parameters
- `duration`: Time for ambient noise adjustment (1-2 seconds typical)
- `timeout`: Max time to wait for speech (None for infinite)
- `phrase_time_limit`: Max time for a single phrase (None for infinite)

## Common Audio Issues and Solutions

### Issue: "No input device found"
**Solutions:**
1. Check if microphone is properly connected
2. Verify microphone works in other applications
3. Check system audio settings
4. Install PyAudio properly for your platform

### Issue: "Could not understand audio"
**Solutions:**
1. Speak louder and clearer
2. Reduce background noise
3. Adjust microphone sensitivity
4. Use longer ambient noise adjustment time
5. Try different recognition backends

### Issue: PyAudio Installation Problems
**Solutions:**
1. Use pre-compiled wheels: `pip install --upgrade pip` then `pip install pyaudio`
2. Install system dependencies first (portaudio-devel, etc.)
3. Use alternative: `pip install sounddevice` for audio input
4. Use conda instead of pip: `conda install pyaudio`

## Testing Audio Setup

### Basic Test Script
```python
import speech_recognition as sr

def test_microphone():
    recognizer = sr.Recognizer()

    # Test if microphone is available
    try:
        with sr.Microphone() as source:
            print("Microphone is accessible. Testing...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Microphone test successful!")
            return True
    except Exception as e:
        print(f"Microphone test failed: {e}")
        return False

if __name__ == "__main__":
    test_microphone()
```

## Performance Considerations

### Sample Rate and Energy Threshold
```python
import speech_recognition as sr

recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Adjust sample rate (default is 16000)
microphone.SAMPLE_RATE = 16000  # or 44100 for higher quality

# Adjust energy threshold (default is 300)
# Lower values = more sensitive, higher values = less sensitive
recognizer.energy_threshold = 400

with microphone as source:
    recognizer.adjust_for_ambient_noise(source)
    audio = recognizer.listen(source)
```

### Energy Threshold Guidelines
- **Quiet environment**: 300-400
- **Moderate background noise**: 400-600
- **Noisy environment**: 600-800
- **Very noisy environment**: 800-1000