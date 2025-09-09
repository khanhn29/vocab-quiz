// Grammar Audio Manager Module
// Handles audio functionality for grammar exercises with dual voice support

class GrammarAudioManager {
    constructor() {
        this.currentAudioElement = null;
        this.voiceType = 'female'; // Start with female voice
        this.playCount = 0; // Track number of plays to alternate
    }

    // Toggle between male and female voice
    toggleVoice() {
        this.voiceType = this.voiceType === 'female' ? 'male' : 'female';
        console.log('Switched to voice:', this.voiceType);
    }

    // Stop current audio
    stop() {
        if (this.currentAudioElement) {
            this.currentAudioElement.pause();
            this.currentAudioElement.currentTime = 0;
            this.currentAudioElement = null;
        }
    }

    // Play audio for a grammar question
    playQuestionAudio(questionId) {
        if (!questionId) return;
        
        const replayButton = document.getElementById('replay-audio-btn');
        
        // Increment play count and toggle voice every time
        this.playCount++;
        this.toggleVoice();
        
        // Create audio file path with voice type
        const audioFile = `audio/sentences/${this.voiceType}/${questionId}.mp3`;
        
        console.log(`Playing grammar audio (${this.voiceType} voice):`, audioFile);
        
        // Stop current audio if playing
        this.stop();
        
        // Create new audio element
        this.currentAudioElement = new Audio(audioFile);
        
        // Handle audio events
        this.currentAudioElement.addEventListener('loadstart', () => {
            if (replayButton) {
                replayButton.classList.add('playing');
                replayButton.style.pointerEvents = 'none';
                replayButton.textContent = '🔊';
            }
        });
        
        this.currentAudioElement.addEventListener('ended', () => {
            if (replayButton) {
                replayButton.classList.remove('playing');
                replayButton.style.pointerEvents = 'auto';
                replayButton.textContent = '🔊';
            }
        });
        
        this.currentAudioElement.addEventListener('error', (e) => {
            console.warn(`Audio file not found (${this.voiceType} voice):`, audioFile);
            
            // Try the other voice if current one fails
            const alternateVoice = this.voiceType === 'female' ? 'male' : 'female';
            const alternateAudioFile = `audio/sentences/${alternateVoice}/${questionId}.mp3`;
            
            console.log(`Trying alternate voice (${alternateVoice}):`, alternateAudioFile);
            
            const alternateAudio = new Audio(alternateAudioFile);
            alternateAudio.play().catch(error => {
                console.warn('Both voice files failed, falling back to TTS:', error);
                if (replayButton) {
                    replayButton.classList.remove('playing');
                    replayButton.style.pointerEvents = 'auto';
                    replayButton.textContent = '🔊';
                }
                // Fallback to TTS if available
                this.playTextToSpeech(questionId);
            });
            
            alternateAudio.addEventListener('ended', () => {
                if (replayButton) {
                    replayButton.classList.remove('playing');
                    replayButton.style.pointerEvents = 'auto';
                    replayButton.textContent = '🔊';
                }
            });
            
            return; // Don't continue with the original audio
        });
        
        // Play audio
        this.currentAudioElement.play().then(() => {
            // Track audio play with voice type
            if (typeof window.trackAudioPlay === 'function') {
                window.trackAudioPlay(questionId, 'grammar', this.voiceType);
            }
        }).catch(e => {
            console.warn('Could not play audio, trying TTS fallback:', e);
            if (replayButton) {
                replayButton.classList.remove('playing');
                replayButton.style.pointerEvents = 'auto';
                replayButton.textContent = '🔊';
            }
            // Fallback to TTS
            this.playTextToSpeech(questionId);
        });
    }

    // Play text-to-speech as fallback
    playTextToSpeech(questionId) {
        // Try to get the complete sentence from current question
        if (window.currentQuestion && window.currentQuestion.completeSentence) {
            const text = window.currentQuestion.completeSentence;
            
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);
                const voices = speechSynthesis.getVoices();
                const koreanVoice = voices.find(voice => voice.lang.includes('ko'));
                
                if (koreanVoice) {
                    utterance.voice = koreanVoice;
                } else {
                    console.log('No Korean voice found, using default');
                }
                
                utterance.rate = 0.8;
                speechSynthesis.speak(utterance);
                console.log('Playing TTS for:', text);
            } else {
                console.log('Speech synthesis not supported');
            }
        }
    }

    // Play audio with delay
    playQuestionAudioDelayed(questionId, delay = 500) {
        setTimeout(() => {
            this.playQuestionAudio(questionId);
        }, delay);
    }
}

// Create global instance for grammar exercises
window.grammarAudioManager = new GrammarAudioManager();
