// Using global Deepgram object from CDN
// const { createClient, LiveTranscriptionEvents } = window.deepgram;

class DeepgramService {
  constructor(apiKey) {
    if (!window.deepgram) {
      throw new Error('Deepgram SDK not loaded. Include CDN script first.');
    }
    
    const { createClient } = window.deepgram;
    this.client = createClient(apiKey);
    this.connection = null;
    this.isListening = false;
  }

  /**
   * Initialize live transcription connection
   * @param {Object} config - Configuration options
   * @param {Function} onTranscript - Callback for transcription results
   * @param {Function} onError - Callback for errors
   */
  async startListening(config = {}, onTranscript, onError) {
    if (this.isListening) {
      console.warn('Already listening, stop current session first');
      return;
    }

    const defaultConfig = {
      model: process.env.DEEPGRAM_MODEL || 'nova-2',
      language: process.env.DEEPGRAM_LANGUAGE || 'en-US',
      smart_format: process.env.DEEPGRAM_SMART_FORMAT === 'true',
      interim_results: true,
      endpointing: 300, // ms of silence to trigger endpoint
      utterance_end_ms: 1000,
      vad_events: true,
    };

    const finalConfig = { ...defaultConfig, ...config };

    try {
      this.connection = this.client.listen.live(finalConfig);

      // Handle connection events
      const { LiveTranscriptionEvents } = window.deepgram;
      
      this.connection.on(LiveTranscriptionEvents.Open, () => {
        console.log('DeepGram connection opened');
        this.isListening = true;
      });

      this.connection.on(LiveTranscriptionEvents.Transcript, (data) => {
        const transcript = data.channel.alternatives[0].transcript;
        const isFinal = data.is_final;
        const confidence = data.channel.alternatives[0].confidence;

        if (transcript && transcript.trim() !== '') {
          onTranscript({
            text: transcript,
            isFinal,
            confidence,
            metadata: {
              words: data.channel.alternatives[0].words,
              speechFinal: data.speech_final,
            }
          });
        }
      });

      this.connection.on(LiveTranscriptionEvents.Metadata, (data) => {
        console.log('DeepGram metadata:', data);
      });

      this.connection.on(LiveTranscriptionEvents.Error, (error) => {
        console.error('DeepGram error:', error);
        onError?.(error);
      });

      this.connection.on(LiveTranscriptionEvents.Close, () => {
        console.log('DeepGram connection closed');
        this.isListening = false;
        this.connection = null;
      });

    } catch (error) {
      console.error('Failed to start DeepGram connection:', error);
      onError?.(error);
    }
  }

  /**
   * Send audio data to DeepGram
   * @param {ArrayBuffer|Uint8Array} audioData - Audio data to transcribe
   */
  sendAudio(audioData) {
    if (!this.connection || !this.isListening) {
      console.warn('DeepGram connection not active');
      return;
    }

    this.connection.send(audioData);
  }

  /**
   * Stop listening and close connection
   */
  stopListening() {
    if (this.connection) {
      this.connection.requestClose();
      this.connection = null;
      this.isListening = false;
    }
  }

  /**
   * Check if currently listening
   */
  getStatus() {
    return {
      isListening: this.isListening,
      hasConnection: !!this.connection
    };
  }
}

export default DeepgramService;
