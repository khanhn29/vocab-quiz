#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import os
import asyncio
import edge_tts
from pathlib import Path
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KoreanAudioGenerator:
    def __init__(self, vocab_js_path, output_base_dir="audio"):
        self.vocab_js_path = vocab_js_path
        self.output_base_dir = Path(output_base_dir)
        # self.voice = "ko-KR-InJoonNeural"  # Giọng nam tiếng Hàn
        self.voice = "ko-KR-SunHiNeural"  # Giọng nữ tiếng Hàn (thay thế nếu muốn)
        
    def extract_vocabulary_data(self):
        """Trích xuất dữ liệu vocabularyData từ file vocabulary-data.js"""
        try:
            with open(self.vocab_js_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Tìm phần vocabularyData bằng regex
            pattern = r'const vocabularyData\s*=\s*({.*?});'
            match = re.search(pattern, content, re.DOTALL)
            
            if not match:
                logger.error("Không tìm thấy vocabularyData trong file JavaScript")
                return None
            
            # Lấy phần JSON và xử lý để có thể parse
            vocab_str = match.group(1)
            
            # Chuyển đổi JavaScript object thành JSON hợp lệ một cách tốt hơn
            # Xử lý comments trước
            vocab_str = re.sub(r'//.*?$', '', vocab_str, flags=re.MULTILINE)
            
            # Thay thế single quotes bằng double quotes cho keys
            vocab_str = re.sub(r"'([^']*)':", r'"\1":', vocab_str)
            
            # Xử lý trailing comma
            vocab_str = re.sub(r',(\s*[}\]])', r'\1', vocab_str)
            
            try:
                vocabulary_data = json.loads(vocab_str)
                logger.info(f"Đã trích xuất thành công {len(vocabulary_data)} bộ từ vựng")
                
                # Log thông tin chi tiết
                total_words = sum(len(words) for words in vocabulary_data.values())
                logger.info(f"Tổng số từ vựng: {total_words}")
                
                return vocabulary_data
            except json.JSONDecodeError as e:
                logger.error(f"Lỗi parse JSON: {e}")
                logger.error(f"JSON string preview: {vocab_str[:500]}...")
                # Fallback: parse thủ công
                return self._manual_parse_vocabulary(content)
                
        except FileNotFoundError:
            logger.error(f"Không tìm thấy file: {self.vocab_js_path}")
            return None
        except Exception as e:
            logger.error(f"Lỗi đọc file: {e}")
            return None
    
    def _manual_parse_vocabulary(self, content):
        """Parse thủ công nếu JSON parser thất bại"""
        vocabulary_data = {}
        
        # Tìm tất cả các lesson
        lesson_pattern = r"'([^']+)':\s*\[(.*?)\]"
        lessons = re.findall(lesson_pattern, content, re.DOTALL)
        
        for lesson_key, lesson_content in lessons:
            if lesson_key.startswith('l') and '-' in lesson_key:  # Filter lesson keys
                words = []
                # Tìm tất cả các từ trong lesson
                word_pattern = r'{\s*"vi":\s*"([^"]+)",\s*"han":\s*"([^"]+)"\s*}'
                word_matches = re.findall(word_pattern, lesson_content)
                
                for vi, han in word_matches:
                    words.append({"vi": vi, "han": han})
                
                if words:
                    vocabulary_data[lesson_key] = words
                    logger.info(f"Lesson {lesson_key}: {len(words)} từ")
        
        return vocabulary_data
    
    def create_directory_structure(self, lesson_key):
        """Tạo cấu trúc thư mục cho lesson"""
        # Chuyển đổi lesson key thành path
        # l1-jobs -> audio/vocab/lesson1
        # l2-classroom -> audio/vocab/lesson2
        
        parts = lesson_key.split('-')
        if len(parts) >= 2:
            lesson_num = parts[0][1:]  # l1 -> 1
            output_dir = self.output_base_dir / "vocab" / f"lesson{lesson_num}"
        else:
            # Fallback nếu format không đúng
            output_dir = self.output_base_dir / "vocab" / lesson_key
        
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    async def generate_audio_file(self, korean_text, output_path):
        """Tạo file audio từ text tiếng Hàn"""
        try:
            # Tạo TTS
            communicate = edge_tts.Communicate(korean_text, self.voice)
            
            # Lưu file
            await communicate.save(str(output_path))
            logger.info(f"Đã tạo audio: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi tạo audio cho '{korean_text}': {e}")
            return False
    
    def sanitize_filename(self, filename):
        """Làm sạch tên file, loại bỏ ký tự không hợp lệ"""
        # Loại bỏ ký tự đặc biệt, giữ lại ký tự Hàn Quốc
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        return sanitized.strip()
    
    async def process_lesson(self, lesson_key, words):
        """Xử lý một lesson"""
        logger.info(f"Đang xử lý lesson: {lesson_key} ({len(words)} từ)")
        
        # Tạo thư mục
        output_dir = self.create_directory_structure(lesson_key)
        logger.info(f"Thư mục output: {output_dir}")
        
        # Tạo audio cho từng từ
        success_count = 0
        for i, word in enumerate(words, 1):
            korean_word = word['han']
            vietnamese_word = word['vi']
            
            # Tạo tên file từ từ tiếng Hàn
            filename = self.sanitize_filename(korean_word) + '.mp3'
            output_path = output_dir / filename
            
            # Kiểm tra file đã tồn tại chưa
            if output_path.exists():
                logger.info(f"File đã tồn tại: {output_path}")
                success_count += 1
                continue
            
            # Tạo audio
            logger.info(f"[{i}/{len(words)}] Tạo audio: {korean_word} ({vietnamese_word})")
            
            if await self.generate_audio_file(korean_word, output_path):
                success_count += 1
            
            # Nghỉ ngắn để tránh spam API
            await asyncio.sleep(0.1)
        
        logger.info(f"Hoàn thành lesson {lesson_key}: {success_count}/{len(words)} file")
        return success_count
    
    async def generate_all_audio(self):
        """Tạo audio cho tất cả từ vựng"""
        # Trích xuất dữ liệu
        vocabulary_data = self.extract_vocabulary_data()
        if not vocabulary_data:
            logger.error("Không thể trích xuất dữ liệu từ vựng")
            return
        
        # Tạo thư mục gốc
        self.output_base_dir.mkdir(exist_ok=True)
        
        total_lessons = len(vocabulary_data)
        total_words = sum(len(words) for words in vocabulary_data.values())
        
        logger.info(f"Bắt đầu tạo audio cho {total_lessons} lessons, {total_words} từ")
        
        # Xử lý từng lesson
        total_success = 0
        for lesson_key, words in vocabulary_data.items():
            success_count = await self.process_lesson(lesson_key, words)
            total_success += success_count
        
        logger.info(f"Hoàn thành! Đã tạo {total_success}/{total_words} file audio")

    async def generate_specific_lesson(self, lesson_keys):
        """Tạo audio cho các lesson cụ thể"""
        vocabulary_data = self.extract_vocabulary_data()
        if not vocabulary_data:
            logger.error("Không thể trích xuất dữ liệu từ vựng")
            return
        
        # Filter theo lesson keys
        filtered_data = {k: v for k, v in vocabulary_data.items() if k in lesson_keys}
        
        if not filtered_data:
            logger.error(f"Không tìm thấy lesson nào trong: {lesson_keys}")
            return
        
        total_words = sum(len(words) for words in filtered_data.values())
        logger.info(f"Tạo audio cho {len(filtered_data)} lessons, {total_words} từ")
        
        # Xử lý từng lesson
        total_success = 0
        for lesson_key, words in filtered_data.items():
            success_count = await self.process_lesson(lesson_key, words)
            total_success += success_count
        
        logger.info(f"Hoàn thành! Đã tạo {total_success}/{total_words} file audio")

async def main():
    # Cấu hình
    vocab_js_file = "js/vocabulary-data.js"  # Đường dẫn tới file vocabulary-data.js
    output_dir = "audio"                     # Thư mục output
    
    # Kiểm tra file JavaScript tồn tại
    if not os.path.exists(vocab_js_file):
        print(f"Lỗi: Không tìm thấy file {vocab_js_file}")
        print("Vui lòng đảm bảo file vocabulary-data.js nằm trong thư mục js/")
        return
    
    # Tạo generator và chạy
    generator = KoreanAudioGenerator(vocab_js_file, output_dir)
    
    # Cho phép chọn lesson cụ thể
    print("Tùy chọn:")
    print("1. Tạo audio cho tất cả lessons")
    print("2. Tạo audio cho lesson cụ thể")
    
    choice = input("Chọn (1/2): ").strip()
    
    if choice == "2":
        print("\nCác lesson có sẵn:")
        vocabulary_data = generator.extract_vocabulary_data()
        if vocabulary_data:
            for i, key in enumerate(vocabulary_data.keys(), 1):
                word_count = len(vocabulary_data[key])
                print(f"{i}. {key} ({word_count} từ)")
            
            lesson_input = input("\nNhập lesson keys (cách nhau bởi dấu phẩy): ").strip()
            lesson_keys = [key.strip() for key in lesson_input.split(',')]
            
            await generator.generate_specific_lesson(lesson_keys)
        else:
            print("Không thể đọc dữ liệu từ vựng")
    else:
        await generator.generate_all_audio()

if __name__ == "__main__":
    print("Chương trình tạo audio tiếng Hàn từ file vocabulary-data.js")
    print("=" * 60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nĐã dừng chương trình")
    except Exception as e:
        print(f"Lỗi: {e}")
