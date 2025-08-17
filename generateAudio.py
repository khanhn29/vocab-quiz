"""
Công cụ tự động tạo file âm thanh cho từ vựng tiếng Hàn
===================================================

Các bước chuẩn bị trước khi chạy:
1. Cài đặt Python 3.x
2. Cài đặt thư viện edge-tts:
   pip install edge-tts

3. Chuẩn bị file dữ liệu:
   - Tạo file .js trong thư mục data/
   - Đặt tên theo format: sc[số]b[số]_[số][Chủ đề].js
     Ví dụ: sc1b1_1NgheNghiep.js
   
   - Nội dung file phải có cấu trúc:
     const vocabulary = [
         {
             "han": "한국어",  // Từ tiếng Hàn cần tạo âm thanh
             // ... các thông tin khác
         }
     ];

4. Cấu trúc thư mục:
   vocab-quiz/
   ├── data/           # Chứa file .js
   └── audio/         # Nơi lưu file âm thanh (tự động tạo)

5. Chạy script:
   python generateAudio.py

Kết quả:
- Tạo file .mp3 trong thư mục audio/
- In ra console các đường dẫn app.html
"""

import os
import json
import re
import asyncio
import edge_tts

DATA_DIR = 'data'
AUDIO_DIR = 'audio'
VOICE = "ko-KR-SunHiNeural"

# Trích xuất danh sách từ vựng
def extract_vocabulary(js_content):
    match = re.search(r'const\s+vocabulary\s*=\s*(\[[\s\S]*?\]);', js_content)
    if match:
        array_str = match.group(1)
        try:
            json_str = array_str.replace("'", '"')
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print("Lỗi parse JSON:", e)
    return []

# Tạo file âm thanh
async def create_audio(text, filepath):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(filepath)

# Main
async def main():
    paths = []

    for filename in os.listdir(DATA_DIR):
        if not filename.endswith(".js"):
            continue

        match = re.match(r"(sc\d+b\d+)_([0-9]+)([A-Za-z0-9]+)\.js", filename)
        if not match:
            print(f"Tên file không hợp lệ: {filename}")
            continue

        lesson_code, part_number, topic = match.groups()

        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            vocab_list = extract_vocabulary(content)

        # Tạo thư mục output
        output_dir = os.path.join(AUDIO_DIR, lesson_code, topic)
        os.makedirs(output_dir, exist_ok=True)

        for entry in vocab_list:
            han_word = entry.get("han")
            if not han_word:
                continue
            output_file = os.path.join(output_dir, f"{han_word}.mp3")
            if not os.path.exists(output_file):
                print(f"Đang tạo {output_file}...")
                await create_audio(han_word, output_file)
            else:
                print(f"Đã tồn tại {output_file}")

        # Nếu có file audio được tạo hoặc tồn tại → tạo path
        if os.listdir(output_dir):
            path = f"app.html?vocab={filename[:-3]}&audio=audio/{lesson_code}/{topic}"
            paths.append(path)

    print("\n" + "="*50)
    print("Các đường dẫn được tạo:")
    print("="*50)
    for path in paths:
        print(path)

if __name__ == "__main__":
    asyncio.run(main())