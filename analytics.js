// analytics.js - Shared Google Analytics configuration
(function() {
    // Load Google tag script
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=G-FMXYTG7WCJ';
    document.head.appendChild(script);

    // Initialize dataLayer and gtag
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    
    // Wait for script to load before configuring
    script.onload = function() {
        gtag('js', new Date());
        gtag('config', 'G-FMXYTG7WCJ');
        console.log('Google Analytics initialized');
    };

    // Export gtag for global use
    window.gtag = gtag;

    // Custom tracking functions for vocabulary learning
    window.trackVocabStart = function(vocabFile) {
        if (typeof gtag === 'function') {
            gtag('event', 'vocab_start', {
                vocab_file: vocabFile,
                page_location: window.location.href
            });
            console.log('Tracked vocab start:', vocabFile);
        }
    };

    window.trackVocabComplete = function(vocabFile, correctAnswers, totalQuestions, wrongAnswerCount) {
        if (typeof gtag === 'function') {
            const accuracy = totalQuestions > 0 ? (correctAnswers / totalQuestions * 100).toFixed(1) : 0;
            gtag('event', 'vocab_complete', {
                vocab_file: vocabFile,
                correct_answers: correctAnswers,
                total_questions: totalQuestions,
                wrong_answers: wrongAnswerCount,
                accuracy_percent: parseFloat(accuracy)
            });
            console.log('Tracked vocab complete:', {
                file: vocabFile,
                accuracy: accuracy + '%',
                correct: correctAnswers,
                total: totalQuestions
            });
        }
    };

    window.trackQuestionAnswer = function(isCorrect, questionType, koreanWord, vietnameseWord) {
        if (typeof gtag === 'function') {
            gtag('event', 'question_answer', {
                is_correct: isCorrect,
                question_type: questionType, // 'vn-kr' or 'kr-vn'
                korean_word: koreanWord,
                vietnamese_word: vietnameseWord
            });
        }
    };

    // Track page views with custom titles
    window.trackPageView = function(pageTitle, pagePath) {
        if (typeof gtag === 'function') {
            gtag('config', 'G-FMXYTG7WCJ', {
                page_title: pageTitle,
                page_location: window.location.href,
                page_path: pagePath || window.location.pathname
            });
            console.log('Tracked page view:', pageTitle);
        }
    };

    // Track audio play events
    window.trackAudioPlay = function(koreanWord, vocabFile, voiceType = 'unknown') {
        if (typeof gtag === 'function') {
            gtag('event', 'audio_play', {
                korean_word: koreanWord,
                vocab_file: vocabFile,
                voice_type: voiceType, // Track whether it's male or female voice
                audio_type: 'korean_pronunciation'
            });
        }
    };

    console.log('Analytics.js loaded successfully');
})();