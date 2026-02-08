# Error Handling for Voice-to-Text Applications

This document covers best practices for handling speech recognition errors and providing appropriate user feedback.

## Common Speech Recognition Errors

### 1. Timeout Errors
**Error Type:** `sr.WaitTimeoutError`
**Cause:** No speech detected within the specified timeout period
**Solution:** Provide feedback and allow retry

```python
import speech_recognition as sr

def handle_timeout_error():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening... (timeout in 5 seconds)")
        try:
            audio = recognizer.listen(source, timeout=5)
        except sr.WaitTimeoutError:
            print("No speech detected. Please try again.")
            # Option to retry
            return handle_timeout_error()  # Recursive retry or loop
```

### 2. Recognition Errors
**Error Type:** `sr.UnknownValueError`
**Cause:** Audio could not be understood
**Solution:** Ask user to repeat with suggestions

```python
def handle_recognition_error():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
            print("Suggestions:")
            print("- Speak more clearly")
            print("- Reduce background noise")
            print("- Try again")
            return None
```

### 3. Request Errors
**Error Type:** `sr.RequestError`
**Cause:** API request failed (network, service unavailable, etc.)
**Solution:** Provide offline alternative or retry

```python
def handle_request_error():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            return text
        except sr.RequestError as e:
            print(f"API request failed: {e}")
            print("Trying offline recognition...")

            # Fallback to offline recognition
            try:
                text = recognizer.recognize_sphinx(audio)
                return text
            except:
                print("Offline recognition also failed.")
                return None
```

## Comprehensive Error Handling Pattern

### Voice-to-Text with Error Handling
```python
import speech_recognition as sr
import time

def robust_voice_to_text(backend='google', max_retries=3):
    """
    Robust voice-to-text with comprehensive error handling
    """
    recognizer = sr.Recognizer()
    retry_count = 0

    while retry_count < max_retries:
        with sr.Microphone() as source:
            try:
                print(f"Attempt {retry_count + 1} of {max_retries}")
                print("Adjusting for ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Listening... Please speak now.")

                # Listen with timeout
                audio = recognizer.listen(source, timeout=5)
                print("Processing speech...")

                # Try recognition based on backend
                if backend == 'google':
                    text = recognizer.recognize_google(audio)
                elif backend == 'sphinx':
                    text = recognizer.recognize_sphinx(audio)
                else:
                    text = recognizer.recognize_google(audio)

                print(f"Recognized: {text}")
                return text

            except sr.WaitTimeoutError:
                print("No speech detected. Please speak more loudly or clearly.")
                retry_count += 1

            except sr.UnknownValueError:
                print("Could not understand audio. Please try again.")
                retry_count += 1

            except sr.RequestError as e:
                print(f"Service request failed: {e}")
                print("Trying offline recognition...")

                # Try offline fallback
                try:
                    text = recognizer.recognize_sphinx(audio)
                    print(f"Offline recognition: {text}")
                    return text
                except:
                    print("Offline recognition also failed.")
                    retry_count += 1
                    time.sleep(1)  # Brief pause before retry

    print(f"Failed after {max_retries} attempts.")
    return None
```

## Error Recovery Strategies

### 1. Progressive Timeout Increase
```python
def adaptive_timeout_voice_to_text():
    """
    Increase timeout on each retry to accommodate slower speakers
    """
    recognizer = sr.Recognizer()
    timeouts = [3, 5, 7]  # Increasing timeouts

    for timeout in timeouts:
        with sr.Microphone() as source:
            try:
                print(f"Listening with {timeout}s timeout...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=timeout)
                text = recognizer.recognize_google(audio)
                return text
            except sr.WaitTimeoutError:
                print(f"No speech detected with {timeout}s timeout.")
                continue
            except sr.UnknownValueError:
                print("Could not understand audio.")
                continue
            except sr.RequestError as e:
                print(f"Request error: {e}")
                break

    return None
```

### 2. Multiple Backend Fallback
```python
def multi_backend_recognition():
    """
    Try multiple backends in order of preference
    """
    recognizer = sr.Recognizer()
    backends = [
        ('google', recognizer.recognize_google),
        ('sphinx', recognizer.recognize_sphinx),
        # Add more backends as needed
    ]

    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source, timeout=5)
        except sr.WaitTimeoutError:
            print("No speech detected.")
            return None

    for backend_name, recognition_func in backends:
        try:
            text = recognition_func(audio)
            print(f"Recognized with {backend_name}: {text}")
            return text
        except sr.UnknownValueError:
            print(f"{backend_name} could not understand audio.")
            continue
        except sr.RequestError as e:
            print(f"{backend_name} request failed: {e}")
            continue

    print("All recognition backends failed.")
    return None
```

## User Feedback Best Practices

### 1. Clear Error Messages
```python
def provide_clear_feedback(error_type, context=""):
    """
    Provide clear, actionable feedback to users
    """
    feedback_messages = {
        'timeout': (
            "I didn't hear anything. Please make sure your microphone is working "
            "and speak clearly when prompted."
        ),
        'unknown': (
            "I couldn't understand what you said. Please speak more clearly "
            "and try again."
        ),
        'request': (
            "I couldn't process your request. This might be due to network issues. "
            "Please check your internet connection and try again."
        ),
        'no_microphone': (
            "I couldn't access your microphone. Please check that it's connected "
            "and that the app has permission to use it."
        )
    }

    message = feedback_messages.get(error_type, "An error occurred.")
    if context:
        message += f" Context: {context}"

    print(f"Error: {message}")
    return message
```

### 2. Suggestive Feedback
```python
def provide_suggestive_feedback(error_type):
    """
    Provide feedback with suggestions for resolution
    """
    suggestions = {
        'timeout': [
            "Check your microphone is working",
            "Speak louder or closer to the microphone",
            "Wait for the prompt before speaking"
        ],
        'unknown': [
            "Speak more slowly and clearly",
            "Reduce background noise",
            "Use simpler, more direct language"
        ],
        'request': [
            "Check your internet connection",
            "Try again in a moment",
            "Use offline mode if available"
        ]
    }

    if error_type in suggestions:
        print("Suggestions to resolve this:")
        for i, suggestion in enumerate(suggestions[error_type], 1):
            print(f"  {i}. {suggestion}")
```

## Todo Application Error Handling

### Voice Todo with Error Handling
```python
class VoiceTodoWithErrorHandling:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.todo_list = []  # Simplified todo list

    def safe_voice_input(self, prompt="Please speak your command:"):
        """
        Safe voice input with error handling and retry logic
        """
        print(prompt)

        for attempt in range(3):  # 3 attempts
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    print(f"Listening... (attempt {attempt + 1}/3)")

                    audio = self.recognizer.listen(source, timeout=5)
                    text = self.recognizer.recognize_google(audio)

                    print(f"Heard: {text}")
                    return text

            except sr.WaitTimeoutError:
                print(f"No speech detected. Attempt {attempt + 1}/3")
                if attempt == 2:  # Last attempt
                    print("Please type your command instead:")
                    return input("Command: ")

            except sr.UnknownValueError:
                print(f"Could not understand. Attempt {attempt + 1}/3")
                if attempt < 2:  # Not the last attempt
                    print("Please speak more clearly.")

            except sr.RequestError as e:
                print(f"Service error: {e}")
                print("Falling back to manual input:")
                return input("Command: ")

        print("Too many failed attempts. Please enter manually:")
        return input("Command: ")

    def process_voice_todo_command(self):
        """
        Process voice command for todo with error handling
        """
        voice_input = self.safe_voice_input("Add a task by speaking:")

        if voice_input:
            # Process the command (simplified)
            self.todo_list.append(voice_input)
            print(f"Added task: {voice_input}")
            print(f"Total tasks: {len(self.todo_list)}")
        else:
            print("No valid command received.")
```

## Error Logging

### For Debugging and Improvement
```python
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    filename='voice_recognition.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_recognition_attempt(audio_data, error_type=None, error_message=None):
    """
    Log recognition attempts for debugging
    """
    timestamp = datetime.now().isoformat()

    if error_type:
        logging.error(f"{timestamp} - {error_type}: {error_message}")
    else:
        logging.info(f"{timestamp} - Successful recognition")
```

## Graceful Degradation

### Fallback to Text Input
```python
def voice_with_fallback(prompt="Speak your command:"):
    """
    Voice input with graceful fallback to text input
    """
    try:
        # Try voice input first
        with sr.Microphone() as source:
            recognizer = sr.Recognizer()
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print(prompt)
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            return text, 'voice'
    except:
        # Fallback to text input
        print("Voice input failed. Please type your command:")
        text = input("> ")
        return text, 'text'
```

These error handling patterns ensure your voice-to-text application remains robust and user-friendly even when recognition fails.