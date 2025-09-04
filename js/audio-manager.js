// Audio Manager Module
// Handles all audio-related functionality

class AudioManager {
    constructor() {
        this.currentAudioElement = null;
        this.audioPath = '';
    }

    setAudioPath(path) {
        this.audioPath = path;
    }

    // Stop current audio
    stop() {
        if (this.currentAudioElement) {
            this.currentAudioElement.pause();
            this.currentAudioElement.currentTime = 0;
            this.currentAudioElement = null;
        }
    }

    // Play audio for a Korean word
    playAudio(koreanWord) {
        if (!koreanWord) return;
        
        const audioButton = document.getElementById('audioButton');
        
        // Create audio file path
        const audioFile = `${this.audioPath}/${koreanWord}.mp3`;
        
        // Stop current audio if playing
        this.stop();
        
        // Create new audio element
        this.currentAudioElement = new Audio(audioFile);
        
        // Handle audio events
        this.currentAudioElement.addEventListener('loadstart', () => {
            if (audioButton) {
                audioButton.classList.add('playing');
                audioButton.style.pointerEvents = 'none';
            }
        });
        
        this.currentAudioElement.addEventListener('ended', () => {
            if (audioButton) {
                audioButton.classList.remove('playing');
                audioButton.style.pointerEvents = 'auto';
            }
        });
        
        this.currentAudioElement.addEventListener('error', (e) => {
            console.warn('Audio file not found:', audioFile);
            if (audioButton) {
                audioButton.classList.remove('playing');
                audioButton.classList.add('disabled');
                audioButton.style.pointerEvents = 'none';
            }
        });
        
        // Play audio
        this.currentAudioElement.play().catch(e => {
            console.warn('Could not play audio:', e);
            if (audioButton) {
                audioButton.classList.remove('playing');
                audioButton.classList.add('disabled');
            }
        });
    }

    // Play audio with delay
    playAudioDelayed(koreanWord, delay = 500) {
        setTimeout(() => {
            this.playAudio(koreanWord);
        }, delay);
    }
}

// Create global instance
window.audioManager = new AudioManager();

// Global function for compatibility
function playAudio() {
    if (window.currentQuestion) {
        window.audioManager.playAudio(window.currentQuestion.han);
    }
}
