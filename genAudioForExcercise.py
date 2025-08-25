import re
import os
import asyncio
import edge_tts

# --- Configuration ---
HTML_FILE = "grammar-exercise.html"
AUDIO_DIR = "audio/sentences"
VOICE = "ko-KR-SunHiNeural"

def extract_sentences_with_id(html_content):
    """
    Extracts sentence data from the JavaScript exercise object in the HTML file.
    It prioritizes 'completeSentence' and falls back to 'template' and 'solution'.
    """
    results = []
    
    # Regex to find each individual exercise object (the content within {...})
    exercise_pattern = re.compile(r'{([\s\S]*?)}', re.MULTILINE)
    
    # Regex to find the content of the entire exercises array to avoid matching other objects
    exercises_data_pattern = re.compile(r'const exerciseData = ({[\s\S]*?});', re.MULTILINE)
    
    data_match = exercises_data_pattern.search(html_content)
    if not data_match:
        return []
        
    js_object_content = data_match.group(1)

    for match in exercise_pattern.finditer(js_object_content):
        exercise_block = match.group(1)
        
        # Ensure we are only matching blocks inside the 'exercises' array
        if 'id:' not in exercise_block or 'template:' not in exercise_block:
            continue

        # Extract the ID
        id_match = re.search(r'id:\s*"([^"]+)"', exercise_block)
        if not id_match:
            continue
        
        qid = id_match.group(1)
        sentence = None

        # 1. Prioritize 'completeSentence'
        complete_sentence_match = re.search(r'completeSentence:\s*"([^"]+)"', exercise_block)
        if complete_sentence_match:
            sentence = complete_sentence_match.group(1)
        else:
            # 2. Fallback to 'template' and 'solution'
            template_match = re.search(r'template:\s*"([^"]+)"', exercise_block)
            solution_match = re.search(r'solution:\s*\[([^\]]+)\]', exercise_block)
            
            if template_match and solution_match:
                template = template_match.group(1)
                # Extract all answers from the solution array string
                answers = re.findall(r'"([^"]+)"', solution_match.group(1))
                
                # Sequentially replace blanks with answers
                temp_sentence = template
                for ans in answers:
                    temp_sentence = temp_sentence.replace("__", ans, 1)
                sentence = temp_sentence
        
        if qid and sentence:
            results.append((qid, sentence))
            
    return results


async def create_audio(text, filepath):
    """Generates an MP3 file for the given text using the specified voice."""
    try:
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(filepath)
    except Exception as e:
        print(f"Error creating audio for '{text}': {e}")


async def main():
    """Main function to extract sentences and generate audio files."""
    try:
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{HTML_FILE}' was not found.")
        return

    sentences = extract_sentences_with_id(content)
    if not sentences:
        print("No sentences were extracted. Please check the HTML file structure.")
        return

    os.makedirs(AUDIO_DIR, exist_ok=True)
    
    tasks = []
    for qid, sentence in sentences:
        filepath = os.path.join(AUDIO_DIR, f"{qid}.mp3")
        if os.path.exists(filepath):
            print(f"Skipping, already exists: {filepath}")
            continue
        print(f"Generating audio for {qid}: \"{sentence}\"")
        tasks.append(create_audio(sentence, filepath))

    await asyncio.gather(*tasks)

    print(f"\nProcessing complete. Audio files are saved in the '{AUDIO_DIR}' directory.")


if __name__ == "__main__":
    # Ensure we have a fresh event loop if running in certain environments like Jupyter
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(main())