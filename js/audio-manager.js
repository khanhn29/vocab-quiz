// Audio Manager Module
// Handles all audio-related functionality

class AudioManager {
    constructor() {
        this.currentAudioElement = null;
        this.audioPath = '';
        this.voiceType = 'female'; // Start with female voice
        this.playCount = 0; // Track number of plays to alternate
    }

    setAudioPath(path) {
        this.audioPath = path;
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

    // Play audio for a Korean word
    playAudio(koreanWord) {
        if (!koreanWord) return;
        
        const audioButton = document.getElementById('audioButton');
        
        // Increment play count and toggle voice every time
        this.playCount++;
        this.toggleVoice();
        
        // Create audio file path with voice type
        let voiceAudioPath = this.audioPath;
        
        // Handle different audio path formats
        if (this.audioPath.includes('audio/vocab/female/') || this.audioPath.includes('audio/vocab/male/')) {
            // New format: audio/vocab/female/lesson1 or audio/vocab/male/lesson1
            // Replace the voice folder with current voice type
            voiceAudioPath = this.audioPath.replace(/audio\/vocab\/(female|male)\//, `audio/vocab/${this.voiceType}/`);
        } else if (this.audioPath.includes('audio/vocab/lesson')) {
            // Old format: audio/vocab/lesson1
            // Extract lesson number and add voice folder
            const lessonMatch = this.audioPath.match(/audio\/vocab\/(lesson\d+)/);
            if (lessonMatch) {
                const lessonFolder = lessonMatch[1]; // e.g., "lesson1"
                voiceAudioPath = `audio/vocab/${this.voiceType}/${lessonFolder}`;
            }
        }
        
        const audioFile = `${voiceAudioPath}/${koreanWord}.mp3`;
        
        console.log(`Playing audio (${this.voiceType} voice):`, audioFile);
        
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
            console.warn(`Audio file not found (${this.voiceType} voice):`, audioFile);
            
            // Try the other voice if current one fails
            const alternateVoice = this.voiceType === 'female' ? 'male' : 'female';
            
            // Create alternate audio path correctly
            let alternateAudioPath = this.audioPath;
            
            // Handle different audio path formats
            if (this.audioPath.includes('audio/vocab/female/') || this.audioPath.includes('audio/vocab/male/')) {
                // New format: audio/vocab/female/lesson1 or audio/vocab/male/lesson1
                // Replace the voice folder with alternate voice type
                alternateAudioPath = this.audioPath.replace(/audio\/vocab\/(female|male)\//, `audio/vocab/${alternateVoice}/`);
            } else if (this.audioPath.includes('audio/vocab/lesson')) {
                // Old format: audio/vocab/lesson1
                // Extract lesson number and add alternate voice folder
                const lessonMatch = this.audioPath.match(/audio\/vocab\/(lesson\d+)/);
                if (lessonMatch) {
                    const lessonFolder = lessonMatch[1];
                    alternateAudioPath = `audio/vocab/${alternateVoice}/${lessonFolder}`;
                }
            }
            
            const alternateAudioFile = `${alternateAudioPath}/${koreanWord}.mp3`;
            
            console.log(`Trying alternate voice (${alternateVoice}):`, alternateAudioFile);
            
            const alternateAudio = new Audio(alternateAudioFile);
            alternateAudio.play().catch(error => {
                console.warn('Both voice files failed:', error);
                if (audioButton) {
                    audioButton.classList.remove('playing');
                    audioButton.classList.add('disabled');
                    audioButton.style.pointerEvents = 'none';
                }
            });
            
            alternateAudio.addEventListener('ended', () => {
                if (audioButton) {
                    audioButton.classList.remove('playing');
                    audioButton.style.pointerEvents = 'auto';
                }
            });
            
            return; // Don't continue with the original audio
        });
        
        // Play audio
        this.currentAudioElement.play().then(() => {
            // Track audio play with voice type
            if (typeof window.trackAudioPlay === 'function') {
                const vocabFile = new URLSearchParams(window.location.search).get('vocab');
                window.trackAudioPlay(koreanWord, vocabFile, this.voiceType);
            }
        }).catch(e => {
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
