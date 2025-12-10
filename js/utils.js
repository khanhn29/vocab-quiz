// Utility functions
// Common helper functions used across the application

// Get lesson name from vocabulary file parameter
function getLessonName(vocabFile) {
    const lessonNames = {
        // Bài 1 - Nghề nghiệp và thông tin cá nhân
        'l1-jobs': 'Bài 1 - Nghề nghiệp',
        'l1-personal-info': 'Bài 1 - Thông tin cá nhân',
        'l1-school-terms': 'Bài 1 - Thuật ngữ học đường',
        'l1-countries': 'Bài 1 - Quốc gia (Phần 1)',
        'l1-countries-2': 'Bài 1 - Quốc gia (Phần 2)',
        
        // Bài 2 - Địa điểm và trường học
        'l2-public-places': 'Bài 2 - Địa điểm công cộng',
        'l2-school-facilities': 'Bài 2 - Cơ sở vật chất trường học',
        'l2-classroom-items': 'Bài 2 - Đồ vật trong lớp học',
        'l2-stationery': 'Bài 2 - Văn phòng phẩm',
        
        // Bài 3 - Động từ và hoạt động
        'l3-basic-verbs': 'Bài 3 - Động từ cơ bản',
        'l3-study-verbs': 'Bài 3 - Động từ học tập',
        'l3-adjectives': 'Bài 3 - Tính từ',
        'l3-food-drink': 'Bài 3 - Đồ ăn thức uống',
        'l3-question-words': 'Bài 3 - Từ nghi vấn',
        'l3-places-activities': 'Bài 3 - Địa điểm và hoạt động',
        
        // Bài 4 - Thời gian và số đếm
        'l4-months': 'Bài 4 - Tháng trong năm',
        'l4-years-units': 'Bài 4 - Thời gian theo năm',
        'l4-weekdays': 'Bài 4 - Thứ ngày trong tuần',
        'l4-relativeDays-time': 'Bài 4 - Thời gian tương đối theo ngày',
        'l4-monthsWeeks-time': 'Bài 4 - Thời gian theo Tuần và Tháng',
        'l4-holidays': 'Bài 4 - Ngày lễ và sự kiện',
        'l4-academic': 'Bài 4 - Học tập và công việc',
        'l4-numbers-0-10': 'Bài 4 - Số đếm 0-10',
        'l4-numbers-10-90': 'Bài 4 - Số đếm 10-90',
        'l4-big-numbers': 'Bài 4 - Số lớn',

        // Bài 5 - Hoạt động hằng ngày
        'l5-korean-numbers': 'Bài 5 - Số thuần Hàn',
        'l5-time-of-day': 'Bài 5 - Thời gian trong ngày',
        'l5-daily-activities': 'Bài 5 - Hoạt động hằng ngày',
        'l5-work-study': 'Bài 5 - Công việc và học tập',
        'l5-family-people': 'Bài 5 - Gia đình và con người',
        'l5-technology': 'Bài 5 - Công nghệ và giải trí',

        // Bài 6 - Cuối tuần
        'l6-weekend-activities': 'Bài 6 - Hoạt động cuối tuần',
        'l6-food-items': 'Bài 6 - Đồ ăn thức uống',
        'l6-nature-animals': 'Bài 6 - Thiên nhiên và động vật',
        'l6-music-movies': 'Bài 6 - Âm nhạc và phim ảnh',
        'l6-sports-clothing': 'Bài 6 - Thể thao và quần áo',

        // Bài 7 - Danh từ chỉ đơn vị
        'l7-korean-numbers-units': 'Bài 7 - Số thuần Hàn với đơn vị',
        'l7-unit-counters': 'Bài 7 - Danh từ chỉ đơn vị',
        'l7-clothing-food': 'Bài 7 - Quần áo và thực phẩm',
        'l7-shopping-items': 'Bài 7 - Mua sắm',

        // Bài 8 - Nhà hàng
        'l8-korean-food': 'Bài 8 - Món ăn Hàn Quốc',
        'l8-taste': 'Bài 8 - Mùi vị',
        'l8-restaurant': 'Bài 8 - Quán ăn',
        'l8-new-words-1': 'Bài 8 - Từ mới (Phần 1)',
        'l8-new-words-2': 'Bài 8 - Từ mới (Phần 2)'
    };
    
    return lessonNames[vocabFile] || 'Bài học từ vựng';
}

// Navigate back to index page
function goToIndex() {
    window.location.href = 'index.html';
}

// Parse URL parameters
function getUrlParams() {
    const params = new URLSearchParams(window.location.search);
    return {
        vocab: params.get("vocab"),
        audio: params.get("audio") || 'audio/vocab/female/lesson1' // Default to female voice
    };
}

// Format number with thousand separators
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Shuffle array utility
function shuffleArray(array) {
    const newArray = [...array];
    for (let i = newArray.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
    }
    return newArray;
}

// Create element with attributes and content
function createElement(tag, attributes = {}, content = '') {
    const element = document.createElement(tag);
    
    Object.keys(attributes).forEach(key => {
        if (key === 'className') {
            element.className = attributes[key];
        } else {
            element.setAttribute(key, attributes[key]);
        }
    });
    
    if (content) {
        element.innerHTML = content;
    }
    
    return element;
}

// Add CSS animation styles if not already present
function addAnimationStyles() {
    if (!document.querySelector('#app-animations')) {
        const style = document.createElement('style');
        style.id = 'app-animations';
        style.textContent = `
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            @keyframes bounce {
                0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                40% { transform: translateY(-20px); }
                60% { transform: translateY(-10px); }
            }
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }
            .fade-in { animation: fadeIn 0.5s ease-in; }
            .bounce { animation: bounce 1s ease-in-out; }
            .pulse { animation: pulse 1.5s infinite; }
        `;
        document.head.appendChild(style);
    }
}

// Initialize app animations
addAnimationStyles();

// Make functions globally available
window.getLessonName = getLessonName;
window.goToIndex = goToIndex;
window.getUrlParams = getUrlParams;
window.formatNumber = formatNumber;
window.shuffleArray = shuffleArray;
window.createElement = createElement;
