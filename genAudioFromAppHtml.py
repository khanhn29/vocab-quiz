import re
import os
import asyncio
import edge_tts

APP_HTML = "app.html"
AUDIO_BASE = "audio"
VOICE = "ko-KR-SunHiNeural"

# Regex để lấy các object trong vocabularyData
VOCAB_BLOCK_RE = re.compile(r'vocabularyData\s*=\s*{([\s\S]*?)};', re.MULTILINE)
ENTRY_RE = re.compile(r'"han"\s*:\s*"([^"]+)"')
# Sửa lại regex cho audioPath để match với JavaScript
PATH_RE = re.compile(r'audioPath\s*=\s*params\.get\(["\']audio["\']\)\s*\|\|\s*["\']([^"\']+)["\']')

async def create_audio(text, filepath):
    try:
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(filepath)
    except Exception as e:
        print(f"Lỗi khi tạo audio cho '{text}': {e}")

async def main():
    try:
        with open(APP_HTML, "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        print(f"Không tìm thấy file '{APP_HTML}'")
        return

    # Tìm block vocabularyData
    vocab_block_match = VOCAB_BLOCK_RE.search(html)
    if not vocab_block_match:
        print("Không tìm thấy vocabularyData trong app.html")
        return
    vocab_block = vocab_block_match.group(1)

    # Tìm tất cả từ tiếng Hàn
    han_words = set(ENTRY_RE.findall(vocab_block))
    if not han_words:
        print("Không tìm thấy từ tiếng Hàn nào trong app.html")
        return

    print(f"Tìm thấy {len(han_words)} từ tiếng Hàn:")
    for word in sorted(han_words):
        print(f"  - {word}")

    # Tìm audioPath mặc định
    audio_path_match = PATH_RE.search(html)
    default_audio_path = audio_path_match.group(1) if audio_path_match else "audio/l1/jobs"
    
    # Tạo audio trong thư mục default và các thư mục có sẵn
    audio_dirs_to_check = [default_audio_path]
    
    # Thêm các thư mục audio có sẵn
    for root, dirs, files in os.walk(AUDIO_BASE):
        if any(f.endswith('.mp3') for f in files):
            rel_path = os.path.relpath(root, '.').replace('\\', '/')
            if rel_path not in audio_dirs_to_check:
                audio_dirs_to_check.append(rel_path)

    tasks = []
    created_count = 0
    
    for audio_dir in audio_dirs_to_check:
        os.makedirs(audio_dir, exist_ok=True)
        print(f"\nKiểm tra thư mục: {audio_dir}")
        
        for han_word in han_words:
            audio_file = os.path.join(audio_dir, f"{han_word}.mp3")
            if os.path.exists(audio_file):
                print(f"  Đã tồn tại: {han_word}.mp3")
                continue
            print(f"  Tạo mới: {han_word}.mp3")
            tasks.append(create_audio(han_word, audio_file))
            created_count += 1

    if tasks:
        print(f"\nBắt đầu tạo {len(tasks)} file audio...")
        await asyncio.gather(*tasks)
        print(f"Hoàn tất tạo {created_count} file audio mới.")
    else:
        print("\nTất cả file audio đã tồn tại.")

if __name__ == "__main__":
    asyncio.run(main())
