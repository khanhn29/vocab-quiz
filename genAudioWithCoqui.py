import re
import os
from TTS.api import TTS

# --- Configuration ---
HTML_FILE = "grammar-exercise.html"
AUDIO_DIR = "audio/sentences"
MODEL_NAME = "tts_models/ko/kss/tacotron2-DDC-GST"

# Hướng dẫn cài đặt:
# pip install TTS
# Lần đầu chạy sẽ tự động tải model, cần internet lần đầu.

def extract_sentences_with_id(html_content):
    """
    Extracts sentence data from the JavaScript exercise object in the HTML file.
    It prioritizes 'completeSentence' and falls back to 'template' and 'solution'.
    """
    results = []
    exercise_pattern = re.compile(r'{([\s\S]*?)}', re.MULTILINE)
    exercises_data_pattern = re.compile(r'const exerciseData = ({[\s\S]*?});', re.MULTILINE)
    data_match = exercises_data_pattern.search(html_content)
    if not data_match:
        return []
    js_object_content = data_match.group(1)
    for match in exercise_pattern.finditer(js_object_content):
        exercise_block = match.group(1)
        if 'id:' not in exercise_block or 'template:' not in exercise_block:
            continue
        id_match = re.search(r'id:\s*"([^"]+)"', exercise_block)
        if not id_match:
            continue
        qid = id_match.group(1)
        sentence = None
        complete_sentence_match = re.search(r'completeSentence:\s*"([^"]+)"', exercise_block)
        if complete_sentence_match:
            sentence = complete_sentence_match.group(1)
        else:
            template_match = re.search(r'template:\s*"([^"]+)"', exercise_block)
            solution_match = re.search(r'solution:\s*\[([^\]]+)\]', exercise_block)
            if template_match and solution_match:
                template = template_match.group(1)
                answers = re.findall(r'"([^"]+)"', solution_match.group(1))
                temp_sentence = template
                for ans in answers:
                    temp_sentence = temp_sentence.replace("__", ans, 1)
                sentence = temp_sentence
        if qid and sentence:
            results.append((qid, sentence))
    return results


def create_audio(text, filepath, tts):
    """Sinh file MP3 cho câu bằng Coqui TTS."""
    try:
        tts.tts_to_file(text=text, file_path=filepath)
    except Exception as e:
        print(f"Lỗi khi tạo audio cho '{text}': {e}")


def main():
    try:
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Không tìm thấy file '{HTML_FILE}'")
        return
    sentences = extract_sentences_with_id(content)
    if not sentences:
        print("Không tìm thấy câu nào. Kiểm tra lại cấu trúc HTML.")
        return
    os.makedirs(AUDIO_DIR, exist_ok=True)
    tts = TTS(MODEL_NAME)
    for qid, sentence in sentences:
        filepath = os.path.join(AUDIO_DIR, f"{qid}.mp3")
        if os.path.exists(filepath):
            print(f"Bỏ qua, đã tồn tại: {filepath}")
            continue
        print(f"Đang tạo audio cho {qid}: '{sentence}'")
        create_audio(sentence, filepath, tts)
    print(f"\nHoàn tất. File audio lưu ở '{AUDIO_DIR}'")

if __name__ == "__main__":
    main()
