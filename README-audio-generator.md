# Audio Generator for Korean Vocabulary

## Tổng quan

Script Python này tự động tạo file audio tiếng Hàn từ dữ liệu từ vựng trong file `js/vocabulary-data.js`.

## Thay đổi từ phiên bản cũ

### ✅ **Cải tiến:**
- **Đọc từ file riêng biệt**: Thay vì parse từ HTML, giờ đọc trực tiếp từ `vocabulary-data.js`
- **Parser tốt hơn**: Xử lý JavaScript object syntax chính xác hơn
- **Chọn lesson cụ thể**: Có thể tạo audio cho lesson cụ thể thay vì tất cả
- **Logging chi tiết**: Hiển thị tiến trình rõ ràng hơn
- **Error handling**: Xử lý lỗi tốt hơn

### 📁 **File structure:**
```
vocab-quiz/
├── genAudioFromVocabData.py (file mới)
├── genAudioFromAppHtml.py   (file cũ - có thể xóa)
├── js/
│   └── vocabulary-data.js   (nguồn dữ liệu)
└── audio/
    └── vocab/
        ├── lesson1/
        ├── lesson2/
        └── ...
```

## Cài đặt

### 1. Cài đặt dependencies:
```bash
pip install edge-tts
```

### 2. Kiểm tra structure:
Đảm bảo có file `js/vocabulary-data.js` trong cùng thư mục

## Sử dụng

### Chạy script:
```bash
python genAudioFromVocabData.py
```

### Tùy chọn:
1. **Tạo audio cho tất cả lessons**: Tạo audio cho tất cả từ vựng
2. **Tạo audio cho lesson cụ thể**: Chọn lesson nào cần tạo

### Ví dụ sử dụng:

```
Chọn (1/2): 2

Các lesson có sẵn:
1. l1-jobs (8 từ)
2. l1-personal-info (13 từ)
3. l1-school-terms (10 từ)
...

Nhập lesson keys (cách nhau bởi dấu phẩy): l1-jobs
```

## Output Structure

Audio files sẽ được tạo theo cấu trúc:

```
audio/
└── vocab/
    ├── lesson1/
    │   ├── 은행원.mp3
    │   ├── 공무원.mp3
    │   └── ...
    ├── lesson5/
    │   ├── 가족.mp3
    │   ├── 아버지.mp3
    │   └── ...
    └── ...
```

## Features

### ✨ **Smart Features:**
- **Skip existing files**: Không tạo lại file đã tồn tại
- **Sanitize filenames**: Tự động làm sạch tên file
- **Progress tracking**: Hiển thị tiến trình chi tiết
- **Error recovery**: Tiếp tục với file khác nếu có lỗi

### 🎙️ **Audio Quality:**
- **Voice**: `ko-KR-SunHiNeural` (giọng nữ tiếng Hàn)
- **Format**: MP3
- **Quality**: Edge TTS standard quality

### 📊 **Statistics:**
- Tổng số lessons được xử lý
- Tổng số từ vựng
- Số file thành công/thất bại
- Thời gian xử lý

## Troubleshooting

### Lỗi thường gặp:

1. **"Không tìm thấy file js/vocabulary-data.js"**
   - Đảm bảo chạy script từ thư mục gốc của project
   - Kiểm tra file `vocabulary-data.js` có tồn tại

2. **"Lỗi parse JSON"**
   - Kiểm tra syntax trong `vocabulary-data.js`
   - Script sẽ tự động fallback sang manual parsing

3. **"Lỗi tạo audio"**
   - Kiểm tra kết nối internet
   - Edge TTS cần internet để hoạt động

### Debug:
Script có logging chi tiết, check console output để debug.

## Migration từ script cũ

### Từ `genAudioFromAppHtml.py`:
1. Dừng sử dụng script cũ
2. Sử dụng `genAudioFromVocabData.py` mới
3. Audio output structure giống hệt nhau
4. Có thể xóa script cũ sau khi test

### Benefits của script mới:
- ⚡ **Nhanh hơn**: Không cần parse HTML lớn
- 🎯 **Chính xác hơn**: Đọc trực tiếp từ source data
- 🔧 **Dễ maintain**: Tách biệt data và logic
- 📈 **Scalable**: Dễ thêm features mới

## Future Enhancements

Có thể mở rộng:
- Multiple voices support
- Audio quality options  
- Batch processing
- API integration
- Progress bar GUI
