
import re

def extract_complete_sentences(html_file):
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Tìm toàn bộ block exerciseData
    match = re.search(r"const\s+exerciseData\s*=\s*{([\s\S]*?)};", content)
    if not match:
        print("Không tìm thấy exerciseData")
        return []

    block = match.group(1)

    # Tìm tất cả các cặp template + solution
    templates = re.findall(r'template:\s*"([^"]+)"', block)
    solutions = re.findall(r'solution:\s*\[([^\]]+)\]', block)

    sentences = []
    for template, sol in zip(templates, solutions):
        # Lấy danh sách đáp án
        answers = re.findall(r'"([^"]+)"', sol)
        sentence = template
        for ans in answers:
            sentence = sentence.replace("__", ans, 1)
        sentences.append(sentence)

    return sentences


if __name__ == "__main__":
    sentences = extract_complete_sentences("grammar-exercise.html")
    for i, s in enumerate(sentences, 1):
        print(f"translation: {s},")
