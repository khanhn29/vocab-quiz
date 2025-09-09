import os
import json
import re
import asyncio
import edge_tts

VOCAB_DATA_FILE = 'js/vocabulary-data.js'
AUDIO_DIR = 'audio'

# Voice configuration for male and female
VOICES = {
    'female': "ko-KR-SunHiNeural",  # Female Korean voice
    'male': "ko-KR-InJoonNeural"    # Male Korean voice
}

# Extract vocabulary data from the vocabularyData object
def extract_vocabulary_data(js_content):
    """Extract vocabularyData object from vocabulary-data.js"""
    try:
        # Find the vocabularyData object
        pattern = r'const vocabularyData\s*=\s*(\{[\s\S]*?\});'
        match = re.search(pattern, js_content)
        
        if not match:
            print("❌ Không tìm thấy vocabularyData trong file")
            return {}
        
        vocab_str = match.group(1)
        
        # Remove comments
        vocab_str = re.sub(r'//.*?$', '', vocab_str, flags=re.MULTILINE)
        
        # Convert JavaScript object to JSON format
        # Replace single quotes with double quotes for keys and values
        vocab_str = re.sub(r"'([^']*)':", r'"\1":', vocab_str)
        vocab_str = re.sub(r':\s*\'([^\']*?)\'', r': "\1"', vocab_str)
        
        # Remove trailing commas
        vocab_str = re.sub(r',(\s*[}\]])', r'\1', vocab_str)
        
        # Parse the JSON
        vocab_data = json.loads(vocab_str)
        return vocab_data
        
    except json.JSONDecodeError as e:
        print(f"❌ Lỗi parse JSON: {e}")
        return {}
    except Exception as e:
        print(f"❌ Lỗi extract vocabulary: {e}")
        return {}

# Tạo file âm thanh
async def create_audio(text, filepath, voice):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filepath)
        return True
    except Exception as e:
        print(f"Lỗi tạo audio {filepath}: {e}")
        return False

# Main
async def main():
    total_created = 0
    total_existing = 0

    print("🎤 Tạo Audio Tiếng Hàn với Giọng Nam và Nữ")
    print("=" * 50)

    # Read vocabulary data from vocabulary-data.js
    if not os.path.exists(VOCAB_DATA_FILE):
        print(f"❌ Không tìm thấy file: {VOCAB_DATA_FILE}")
        return

    print(f"📖 Đọc dữ liệu từ: {VOCAB_DATA_FILE}")
    
    with open(VOCAB_DATA_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        vocab_data = extract_vocabulary_data(content)

    if not vocab_data:
        print("❌ Không thể trích xuất dữ liệu từ vựng")
        return

    print(f"📚 Tìm thấy {len(vocab_data)} nhóm từ vựng")

    # Process each vocabulary group
    for topic_key, vocab_list in vocab_data.items():
        if not isinstance(vocab_list, list):
            continue
            
        print(f"\n� Xử lý nhóm: {topic_key}")
        print(f"   📋 Số từ vựng: {len(vocab_list)}")

        # Extract lesson number from topic key (e.g., 'l1-jobs' -> 'lesson1')
        lesson_match = re.match(r'l(\d+)', topic_key)
        if lesson_match:
            lesson_num = lesson_match.group(1)
            lesson_code = f"lesson{lesson_num}"
        else:
            lesson_code = topic_key  # fallback to original key

        # Tạo audio cho cả giọng nam và nữ
        for voice_type, voice in VOICES.items():
            print(f"   🎵 Tạo giọng {voice_type} ({voice})")
            
            output_dir = os.path.join(AUDIO_DIR, 'vocab', voice_type, lesson_code)
            os.makedirs(output_dir, exist_ok=True)

            for entry in vocab_list:
                if not isinstance(entry, dict):
                    continue
                    
                han_word = entry.get("han")
                if not han_word:
                    continue
                    
                output_file = os.path.join(output_dir, f"{han_word}.mp3")
                
                if os.path.exists(output_file):
                    total_existing += 1
                    print(f"      ✅ Đã có: {han_word}.mp3")
                else:
                    print(f"      🔄 Tạo: {han_word}.mp3")
                    success = await create_audio(han_word, output_file, voice)
                    if success:
                        total_created += 1
                        print(f"      ✨ Hoàn thành: {han_word}.mp3")
                    else:
                        print(f"      ❌ Thất bại: {han_word}.mp3")
    print("\n" + "="*70)
    print("📊 THỐNG KÊ TỔNG KẾT")
    print("="*70)
    print(f"✨ File âm thanh mới tạo: {total_created}")
    print(f"✅ File âm thanh đã có: {total_existing}")
    
    print(f"\n🎭 Cấu trúc thư mục audio:")
    print(f"audio/vocab/female/  - Giọng nữ (ko-KR-SunHiNeural)")
    print(f"audio/vocab/male/    - Giọng nam (ko-KR-InJoonNeural)")
    
    print(f"\n🎵 Tính năng: Audio được tạo cho cả giọng nam và nữ!")
    print("📁 Các thư mục được tạo:")
    
    # List generated directories
    vocab_dir = os.path.join(AUDIO_DIR, 'vocab')
    if os.path.exists(vocab_dir):
        for voice_type in ['female', 'male']:
            voice_dir = os.path.join(vocab_dir, voice_type)
            if os.path.exists(voice_dir):
                lessons = [d for d in os.listdir(voice_dir) if os.path.isdir(os.path.join(voice_dir, d))]
                print(f"   📂 {voice_type}: {', '.join(sorted(lessons))}")

if __name__ == "__main__":
    asyncio.run(main())
