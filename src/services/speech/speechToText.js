import DeepgramService from './deepgram.js';
import MicrophoneService from './microphone.js';

class SpeechToTextService {
  constructor(apiKey) {
    this.deepgram = new DeepgramService(apiKey);
    this.microphone = new MicrophoneService();
    this.isActive = false;
    this.currentTranscript = '';
    this.callbacks = {
      onTranscript: null,
      onFinalTranscript: null,
      onError: null,
      onStatusChange: null,
    };
  }

  /**
   * Set event callbacks
   * @param {Object} callbacks - Event callbacks
   */
  setCallbacks(callbacks) {
    this.callbacks = { ...this.callbacks, ...callbacks };
  }

  /**
   * Start speech-to-text service
   * @param {Object} config - Configuration options
   */
  async start(config = {}) {
    if (this.isActive) {
      console.warn('Speech-to-text already active');
      return;
    }

    try {
      // Initialize microphone
      await this.microphone.initialize();
      
      // Start DeepGram connection
      await this.deepgram.startListening(
        config,
        this._handleTranscript.bind(this),
        this._handleError.bind(this)
      );

      // Start recording and streaming to DeepGram
      await this.microphone.startRecording((audioData) => {
        this.deepgram.sendAudio(audioData);
      });

      this.isActive = true;
      this._notifyStatusChange('active');
      
      console.log('Speech-to-text service started');

    } catch (error) {
      console.error('Failed to start speech-to-text:', error);
      this._handleError(error);
      throw error;
    }
  }

  /**
   * Stop speech-to-text service
   */
  stop() {
    if (!this.isActive) {
      return;
    }

    this.microphone.stopRecording();
    this.deepgram.stopListening();
    
    this.isActive = false;
    this.currentTranscript = '';
    
    this._notifyStatusChange('stopped');
    console.log('Speech-to-text service stopped');
  }

  /**
   * Cleanup all resources
   */
  cleanup() {
    this.stop();
    this.microphone.cleanup();
  }

  /**
   * Get current status
   */
  getStatus() {
    return {
      isActive: this.isActive,
      currentTranscript: this.currentTranscript,
      microphone: this.microphone.getStatus(),
      deepgram: this.deepgram.getStatus(),
    };
  }

  /**
   * Handle transcript events from DeepGram
   * @private
   */
  _handleTranscript(transcriptData) {
    const { text, isFinal, confidence, metadata } = transcriptData;

    // Update current transcript
    if (isFinal) {
      this.currentTranscript = text;
      
      // Notify final transcript
      if (this.callbacks.onFinalTranscript && text.trim()) {
        this.callbacks.onFinalTranscript({
          text: text.trim(),
          confidence,
          metadata,
          timestamp: new Date().toISOString(),
        });
      }
    } else {
      // Interim result
      if (this.callbacks.onTranscript) {
        this.callbacks.onTranscript({
          text,
          isFinal: false,
          confidence,
          metadata,
        });
      }
    }
  }

  /**
   * Handle errors
   * @private
   */
  _handleError(error) {
    console.error('Speech-to-text error:', error);
    
    if (this.callbacks.onError) {
      this.callbacks.onError(error);
    }

    // Auto-restart on certain errors
    if (this.isActive && this._shouldRestart(error)) {
      console.log('Attempting to restart speech-to-text service...');
      setTimeout(() => {
        this.stop();
        this.start().catch(console.error);
      }, 2000);
    }
  }

  /**
   * Notify status changes
   * @private
   */
  _notifyStatusChange(status) {
    if (this.callbacks.onStatusChange) {
      this.callbacks.onStatusChange(status, this.getStatus());
    }
  }

  /**
   * Determine if service should auto-restart
   * @private
   */
  _shouldRestart(error) {
    const restartableErrors = [
      'connection lost',
      'websocket error',
      'network error',
    ];

    return restartableErrors.some(errorType => 
      error.message?.toLowerCase().includes(errorType)
    );
  }

  /**
   * Get audio level for visualization
   */
  getAudioLevel() {
    return this.microphone.getAudioLevel();
  }
}

export default SpeechToTextService;
