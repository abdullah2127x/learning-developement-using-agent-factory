#!/usr/bin/env python3
"""
voice_to_text_internet_fallback.py - Voice-to-text with online-first approach and offline fallback

This script prioritizes online recognition (Google) with offline recognition (Sphinx) as fallback.
Useful when you want the best accuracy but need reliability when internet is unavailable.
"""

import speech_recognition as sr
import sys
import time
import threading
import keyboard  # This will be added to requirements


def check_internet_connection():
    """
    Check if internet connection is available by trying to reach Google
    """
    import socket
    try:
        # Try to connect to Google's DNS server
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def voice_to_text_with_internet_fallback():
    """
    Voice-to-text with online-first approach and offline fallback
    Continuous listening for up to 30 seconds or until ESC is pressed
    """
    print("Voice-to-Text with Internet Fallback")
    print("-" * 40)
    print("Press ESC to stop listening at any time")
    print("Listening will automatically stop after 30 seconds of silence")

    # Check internet connectivity first
    internet_available = check_internet_connection()
    if internet_available:
        print("✓ Internet connection detected")
    else:
        print("Offline mode - using local recognition")

    recognizer = sr.Recognizer()
    audio_source = sr.Microphone()

    # Adjust for ambient noise
    with audio_source as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)

    print("Listening... Speak now (or press ESC to stop)")
    start_time = time.time()
    timeout_duration = 30  # 30 seconds timeout

    # Variable to store the result
    result_text = None
    stop_listening = False

    # Function to check for ESC key press
    def check_for_esc():
        nonlocal stop_listening
        while not stop_listening:
            if keyboard.is_pressed('esc'):
                stop_listening = True
                print("\nESC pressed - stopping...")
                break
            time.sleep(0.1)

    # Start the ESC key monitoring thread
    esc_thread = threading.Thread(target=check_for_esc, daemon=True)
    esc_thread.start()

    try:
        # Listen continuously until timeout or ESC key
        while not stop_listening:
            current_time = time.time()
            if current_time - start_time > timeout_duration:
                print("\nTimeout reached - no speech detected")
                break

            try:
                with audio_source as source:
                    # Listen with a shorter timeout to allow for ESC checking
                    audio = recognizer.listen(source, timeout=1.0)

                    # Process the audio
                    print("Processing speech...")

                    if internet_available:
                        # Try online recognition first (Google)
                        try:
                            text = recognizer.recognize_google(audio)
                            print(f"✓ Recognition successful: {text}")
                            result_text = text
                            break  # Stop after successful recognition
                        except sr.RequestError:
                            # Fallback to offline recognition (Sphinx)
                            try:
                                text = recognizer.recognize_sphinx(audio)
                                print(f"✓ Recognition successful: {text}")
                                result_text = text
                                break  # Stop after successful recognition
                            except:
                                print("Could not understand - continue listening")
                        except sr.UnknownValueError:
                            # Even if Google couldn't understand, try Sphinx
                            try:
                                text = recognizer.recognize_sphinx(audio)
                                print(f"✓ Recognition successful: {text}")
                                result_text = text
                                break  # Stop after successful recognition
                            except:
                                print("Could not understand - continue listening")
                    else:
                        # Offline mode only
                        try:
                            text = recognizer.recognize_sphinx(audio)
                            print(f"✓ Recognition successful: {text}")
                            result_text = text
                            break  # Stop after successful recognition
                        except:
                            print("Could not understand - continue listening")

            except sr.WaitTimeoutError:
                # No speech detected, continue listening
                continue
            except sr.UnknownValueError:
                # Could not understand, continue listening
                continue
            except sr.RequestError as e:
                # Error with audio source, continue listening
                continue

    except KeyboardInterrupt:
        print("\nInterrupted by user")

    # Stop the ESC thread
    stop_listening = True
    esc_thread.join(timeout=0.1)

    return result_text


def continuous_voice_to_text_with_fallback():
    """
    Continuous listening with internet fallback for ongoing input
    """
    print("Starting continuous listening mode...")
    print("Press ESC to stop at any time")
    print("Listening will automatically stop after 30 seconds of silence")

    result = voice_to_text_with_internet_fallback()

    if result:
        print(f"\nFinal result: {result}")
    else:
        print("\nNo speech was recognized or listening was stopped.")


def main():
    """Main function to demonstrate internet-first voice-to-text with fallback"""
    print("Voice-to-Text with Internet Fallback")
    print("=" * 40)
    print("This script prioritizes online recognition (Google) but falls back")
    print("to offline recognition (Sphinx) when internet is unavailable or")
    print("when the server returns an error.")
    print()
    print("Features:")
    print("- Online recognition first (Google - highest accuracy)")
    print("- Offline fallback (Sphinx - works without internet)")
    print("- Continuous listening up to 30 seconds")
    print("- ESC key to stop at any time")
    print("- Smart error handling for both services")
    print()

    result = voice_to_text_with_internet_fallback()

    if result:
        print(f"\nFinal result: {result}")
        print("\n✓ Used online service when available, offline as fallback")
    else:
        print("\nNo speech was detected or listening was stopped by user.")
        print("  Make sure you have a working microphone and proper dependencies installed.")


if __name__ == "__main__":
    main()