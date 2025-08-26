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

        match = re.match(r"(l\d+)-v(\d+)-([A-Za-z0-9]+)\.js", filename)
        if not match:
            print(f"Tên file không hợp lệ: {filename}")
            continue

        lesson_code, part_number, topic = match.groups()
        lesson_code = f"l{lesson_code[1:]}"  # Keep the 'l' prefix

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