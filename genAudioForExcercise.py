import re
import os
import asyncio
import edge_tts
import glob

# --- Configuration ---
AUDIO_BASE_DIR = "audio/sentences"
VOICES = {
    'female': "ko-KR-SunHiNeural",  # Female Korean voice
    'male': "ko-KR-InJoonNeural"    # Male Korean voice
}

# Extract sentences with id and completeSentence only
def extract_sentences_with_id(html_content):
    results = []
    # Regex to find each individual exercise object (the content within {...})
    exercise_pattern = re.compile(r'{([\s\S]*?)}', re.MULTILINE)
    # Regex to find the content of the entire exercises array
    exercises_data_pattern = re.compile(r'const exerciseData = ({[\s\S]*?});', re.MULTILINE)
    data_match = exercises_data_pattern.search(html_content)
    if not data_match:
        return []
    js_object_content = data_match.group(1)
    for match in exercise_pattern.finditer(js_object_content):
        exercise_block = match.group(1)
        if 'id:' not in exercise_block or 'completeSentence:' not in exercise_block:
            continue
        # Extract the ID
        id_match = re.search(r'id:\s*"([^"]+)"', exercise_block)
        if not id_match:
            continue
        qid = id_match.group(1)
        # Extract completeSentence
        complete_sentence_match = re.search(r'completeSentence:\s*"([^"]+)"', exercise_block)
        if complete_sentence_match:
            sentence = complete_sentence_match.group(1)
            results.append((qid, sentence))
    return results

async def create_audio(text, filepath, voice):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filepath)
    except Exception as e:
        print(f"Error creating audio for '{text}' ({voice}): {e}")

async def process_html_file(html_file):
    lesson_match = re.search(r'lesson(\d+)', html_file)
    lesson_code = f"lesson{lesson_match.group(1)}" if lesson_match else "lessonX"
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()
    sentences = extract_sentences_with_id(content)
    if not sentences:
        print(f"No completeSentence found in {html_file}")
        return []
    tasks = []
    for qid, sentence in sentences:
        for gender, voice in VOICES.items():
            out_dir = os.path.join(AUDIO_BASE_DIR, gender)
            out_file = os.path.join(out_dir, f"{qid}.mp3")
            if os.path.exists(out_file):
                print(f"[SKIP] {out_file} already exists.")
                continue
            print(f"[GEN] {out_file} ({voice})")
            tasks.append(create_audio(sentence, out_file, voice))
    await asyncio.gather(*tasks)
    return sentences

async def main():
    html_files = sorted(glob.glob("grammar-lesson*-practice.html"))
    if not html_files:
        print("No grammar-lesson*-practice.html files found.")
        return
    all_stats = {}
    for html_file in html_files:
        print(f"\nProcessing {html_file}...")
        sentences = await process_html_file(html_file)
        all_stats[html_file] = len(sentences)
    print("\nSummary:")
    for html_file, count in all_stats.items():
        print(f"{html_file}: {count} completeSentence(s) processed.")
    print("\nDone. Audio files are saved in audio/sentences/male and audio/sentences/female.")

if __name__ == "__main__":
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(main())