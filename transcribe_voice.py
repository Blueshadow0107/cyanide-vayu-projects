#!/usr/bin/env python3
"""
Voice Message Transcription Tool
Uses Google Speech Recognition (free tier) via SpeechRecognition library
"""

import speech_recognition as sr
from pydub import AudioSegment
import sys
import os

def transcribe_audio(audio_path):
    """Transcribe audio file to text"""
    
    # Convert OGG/Opus to WAV if needed
    wav_path = audio_path.replace('.ogg', '.wav').replace('.opus', '.wav')
    
    try:
        # Load audio (pydub will try to use ffmpeg if available)
        print(f"🎙️ Loading audio: {audio_path}")
        audio = AudioSegment.from_file(audio_path)
        
        # Export as WAV (16kHz, mono - optimal for speech recognition)
        print("🔄 Converting to WAV format...")
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(wav_path, format="wav")
        
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # Load WAV file
        with sr.AudioFile(wav_path) as source:
            print("🎧 Processing audio...")
            audio_data = recognizer.record(source)
        
        # Transcribe using Google's free API
        print("📝 Transcribing (using Google Speech Recognition)...")
        text = recognizer.recognize_google(audio_data)
        
        # Cleanup temp file
        os.remove(wav_path)
        
        return text
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 If pydub can't read OGG files, install ffmpeg:")
        print("   sudo apt-get install ffmpeg")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default to the voice message we received
        audio_file = "/home/cyanidepopcorn/.openclaw/media/inbound/a5f820d8-4bb5-40cb-9dd4-49693213bddf.ogg"
    else:
        audio_file = sys.argv[1]
    
    if not os.path.exists(audio_file):
        print(f"❌ File not found: {audio_file}")
        sys.exit(1)
    
    result = transcribe_audio(audio_file)
    
    if result:
        print("\n" + "="*50)
        print("📝 TRANSCRIPTION:")
        print("="*50)
        print(result)
        print("="*50)
    else:
        print("❌ Transcription failed")
