import os
import asyncio
import edge_tts
from bs4 import BeautifulSoup

# Voice configuration
VOICES = {
    'female': "ko-KR-SunHiNeural",  # Female Korean voice
    'male': "ko-KR-InJoonNeural"    # Male Korean voice
}

# HTML file and output directory
HTML_FILE = 'grammar-lesson6-listen.html'
OUTPUT_BASE_DIR = 'audio/listen/lesson6'

async def create_audio(text, filepath, voice):
    """Create audio file from text using specified voice"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Create and save audio
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filepath)
        return True
    except Exception as e:
        print(f"Error creating audio {filepath}: {e}")
        return False

async def main():
    total_created = 0
    total_existing = 0

    print("🎤 Creating Audio Files for Korean Listening Exercise")
    print("=" * 50)

    # Read HTML file
    if not os.path.exists(HTML_FILE):
        print(f"❌ HTML file not found: {HTML_FILE}")
        return

    print(f"📖 Reading from: {HTML_FILE}")
    
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # Find all Korean text spans within korean-text divs
    korean_texts = soup.find_all('div', class_='korean-text')
    
    if not korean_texts:
        print("❌ No Korean text found in HTML")
        return

    print(f"📚 Found {len(korean_texts)} Korean text entries")

    # Process each Korean text for both voices
    for idx, korean_div in enumerate(korean_texts, 1):
        # Get the text from span element only
        span = korean_div.find('span')
        if not span:
            print(f"   ⚠️ No span found in entry {idx}, skipping...")
            continue
            
        # Get text and replace <br> with space
        text = span.get_text(strip=True)
        text = text.replace('\n', ' ')  # Replace any newlines with space
        audio_id = f"lesson6_{idx}"
        
        print(f"\n🔊 Processing text {idx}: {text}")

        # Generate audio for both male and female voices
        for voice_type, voice in VOICES.items():
            output_dir = os.path.join(OUTPUT_BASE_DIR, voice_type)
            output_file = os.path.join(output_dir, f"{audio_id}.mp3")
            
            if os.path.exists(output_file):
                total_existing += 1
                print(f"   ✅ Already exists: {voice_type}/{audio_id}.mp3")
            else:
                print(f"   🔄 Creating: {voice_type}/{audio_id}.mp3")
                success = await create_audio(text, output_file, voice)
                if success:
                    total_created += 1
                    print(f"   ✨ Completed: {voice_type}/{audio_id}.mp3")
                else:
                    print(f"   ❌ Failed: {voice_type}/{audio_id}.mp3")

    print("\n" + "="*50)
    print("📊 SUMMARY")
    print("="*50)
    print(f"✨ New audio files created: {total_created}")
    print(f"✅ Existing audio files: {total_existing}")
    
    print(f"\n🎭 Audio directory structure:")
    print(f"{OUTPUT_BASE_DIR}/")
    print(f"  ├── female/  - Female voice (ko-KR-SunHiNeural)")
    print(f"  └── male/    - Male voice (ko-KR-InJoonNeural)")

if __name__ == "__main__":
    asyncio.run(main())