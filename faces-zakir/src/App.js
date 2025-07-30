import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  // State for mouth positions (in pixels, applied on top of CSS)
  const [mouth1Y, setMouth1Y] = useState(0);
  const [mouth2Y, setMouth2Y] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioInitialized, setAudioInitialized] = useState(false);
  
  // State for head floating positions
  const [head1Position, setHead1Position] = useState({ x: 0, y: 0 });
  const [head2Position, setHead2Position] = useState({ x: 0, y: 0 });
  
  // Audio analysis refs
  const audioRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const dataArrayRef = useRef(null);
  const animationIdRef = useRef(null);
  const sourceRef = useRef(null);

  // Audio configuration
  const AUDIO_THRESHOLD = 7; // Lowered threshold for better sensitivity (0-255)
  const MOUTH_OPEN_DISTANCE = 15; // pixels to move mouth down when "talking"
  
  // Add state for debugging audio levels
  const [currentAudioLevel, setCurrentAudioLevel] = useState(0);
  
  // Floating animation configuration
  const FLOAT_RADIUS = 20; // Maximum pixels to float from center
  const FLOAT_SPEED = 6000; // Animation duration in milliseconds

  // Audio setup function (called after user interaction)
  const setupAudio = async () => {
    try {
      console.log('Setting up audio...');
      
      // Create audio context
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      console.log('Audio context created, state:', audioContextRef.current.state);
      
      // Resume audio context (required for autoplay policy)
      if (audioContextRef.current.state === 'suspended') {
        await audioContextRef.current.resume();
        console.log('Audio context resumed, new state:', audioContextRef.current.state);
      }
      
      // Load the MP3 file
      console.log('Fetching MP3 file...');
      const response = await fetch('/test-1.mp3');
      console.log('MP3 response status:', response.status);
      const arrayBuffer = await response.arrayBuffer();
      console.log('MP3 arrayBuffer size:', arrayBuffer.byteLength);
      const audioBuffer = await audioContextRef.current.decodeAudioData(arrayBuffer);
      console.log('Audio decoded - duration:', audioBuffer.duration, 'channels:', audioBuffer.numberOfChannels);
      
      // Create audio source
      sourceRef.current = audioContextRef.current.createBufferSource();
      sourceRef.current.buffer = audioBuffer;
      console.log('Audio source created');
      
      // Create analyser for audio level detection
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      const bufferLength = analyserRef.current.frequencyBinCount;
      dataArrayRef.current = new Uint8Array(bufferLength);
      console.log('Analyser created - fftSize:', analyserRef.current.fftSize, 'bufferLength:', bufferLength);
      
      // Connect audio graph
      sourceRef.current.connect(analyserRef.current);
      analyserRef.current.connect(audioContextRef.current.destination);
      console.log('Audio graph connected: source -> analyser -> destination');
      
      // Start playing audio on loop
      sourceRef.current.loop = true;
      sourceRef.current.start();
      console.log('Audio playback started with loop=true');
      
      setAudioInitialized(true);
      setIsPlaying(true);
      
      // Start audio analysis
      console.log('Starting audio analysis...');
      analyzeAudio();
      
    } catch (error) {
      console.error('Error setting up audio:', error);
      console.log('Make sure test-1.mp3 is in the public folder');
    }
  };

  const analyzeAudio = () => {
    console.log('analyzeAudio called', { 
      hasAnalyser: !!analyserRef.current, 
      hasDataArray: !!dataArrayRef.current, 
      isPlaying 
    });
    
    if (!analyserRef.current || !dataArrayRef.current) {
      console.log('Exiting analyzeAudio - missing analyser or data array');
      return;
    }
    
    // Check if we have an active audio source
    if (!sourceRef.current) {
      console.log('Stopping audio analysis - no active source');
      return;
    }
    
    // Get time domain data (actual audio amplitude)
    analyserRef.current.getByteTimeDomainData(dataArrayRef.current);
    
    // Debug: log first few samples
    const firstFewSamples = Array.from(dataArrayRef.current.slice(0, 10));
    console.log('First 10 audio samples:', firstFewSamples);
    
    // Calculate RMS (Root Mean Square) for better volume detection
    let sum = 0;
    for (let i = 0; i < dataArrayRef.current.length; i++) {
      const sample = (dataArrayRef.current[i] - 128) / 128; // Normalize to -1 to 1
      sum += sample * sample;
    }
    const rms = Math.sqrt(sum / dataArrayRef.current.length);
    const volume = rms * 255; // Scale back to 0-255 range
    
    console.log('Audio analysis:', { 
      arrayLength: dataArrayRef.current.length,
      sum: sum.toFixed(4),
      rms: rms.toFixed(4),
      volume: volume.toFixed(2),
      threshold: AUDIO_THRESHOLD
    });
    
    // Update debug state
    setCurrentAudioLevel(Math.round(volume));
    
    // Control mouth-1 based on audio level
    if (volume > AUDIO_THRESHOLD) {
      // Audio detected - open mouth
      console.log('MOUTH OPENING - volume above threshold');
      setMouth1Y(MOUTH_OPEN_DISTANCE);
    } else {
      // Quiet - close mouth
      setMouth1Y(0);
    }
    
    // Continue analysis
    animationIdRef.current = requestAnimationFrame(analyzeAudio);
  };

  const handlePlayToggle = async () => {
    if (!audioInitialized) {
      // First time - initialize audio
      await setupAudio();
          } else {
        // Toggle play/pause
        if (isPlaying) {
                     // Stop audio
           console.log('Stopping audio playback');
           if (sourceRef.current) {
             sourceRef.current.stop();
             sourceRef.current = null; // Clear reference to stop analysis
           }
           if (animationIdRef.current) {
             cancelAnimationFrame(animationIdRef.current);
           }
           setIsPlaying(false);
           setMouth1Y(0); // Close mouth when stopped
        } else {
          // Restart audio (need to recreate source)
          console.log('Restarting audio playback');
          await setupAudio();
        }
      }
  };

     // Continuous floating animation for heads
   useEffect(() => {
     let animationId;
     const startTime = Date.now();
     
     // Different frequencies and phases for each head to create unique movement patterns
     const head1Config = {
       xFreq: 0.0008,  // How fast it moves horizontally
       yFreq: 0.0012,  // How fast it moves vertically
       xPhase: 0,      // Starting phase offset
       yPhase: Math.PI / 4
     };
     
     const head2Config = {
       xFreq: 0.0010,
       yFreq: 0.0009,
       xPhase: Math.PI / 2,
       yPhase: Math.PI
     };

     const animate = () => {
       const elapsed = Date.now() - startTime;
       
       // Calculate smooth floating positions using sine waves
       const head1X = Math.sin(elapsed * head1Config.xFreq + head1Config.xPhase) * FLOAT_RADIUS;
       const head1Y = Math.cos(elapsed * head1Config.yFreq + head1Config.yPhase) * FLOAT_RADIUS;
       
       const head2X = Math.sin(elapsed * head2Config.xFreq + head2Config.xPhase) * FLOAT_RADIUS;
       const head2Y = Math.cos(elapsed * head2Config.yFreq + head2Config.yPhase) * FLOAT_RADIUS;
       
       setHead1Position({ x: head1X, y: head1Y });
       setHead2Position({ x: head2X, y: head2Y });
       
       animationId = requestAnimationFrame(animate);
     };

     animate();

     return () => {
       if (animationId) {
         cancelAnimationFrame(animationId);
       }
     };
   }, []);

   // Cleanup function
   useEffect(() => {
     return () => {
       if (animationIdRef.current) {
         cancelAnimationFrame(animationIdRef.current);
       }
       if (sourceRef.current) {
         sourceRef.current.stop();
         sourceRef.current = null;
       }
       if (audioContextRef.current) {
         audioContextRef.current.close();
       }
     };
   }, []);

  // Helper function to combine CSS positioning with JavaScript offsets
  const getMouthStyle = (yOffset) => ({
    transform: `translateX(-50%) translateY(${yOffset}px)`,
    transition: 'transform 0.1s ease-out' // Faster transition for audio responsiveness
  });

  // Helper function for face-pair floating animation (affects both head and mouth)
  const getFacePairStyle = (position) => ({
    transform: `translateX(${position.x}px) translateY(${position.y}px)`
    // No CSS transition - using requestAnimationFrame for smooth continuous movement
  });

  return (
    <div className="App">
      {/* Matrix-style animated grid background */}
      <div className="grid-container">
        <div className="plane">
          <div className="grid"></div>
          <div className="glow"></div>
        </div>
        <div className="plane">
          <div className="grid"></div>
          <div className="glow"></div>
        </div>
      </div>

      {/* Matrix-style title */}
      <h1>Amp vs Claude Code: Roast Battle 😈</h1>

      {/* Play button in top right */}
      <button 
        onClick={handlePlayToggle}
        style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          width: '90px',
          height: '90px',
          border: '2px solid green',
          backgroundColor: 'rgba(0, 20, 0, 0.8)',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1002,
          borderRadius: '10px',
          filter: 'drop-shadow(0px 0px 10px rgba(0, 255, 0, 0.5))'
        }}
        title={isPlaying ? 'Stop Audio' : 'Play Audio'}
      >
        {isPlaying ? (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="green">
            <rect x="6" y="4" width="4" height="16" />
            <rect x="14" y="4" width="4" height="16" />
          </svg>
        ) : (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="green">
            <polygon points="8,5 19,12 8,19" />
          </svg>
        )}
      </button>

      <div className="faces-container">
        <div className="face-column">
          <div className="face-pair face-pair-1" style={getFacePairStyle(head1Position)}>
            <img 
              src="/head-1.png" 
              className="head-image" 
              alt="Head 1"
            />
            <img 
              src="/mouth-1.png" 
              className="mouth-image" 
              alt="Mouth 1"
              id="mouth-1"
              style={getMouthStyle(mouth1Y)}
            />
          </div>
        </div>
        <div className="face-column">
          <div className="face-pair face-pair-2" style={getFacePairStyle(head2Position)}>
            <img 
              src="/head-2.png" 
              className="head-image" 
              alt="Head 2"
            />
            <img 
              src="/mouth-2.png" 
              className="mouth-image" 
              alt="Mouth 2"
              style={getMouthStyle(mouth2Y)}
            />
          </div>
        </div>
      </div>
      
      {/* Audio controls (optional - for debugging) */}
      <div style={{
        position: 'fixed', 
        bottom: '20px', 
        left: '20px', 
        fontSize: '12px', 
        color: 'green', 
        backgroundColor: 'rgba(0, 20, 0, 0.9)', 
        padding: '10px', 
        borderRadius: '5px',
        border: '1px solid green',
        filter: 'drop-shadow(0px 0px 5px rgba(0, 255, 0, 0.3))'
      }}>
        Audio status: {isPlaying ? 'Playing' : 'Stopped'}
        <br />
        Current level: {currentAudioLevel} | Threshold: {AUDIO_THRESHOLD}
        <br />
        Mouth position: {mouth1Y}px | {currentAudioLevel > AUDIO_THRESHOLD ? 'MOUTH OPEN' : 'mouth closed'}
      </div>
    </div>
  );
}

export default App;
