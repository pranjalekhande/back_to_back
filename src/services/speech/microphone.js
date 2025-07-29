class MicrophoneService {
  constructor() {
    this.mediaRecorder = null;
    this.audioStream = null;
    this.isRecording = false;
    this.audioChunks = [];
    this.audioChunkCount = 0;
    this.totalAudioSize = 0;
    
    console.log('🎤 MicrophoneService: Initialized');
  }

  /**
   * Initialize microphone access
   * @param {Object} constraints - Media constraints
   */
  async initialize(constraints = {}) {
    console.log('🎤 MicrophoneService: Starting initialization...');
    
    const defaultConstraints = {
      audio: {
        sampleRate: 16000,
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      }
    };

    const finalConstraints = { ...defaultConstraints, ...constraints };
    console.log('🎤 MicrophoneService: Using constraints:', finalConstraints);

    try {
      // Check if navigator.mediaDevices is available
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('getUserMedia not supported in this browser');
      }

      console.log('🎤 MicrophoneService: Requesting microphone access...');
      this.audioStream = await navigator.mediaDevices.getUserMedia(finalConstraints);
      
      // Log stream details
      const audioTracks = this.audioStream.getAudioTracks();
      console.log('✅ MicrophoneService: Microphone access granted');
      console.log('🎤 MicrophoneService: Audio tracks:', audioTracks.length);
      
      if (audioTracks.length > 0) {
        const track = audioTracks[0];
        console.log('🎤 MicrophoneService: Track settings:', track.getSettings());
        console.log('🎤 MicrophoneService: Track capabilities:', track.getCapabilities());
        console.log('🎤 MicrophoneService: Track constraints:', track.getConstraints());
      }
      
      return true;
    } catch (error) {
      console.error('❌ MicrophoneService: Failed to access microphone:', error);
      console.error('❌ MicrophoneService: Error details:', {
        name: error.name,
        message: error.message,
        constraint: error.constraint
      });
      throw new Error(`Microphone access denied: ${error.message}`);
    }
  }

  /**
   * Start recording and streaming audio
   * @param {Function} onAudioData - Callback for audio chunks
   * @param {number} chunkSize - Size of audio chunks in ms
   */
  async startRecording(onAudioData, chunkSize = 250) {
    console.log('🎤 MicrophoneService: Starting recording...');
    console.log('🎤 MicrophoneService: Chunk size:', chunkSize, 'ms');

    if (!this.audioStream) {
      console.error('❌ MicrophoneService: No audio stream available');
      throw new Error('Microphone not initialized. Call initialize() first.');
    }

    if (this.isRecording) {
      console.warn('⚠️ MicrophoneService: Already recording');
      return;
    }

    try {
      // Check MediaRecorder support
      if (!window.MediaRecorder) {
        throw new Error('MediaRecorder not supported in this browser');
      }

      // Check supported MIME types
      const supportedTypes = [
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/mp4',
        'audio/ogg;codecs=opus'
      ];
      
      let selectedMimeType = null;
      for (const type of supportedTypes) {
        if (MediaRecorder.isTypeSupported(type)) {
          selectedMimeType = type;
          break;
        }
      }

      if (!selectedMimeType) {
        console.warn('⚠️ MicrophoneService: No supported MIME types found, using default');
        selectedMimeType = 'audio/webm';
      }

      console.log('🎤 MicrophoneService: Using MIME type:', selectedMimeType);

      // Create MediaRecorder for streaming
      this.mediaRecorder = new MediaRecorder(this.audioStream, {
        mimeType: selectedMimeType,
        audioBitsPerSecond: 16000,
      });

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunkCount++;
          this.totalAudioSize += event.data.size;
          
          console.log(`🎤 MicrophoneService: Audio chunk #${this.audioChunkCount} - ${event.data.size} bytes`);
          console.log(`🎤 MicrophoneService: Total audio: ${(this.totalAudioSize / 1024).toFixed(2)} KB`);
          
          // Convert blob to ArrayBuffer for DeepGram
          event.data.arrayBuffer().then(buffer => {
            const uint8Array = new Uint8Array(buffer);
            console.log(`🎤 MicrophoneService: Sending ${uint8Array.length} bytes to callback`);
            onAudioData(uint8Array);
          }).catch(error => {
            console.error('❌ MicrophoneService: Failed to convert audio data:', error);
          });
        } else {
          console.warn('⚠️ MicrophoneService: Received empty audio chunk');
        }
      };

      this.mediaRecorder.onstart = () => {
        console.log('✅ MicrophoneService: Recording started successfully');
        this.isRecording = true;
        this.audioChunkCount = 0;
        this.totalAudioSize = 0;
      };

      this.mediaRecorder.onstop = () => {
        console.log('🛑 MicrophoneService: Recording stopped');
        console.log(`🎤 MicrophoneService: Final stats - ${this.audioChunkCount} chunks, ${(this.totalAudioSize / 1024).toFixed(2)} KB total`);
        this.isRecording = false;
      };

      this.mediaRecorder.onerror = (error) => {
        console.error('❌ MicrophoneService: MediaRecorder error:', error);
        console.error('❌ MicrophoneService: Error event details:', {
          type: error.type,
          target: error.target?.state,
          error: error.error
        });
        this.isRecording = false;
      };

      // Log MediaRecorder state before starting
      console.log('🎤 MicrophoneService: MediaRecorder state before start:', this.mediaRecorder.state);

      // Start recording with time slicing
      this.mediaRecorder.start(chunkSize);
      
      console.log('🎤 MicrophoneService: MediaRecorder.start() called');

    } catch (error) {
      console.error('❌ MicrophoneService: Failed to start recording:', error);
      console.error('❌ MicrophoneService: Error stack:', error.stack);
      throw error;
    }
  }

  /**
   * Stop recording
   */
  stopRecording() {
    console.log('🎤 MicrophoneService: Attempting to stop recording...');
    
    if (this.mediaRecorder && this.isRecording) {
      console.log('🎤 MicrophoneService: MediaRecorder state before stop:', this.mediaRecorder.state);
      this.mediaRecorder.stop();
      console.log('🎤 MicrophoneService: MediaRecorder.stop() called');
    } else {
      console.log('🎤 MicrophoneService: No active recording to stop');
    }
  }

  /**
   * Cleanup resources
   */
  cleanup() {
    console.log('🎤 MicrophoneService: Starting cleanup...');
    
    this.stopRecording();
    
    if (this.audioStream) {
      const tracks = this.audioStream.getTracks();
      console.log(`🎤 MicrophoneService: Stopping ${tracks.length} audio tracks`);
      
      tracks.forEach((track, index) => {
        console.log(`🎤 MicrophoneService: Stopping track ${index + 1}: ${track.kind} - ${track.label}`);
        track.stop();
      });
      
      this.audioStream = null;
      console.log('✅ MicrophoneService: Audio stream cleaned up');
    }
    
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.audioChunkCount = 0;
    this.totalAudioSize = 0;
    
    console.log('✅ MicrophoneService: Cleanup completed');
  }

  /**
   * Get current recording status
   */
  getStatus() {
    const status = {
      isRecording: this.isRecording,
      hasStream: !!this.audioStream,
      hasRecorder: !!this.mediaRecorder,
      audioChunkCount: this.audioChunkCount,
      totalAudioSize: this.totalAudioSize,
      totalAudioSizeKB: (this.totalAudioSize / 1024).toFixed(2),
      recorderState: this.mediaRecorder?.state || 'none',
      streamActive: this.audioStream?.active || false,
      trackCount: this.audioStream?.getTracks()?.length || 0
    };
    
    console.log('🎤 MicrophoneService: Current status:', status);
    return status;
  }

  /**
   * Get audio level for visualization
   */
  getAudioLevel() {
    if (!this.audioStream) {
      console.log('🎤 MicrophoneService: No audio stream for level detection');
      return 0;
    }

    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const analyser = audioContext.createAnalyser();
      const microphone = audioContext.createMediaStreamSource(this.audioStream);
      
      analyser.smoothingTimeConstant = 0.8;
      analyser.fftSize = 1024;
      
      microphone.connect(analyser);
      
      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      analyser.getByteFrequencyData(dataArray);
      
      // Calculate average volume
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i];
      }
      
      const level = sum / dataArray.length / 255; // Normalized 0-1
      console.log(`🎤 MicrophoneService: Audio level: ${(level * 100).toFixed(1)}%`);
      
      return level;
    } catch (error) {
      console.error('❌ MicrophoneService: Failed to get audio level:', error);
      return 0;
    }
  }
}

export default MicrophoneService;
