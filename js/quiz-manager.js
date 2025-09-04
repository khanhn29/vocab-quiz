// Quiz Logic Module
// Core quiz functionality and state management

class QuizManager {
    constructor() {
        this.vocabulary = [];
        this.currentQuestion = null;
        this.correctAnswer = null;
        this.hasAnswered = false;
        this.currentAnswers = [];
        this.questionQueue = [];
        this.currentQuestionIndex = 0;
        this.totalQuestions = 0;
        this.wrongAnswerCount = 0;
        this.correctAnswerCount = 0;
        this.completedWords = new Set();
        this.wordProgress = {};
        
        // Detailed statistics
        this.detailedStats = {
            totalOriginalQuestions: 0,
            totalQuestionsAnswered: 0,
            correctOnFirstTry: 0,
            retryCount: 0,
            wordAttempts: {},
            difficultWords: [],
            perfectWords: [],
            masteredWords: 0
        };
    }

    // Initialize quiz with vocabulary data
    init(vocabKey, audioPath) {
        console.log('Initializing quiz...');
        
        if (!window.vocabularyData || !window.vocabularyData[vocabKey]) {
            console.error('Vocabulary data not found for:', vocabKey);
            this.showError('Không tìm thấy dữ liệu từ vựng!');
            return;
        }
        
        this.vocabulary = window.vocabularyData[vocabKey];
        window.audioManager.setAudioPath(audioPath);
        
        this.setupQuestionQueue();
        this.loadNewQuestion();
        this.setupEventListeners();
    }

    // Create question queue
    setupQuestionQueue() {
        this.questionQueue = [];
        this.completedWords.clear();
        this.wordProgress = {};
        
        // Reset detailed stats
        this.detailedStats = {
            totalOriginalQuestions: this.vocabulary.length * 2,
            totalQuestionsAnswered: 0,
            correctOnFirstTry: 0,
            retryCount: 0,
            wordAttempts: {},
            difficultWords: [],
            perfectWords: [],
            masteredWords: 0
        };
        
        // Initialize word progress and attempts
        this.vocabulary.forEach((word, index) => {
            this.wordProgress[index] = { krVn: false, vnKr: false };
            this.detailedStats.wordAttempts[index] = { krVn: 0, vnKr: 0 };
        });
        
        // Create questions: each word gets 2 questions (KR->VN and VN->KR)
        this.vocabulary.forEach((word, index) => {
            this.questionQueue.push({...word, type: 'kr-vn', wordIndex: index, isRetry: false});
            this.questionQueue.push({...word, type: 'vn-kr', wordIndex: index, isRetry: false});
        });
        
        // Shuffle all questions
        this.questionQueue = this.shuffleArray(this.questionQueue);
        this.totalQuestions = this.questionQueue.length;
        this.currentQuestionIndex = 0;
        
        console.log('Total original questions:', this.totalQuestions);
        console.log('Vocabulary count:', this.vocabulary.length);
        console.log('Shuffled question list:', this.questionQueue.map((q, i) => `${i+1}. ${q.type}: ${q.vi} ↔ ${q.han}`));
        
        this.updateQuestionCounter();
    }

    // Setup event listeners
    setupEventListeners() {
        // Next button
        document.getElementById('nextBtn').addEventListener('click', () => this.loadNewQuestion());
        
        // Option buttons
        for (let i = 0; i < 4; i++) {
            document.getElementById('option' + i).addEventListener('click', () => {
                console.log('Clicked option', i, 'with text:', this.currentAnswers[i]);
                this.selectAnswer(i, this.currentAnswers[i]);
            });
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (event) => {
            if (this.hasAnswered && event.key === 'Enter') {
                this.loadNewQuestion();
            } else if (!this.hasAnswered && event.key >= '1' && event.key <= '4') {
                const optionIndex = parseInt(event.key) - 1;
                this.selectAnswer(optionIndex, this.currentAnswers[optionIndex]);
            }
        });
    }

    // Load new question
    loadNewQuestion() {
        console.log('Loading new question...');
        
        // Stop current audio
        window.audioManager.stop();
        
        // Check if we have more questions
        if (this.currentQuestionIndex >= this.questionQueue.length) {
            this.showCompletionMessage();
            return;
        }
        
        // Reset state
        this.hasAnswered = false;
        document.getElementById('feedback').textContent = '';
        document.getElementById('feedback').className = 'feedback';
        document.getElementById('nextBtn').disabled = true;
        
        // Reset audio button
        const audioButton = document.getElementById('audioButton');
        if (audioButton) {
            audioButton.classList.remove('playing', 'disabled');
            audioButton.style.pointerEvents = 'auto';
        }
        
        // Reset options
        for (let i = 0; i < 4; i++) {
            const option = document.getElementById('option' + i);
            option.className = 'option';
            
            // Remove existing icons
            const existingIcons = option.querySelectorAll('.check-mark, .x-mark');
            existingIcons.forEach(icon => icon.remove());
        }
        
        // Get question from queue
        this.currentQuestion = this.questionQueue[this.currentQuestionIndex];
        window.currentQuestion = this.currentQuestion; // For global access
        
        const vietnameseElement = document.getElementById('vietnameseWord');
        
        if (this.currentQuestion.type === 'kr-vn') {
            // Korean -> Vietnamese question
            this.correctAnswer = this.currentQuestion.vi;
            
            // Display Korean word with audio button
            vietnameseElement.innerHTML = `
                ${this.currentQuestion.han}
                <button class="audio-button" id="audioButton" onclick="playAudio()">🔊</button>
            `;
            
            // Auto-play audio for KR->VN questions
            window.audioManager.playAudioDelayed(this.currentQuestion.han, 500);
            
            // Create Vietnamese answers
            const wrongAnswers = this.getRandomWrongAnswers(this.correctAnswer, 3, 'vi');
            this.currentAnswers = this.shuffleArray([this.correctAnswer, ...wrongAnswers]);
            
            console.log('KR->VN question:', this.currentQuestion.han, '- Answer:', this.correctAnswer);
        } else {
            // Vietnamese -> Korean question
            this.correctAnswer = this.currentQuestion.han;
            
            // Display Vietnamese word (NO audio button)
            vietnameseElement.innerHTML = this.currentQuestion.vi;
            
            // Create Korean answers
            const wrongAnswers = this.getRandomWrongAnswers(this.correctAnswer, 3, 'han');
            this.currentAnswers = this.shuffleArray([this.correctAnswer, ...wrongAnswers]);
            
            console.log('VN->KR question:', this.currentQuestion.vi, '- Answer:', this.correctAnswer);
        }
        
        console.log('Question', this.currentQuestionIndex + 1, '/', this.totalQuestions);
        
        // Update counter
        this.updateQuestionCounter();
        
        console.log('Answer options:', this.currentAnswers);
        
        // Display answer options
        for (let i = 0; i < 4; i++) {
            const optionElement = document.getElementById('option' + i);
            const numberElement = optionElement.querySelector('.option-number');
            const textElement = optionElement.querySelector('.option-text');
            
            if (!numberElement) {
                optionElement.innerHTML = `
                    <span class="option-number">${i + 1}</span>
                    <span class="option-text">${this.currentAnswers[i]}</span>
                `;
            } else {
                textElement.textContent = this.currentAnswers[i];
            }
        }
        
        // Move to next question
        this.currentQuestionIndex++;
    }

    // Get random wrong answers
    getRandomWrongAnswers(correctAnswer, count, language) {
        let wrongAnswers;
        
        if (language === 'han') {
            // Get Korean wrong answers
            wrongAnswers = this.vocabulary
                .filter(item => item.han !== correctAnswer)
                .map(item => item.han);
        } else {
            // Get Vietnamese wrong answers
            wrongAnswers = this.vocabulary
                .filter(item => item.vi !== correctAnswer)
                .map(item => item.vi);
        }
        
        return this.shuffleArray(wrongAnswers).slice(0, count);
    }

    // Update question counter
    updateQuestionCounter() {
        const questionCounter = document.getElementById('questionCounter');
        questionCounter.textContent = `Câu ${this.currentQuestionIndex} / ${this.totalQuestions}`;
    }

    // Handle answer selection
    selectAnswer(optionIndex, selectedAnswer) {
        if (this.hasAnswered) return;
        
        this.hasAnswered = true;
        const isCorrect = selectedAnswer === this.correctAnswer;
        const wordIndex = this.currentQuestion.wordIndex;
        const questionType = this.currentQuestion.type;
        const isRetry = this.currentQuestion.isRetry || false;
        
        // Update statistics
        this.detailedStats.totalQuestionsAnswered++;
        this.detailedStats.wordAttempts[wordIndex][questionType]++;
        
        // Create icons
        const checkMark = document.createElement('span');
        checkMark.className = 'check-mark';
        checkMark.textContent = '✓';
        
        const xMark = document.createElement('span');
        xMark.className = 'x-mark';
        xMark.textContent = '✗';
        
        // Show results for each option
        for (let i = 0; i < 4; i++) {
            const option = document.getElementById('option' + i);
            option.classList.add('disabled');
            
            if (this.currentAnswers[i] === this.correctAnswer) {
                option.classList.add('correct');
                option.appendChild(checkMark.cloneNode(true));
            } else if (i === optionIndex && !isCorrect) {
                option.classList.add('incorrect');
                option.appendChild(xMark.cloneNode(true));
            }
        }
        
        // Show feedback and update progress
        const feedback = document.getElementById('feedback');
        if (isCorrect) {
            feedback.textContent = 'Chính xác! 🎉';
            feedback.className = 'feedback success';
            this.correctAnswerCount++;
            document.getElementById('option' + optionIndex).classList.add('correct-animation');
            
            this.updateWordProgress();
        } else {
            feedback.textContent = `Sai rồi! Đáp án đúng là: ${this.correctAnswer}`;
            feedback.className = 'feedback error';
            this.wrongAnswerCount++;
        }
        
        // Handle post-answer audio
        this.handlePostAnswerAudio();
        
        // Enable next button
        document.getElementById('nextBtn').disabled = false;
    }

    // Handle audio after answering
    handlePostAnswerAudio() {
        const vietnameseElement = document.getElementById('vietnameseWord');
        const audioButton = `<button class="audio-button" id="audioButton" onclick="playAudio()">🔊</button>`;
        
        if (this.currentQuestion.type === 'kr-vn') {
            // Với câu hỏi KR->VN, giữ nguyên từ tiếng Hàn
            vietnameseElement.innerHTML = `
                ${this.currentQuestion.han}
                ${audioButton}
            `;
            window.audioManager.playAudio(this.currentQuestion.han);
        } else {
            // Với câu hỏi VN->KR, giữ nguyên nghĩa tiếng Việt và thêm nút audio
            vietnameseElement.innerHTML = `
                ${this.currentQuestion.vi}
                ${audioButton}
            `;
            window.audioManager.playAudio(this.currentQuestion.han);
        }
    }

    // Update word progress when answered correctly
    updateWordProgress() {
        const wordIndex = this.currentQuestion.wordIndex;
        const questionType = this.currentQuestion.type;
        
        // Mark this question type as completed for this word
        if (questionType === 'kr-vn') {
            this.wordProgress[wordIndex].krVn = true;
        } else {
            this.wordProgress[wordIndex].vnKr = true;
        }
        
        // Check if word is fully mastered (both types correct)
        const progress = this.wordProgress[wordIndex];
        if (progress.krVn && progress.vnKr) {
            this.completedWords.add(wordIndex);
            
            // Check if both were answered correctly on first try
            const attempts = this.detailedStats.wordAttempts[wordIndex];
            if (attempts.krVn === 1 && attempts.vnKr === 1) {
                this.detailedStats.perfectWords.push(this.vocabulary[wordIndex]);
            }
        }
    }

    // Show completion message
    showCompletionMessage() {
        // Calculate final statistics
        this.calculateFinalStats();
        
        // Hide current quiz container
        const container = document.querySelector('.container');
        container.style.display = 'none';

        // Calculate scores
        const masteredWords = this.detailedStats.masteredWords;
        const totalWords = this.vocabulary.length;
        const masteryPercentage = Math.round((masteredWords / totalWords) * 100);
        
        const overallAccuracy = this.detailedStats.totalOriginalQuestions > 0 ? 
            Math.round((this.correctAnswerCount / this.detailedStats.totalOriginalQuestions) * 100) : 0;
        
        // Choose content based on mastery
        let resultIcon, resultTitle, resultMessage, resultColor;
        
        if (masteryPercentage === 100) {
            if (this.detailedStats.perfectWords.length === totalWords) {
                resultIcon = '🏆';
                resultTitle = 'Hoàn hảo!';
                resultMessage = 'Bạn đã thành thạo tất cả từ vựng ngay lần đầu tiên! Xuất sắc!';
                resultColor = '#FFD700';
            } else {
                resultIcon = '🎉';
                resultTitle = 'Xuất sắc!';
                resultMessage = 'Bạn đã thành thạo tất cả từ vựng trong bài học!';
                resultColor = '#28a745';
            }
        } else if (masteryPercentage >= 80) {
            resultIcon = '👏';
            resultTitle = 'Rất tốt!';
            resultMessage = 'Bạn đã thành thạo hầu hết từ vựng! Hãy ôn tập những từ còn lại.';
            resultColor = '#17a2b8';
        } else if (masteryPercentage >= 60) {
            resultIcon = '📚';
            resultTitle = 'Cần cố gắng thêm!';
            resultMessage = 'Bạn đã hiểu được nhiều từ vựng. Hãy ôn tập để nâng cao hơn nữa!';
            resultColor = '#ffc107';
        } else {
            resultIcon = '💪';
            resultTitle = 'Đừng nản chí!';
            resultMessage = 'Học tiếng Hàn cần thời gian. Hãy ôn tập và thử lại nhé!';
            resultColor = '#dc3545';
        }

        // Create difficult words HTML
        const difficultWordsHtml = this.detailedStats.difficultWords.length > 0 ? `
            <div style="margin-top: 20px; padding: 15px; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px;">
                <h4 style="color: #856404; margin: 0 0 10px 0;">📝 Từ cần ôn tập thêm:</h4>
                ${this.detailedStats.difficultWords.map(word => `
                    <div style="margin: 5px 0; padding: 8px; background: white; border-radius: 4px; border-left: 3px solid #ffc107;">
                        <strong>${word.vi}</strong> → ${word.han} <span style="color: #6c757d;">(${word.attempts})</span>
                    </div>
                `).join('')}
            </div>
        ` : '';

        const perfectWordsHtml = this.detailedStats.perfectWords.length > 0 ? `
            <div style="margin-top: 15px; padding: 12px; background: #d1f2eb; border: 1px solid #7dcea0; border-radius: 8px;">
                <h4 style="color: #0e6251; margin: 0 0 8px 0;">⭐ Từ thành thạo ngay lần đầu: ${this.detailedStats.perfectWords.length}/${totalWords}</h4>
            </div>
        ` : '';

        // Create results container
        const resultsContainer = document.createElement('div');
        resultsContainer.className = 'container';
        resultsContainer.style.animation = 'fadeIn 0.5s ease-in';
        resultsContainer.innerHTML = `
            <div style="text-align: center; padding: 30px 20px;">
                <div style="font-size: 4rem; margin-bottom: 20px; animation: bounce 1s ease-in-out;">${resultIcon}</div>
                <h2 style="color: ${resultColor}; font-size: 2rem; font-weight: 700; margin-bottom: 16px;">${resultTitle}</h2>
                <div style="color: #6c757d; font-size: 1.1rem; margin-bottom: 8px;">Bạn đã hoàn thành bài học</div>
                <div style="font-size: 1.3rem; color: #007bff; font-weight: 600; margin-bottom: 24px;">${window.getLessonName ? window.getLessonName() : 'Bài học từ vựng'}</div>
                
                <!-- Main result -->
                <div style="background: linear-gradient(135deg, ${resultColor}20, ${resultColor}10); border: 2px solid ${resultColor}; border-radius: 16px; padding: 25px; margin: 20px 0;">
                    <div style="font-size: 2.5rem; font-weight: bold; color: ${resultColor}; margin-bottom: 8px;">
                        ${masteredWords}/${totalWords}
                    </div>
                    <div style="font-size: 1.3rem; color: ${resultColor}; font-weight: 600; margin-bottom: 8px;">
                        ${masteryPercentage}% từ vựng đã thành thạo
                    </div>
                    <div style="font-size: 0.95rem; color: #6c757d;">
                        Tỷ lệ chính xác: ${overallAccuracy}% (${this.correctAnswerCount}/${this.detailedStats.totalOriginalQuestions} câu)
                    </div>
                </div>
                
                <!-- Detailed statistics -->
                <div style="background: #f8f9fa; border-radius: 12px; padding: 20px; margin: 20px 0; text-align: left;">
                    <h3 style="margin: 0 0 15px 0; color: #495057; text-align: center;">📊 Thống kê chi tiết</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.9rem;">
                        <div>📝 Tổng câu hỏi: <strong>${this.detailedStats.totalOriginalQuestions}</strong></div>
                        <div>✅ Câu trả lời đúng: <strong>${this.correctAnswerCount}</strong></div>
                        <div>❌ Câu trả lời sai: <strong>${this.wrongAnswerCount}</strong></div>
                        <div>⭐ Từ hoàn hảo: <strong>${this.detailedStats.perfectWords.length}</strong></div>
                    </div>
                </div>
                
                ${perfectWordsHtml}
                ${difficultWordsHtml}
                
                <p style="font-size: 1.1rem; color: #6c757d; margin: 24px 0 32px 0; line-height: 1.5;">${resultMessage}</p>
                
                <div style="display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;">
                    <button onclick="window.quizManager.restart()" style="background: #28a745; color: white; border: none; border-radius: 8px; padding: 14px 24px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);">
                        🔄 Học lại
                    </button>
                    <button onclick="goToIndex()" style="background: #007bff; color: white; border: none; border-radius: 8px; padding: 14px 24px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 2px 8px rgba(0, 123, 255, 0.3);">
                        🏠 Trang chủ
                    </button>
                </div>
            </div>
        `;

        // Insert results container
        document.body.appendChild(resultsContainer);
    }

    // Calculate final statistics
    calculateFinalStats() {
        this.detailedStats.masteredWords = this.completedWords.size;
        
        // Find difficult words
        this.detailedStats.difficultWords = [];
        
        this.vocabulary.forEach((word, index) => {
            const attempts = this.detailedStats.wordAttempts[index];
            const totalCorrect = (this.wordProgress[index].krVn ? 1 : 0) + (this.wordProgress[index].vnKr ? 1 : 0);
            const totalAttempts = attempts.krVn + attempts.vnKr;
            
            if (totalCorrect < 2 && totalAttempts > 0) {
                this.detailedStats.difficultWords.push({
                    ...word,
                    attempts: `${totalCorrect}/2`
                });
            }
        });
        
        // Sort difficult words by performance
        this.detailedStats.difficultWords.sort((a, b) => {
            const aCorrect = parseInt(a.attempts.split('/')[0]);
            const bCorrect = parseInt(b.attempts.split('/')[0]);
            return aCorrect - bCorrect;
        });
        
        console.log('Final statistics:', this.detailedStats);
    }

    // Restart quiz
    restart() {
        // Stop any playing audio
        window.audioManager.stop();
        
        // Reset all counters and state
        this.currentQuestionIndex = 0;
        this.correctAnswerCount = 0;
        this.wrongAnswerCount = 0;
        this.hasAnswered = false;
        this.completedWords.clear();
        this.wordProgress = {};
        
        // Reset detailed stats
        this.detailedStats = {
            totalOriginalQuestions: 0,
            totalQuestionsAnswered: 0,
            correctOnFirstTry: 0,
            retryCount: 0,
            wordAttempts: {},
            difficultWords: [],
            perfectWords: [],
            masteredWords: 0
        };
        
        // Remove results container
        const resultContainers = document.querySelectorAll('.container');
        resultContainers.forEach((container, index) => {
            if (index > 0) {
                container.remove();
            }
        });
        
        // Show original container
        const originalContainer = document.querySelector('.container');
        originalContainer.style.display = 'block';
        
        // Restart the quiz
        this.setupQuestionQueue();
        this.loadNewQuestion();
    }

    // Show error message
    showError(message) {
        const container = document.querySelector('.container');
        container.innerHTML = `
            <div style="text-align: center; padding: 40px;">
                <div style="font-size: 3rem; margin-bottom: 20px;">😞</div>
                <h2 style="color: #dc3545; margin-bottom: 16px;">Lỗi</h2>
                <p style="color: #6c757d; margin-bottom: 32px;">${message}</p>
                <button onclick="goToIndex()" style="background: #007bff; color: white; border: none; border-radius: 8px; padding: 14px 24px; font-size: 1rem; cursor: pointer;">
                    Quay lại trang chủ
                </button>
            </div>
        `;
    }

    // Utility function to shuffle array
    shuffleArray(array) {
        const newArray = [...array];
        for (let i = newArray.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
        }
        return newArray;
    }
}

// Create global instance
window.quizManager = new QuizManager();
