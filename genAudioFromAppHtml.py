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
    def __init__(self, html_file_path, output_base_dir="audio"):
        self.html_file_path = html_file_path
        self.output_base_dir = Path(output_base_dir)
        # self.voice = "ko-KR-InJoonNeural"  # Giọng nam tiếng Hàn
        self.voice = "ko-KR-SunHiNeural"  # Giọng nữ tiếng Hàn (thay thế nếu muốn)
        
    def extract_vocabulary_data(self):
        """Trích xuất dữ liệu vocabularyData từ file HTML"""
        try:
            with open(self.html_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Tìm phần vocabularyData bằng regex
            pattern = r'const vocabularyData\s*=\s*({.*?});'
            match = re.search(pattern, content, re.DOTALL)
            
            if not match:
                logger.error("Không tìm thấy vocabularyData trong file HTML")
                return None
            
            # Lấy phần JSON và xử lý để có thể parse
            vocab_str = match.group(1)
            
            # Chuyển đổi JavaScript object thành JSON hợp lệ
            # Thay thế single quotes bằng double quotes
            vocab_str = re.sub(r"'([^']*)':", r'"\1":', vocab_str)
            vocab_str = re.sub(r':\s*"([^"]*)"', r': "\1"', vocab_str)
            vocab_str = re.sub(r'{\s*"vi":', r'{"vi":', vocab_str)
            vocab_str = re.sub(r'"han":\s*"([^"]*)"', r'"han": "\1"', vocab_str)
            
            try:
                vocabulary_data = json.loads(vocab_str)
                logger.info(f"Đã trích xuất thành công {len(vocabulary_data)} bộ từ vựng")
                return vocabulary_data
            except json.JSONDecodeError as e:
                logger.error(f"Lỗi parse JSON: {e}")
                # Fallback: parse thủ công
                return self._manual_parse_vocabulary(content)
                
        except FileNotFoundError:
            logger.error(f"Không tìm thấy file: {self.html_file_path}")
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
        # l1-v1-jobs -> audio/lesson1/jobs
        # l2-v3-classroom -> audio/lesson2/classroom
        
        parts = lesson_key.split('-')
        if len(parts) >= 3:
            lesson_num = parts[0][1:]  # l1 -> 1
            topic = '-'.join(parts[2:])  # v1-jobs -> jobs, hoặc classroom
            
            # Xử lý tên topic
            topic_mapping = {
                'v1-jobs': 'jobs',
                'v2-vocab': 'vocab', 
                'v3-countries': 'countries',
                'v1-places': 'places',
                'v2-school': 'school',
                'v3-classroom': 'classroom',
                'v1-verbs': 'verbs',
                'v2-adjectives': 'adjectives',
                'v3-daily': 'daily',
                'v4-question': 'question',
                'v5-vocab': 'vocab',
                'v1-months': 'months',
                'v2-timeUnitsAndDays': 'timeUnitsAndDays',
                'v3-timeRelative': 'timeRelative',
                'v4-eventsActivities': 'eventsActivities',
                'v5-peopleAndMisc': 'peopleAndMisc',
                'v6-numbersv0': 'numbersv0',
                'v7-numbersv1': 'numbersv1',
                'v8-numbersv2': 'numbersv2',
                'v1-timeOfDay': 'timeOfDay',
                'v2-dailyActivities': 'dailyActivities',
                'v3-vocabulary': 'vocabulary',
                'v4-miscellaneous': 'miscellaneous'
            }
            
            topic_name = topic_mapping.get(f'v{parts[1][1:]}-{parts[2]}', parts[2])
            output_dir = self.output_base_dir / f"lesson{lesson_num}" / topic_name
        else:
            # Fallback nếu format không đúng
            output_dir = self.output_base_dir / lesson_key
        
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

async def main():
    # Cấu hình
    html_file = "app.html"  # Đường dẫn tới file HTML
    output_dir = "audio"    # Thư mục output
    
    # Kiểm tra file HTML tồn tại
    if not os.path.exists(html_file):
        print(f"Lỗi: Không tìm thấy file {html_file}")
        print("Vui lòng đảm bảo file HTML nằm cùng thư mục với script này")
        return
    
    # Tạo generator và chạy
    generator = KoreanAudioGenerator(html_file, output_dir)
    await generator.generate_all_audio()

if __name__ == "__main__":
    print("Chương trình tạo audio tiếng Hàn từ file HTML")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nĐã dừng chương trình")
    except Exception as e:
        print(f"Lỗi: {e}")