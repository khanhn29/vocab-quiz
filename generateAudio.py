import os
import json
import re
import asyncio
import edge_tts

DATA_DIR = 'data'
AUDIO_DIR = 'audio'
VOICE = "ko-KR-SunHiNeural"

# Bảng ánh xạ topic -> tiếng Việt
TOPIC_VI = {
    "NgheNghiep": "Nghề nghiệp",
    "TuMoi": "Từ mới",
    "QuocGia": "Quốc gia",
    "NoiChon": "Nơi chốn",
    "TrangThietBiTruongHoc": "Thiết bị trường học",
    "DoVatTrongPhongHoc": "Đồ vật trong phòng học",
    "DongTu": "Động từ",
    "TinhTu": "Tính từ",
    "SinhHoatHangNgay": "Sinh hoạt hằng ngày",
    "DaiTuNghiVan": "Đại từ nghi vấn"
}

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
    html_cards = []

    for filename in os.listdir(DATA_DIR):
        if not filename.endswith(".js"):
            continue

        match = re.match(r"(sc\d+b\d+)_([0-9]+)([A-Za-z0-9]+)\.js", filename)
        if not match:
            print(f"Tên file không hợp lệ: {filename}")
            continue

        lesson_code, part_number, topic = match.groups()
        topic_vi = TOPIC_VI.get(topic, topic)

        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            vocab_list = extract_vocabulary(content)

        # Tạo thư mục output
        output_dir = os.path.join(AUDIO_DIR, lesson_code, topic)
        os.makedirs(output_dir, exist_ok=True)

        audio_created = False

        for entry in vocab_list:
            han_word = entry.get("han")
            if not han_word:
                continue
            output_file = os.path.join(output_dir, f"{han_word}.mp3")
            if not os.path.exists(output_file):
                print(f"Đang tạo {output_file}...")
                await create_audio(han_word, output_file)
                audio_created = True
            else:
                print(f"Đã tồn tại {output_file}")

        # Nếu có ít nhất một file audio được tạo hoặc tồn tại → in ra thẻ HTML
        if os.listdir(output_dir):
            html = f'''<div class="card">
  <a href="app.html?vocab={filename[:-3]}&audio=audio/{lesson_code}/{topic}">
    <div class="card-title">Phần {part_number}: {topic_vi}</div>
  </a>
</div>'''
            html_cards.append(html)

    print("\n<!-- Các thẻ card được tạo từ các file có audio -->\n")
    print("\n".join(html_cards))

if __name__ == "__main__":
    asyncio.run(main())
