import React, { useState, useEffect } from 'react';
import './App.css';
import { useAudioAnalysis } from './useAudioAnalysis';

function App() {
  const { mouthY: mouth1Y, isPlaying: isPlaying1, handlePlayToggle: handlePlayToggle1, currentAudioLevel: currentAudioLevel1 } = useAudioAnalysis('/test-1.mp3');
  const { mouthY: mouth2Y, isPlaying: isPlaying2, handlePlayToggle: handlePlayToggle2, currentAudioLevel: currentAudioLevel2 } = useAudioAnalysis('/test-2.mp3');

  // State for head floating positions
  const [head1Position, setHead1Position] = useState({ x: 0, y: 0 });
  const [head2Position, setHead2Position] = useState({ x: 0, y: 0 });
  
  // Floating animation configuration
  const FLOAT_RADIUS = 20; // Maximum pixels to float from center
  
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

  // Helper function to combine CSS positioning with JavaScript offsets
  const getMouthStyle = (yOffset) => ({
    transform: `translateX(-50%) translateY(${yOffset}px)`,
    transition: 'transform 0.1s ease-out' // Faster transition for audio responsiveness
  });

  // Helper function for face-pair floating animation (affects both head and mouth)
  const getFacePairStyle = (position) => ({
    transform: `translateX(${position.x}px) translateY(${position.y}px)`
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
      <div style={{ position: 'fixed', top: '20px', right: '20px', zIndex: 1002, display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <button 
          onClick={handlePlayToggle1}
          style={{
            width: '90px',
            height: '40px',
            border: '2px solid green',
            backgroundColor: 'rgba(0, 20, 0, 0.8)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: '10px',
            filter: 'drop-shadow(0px 0px 10px rgba(0, 255, 0, 0.5))',
            color: 'green'
          }}
          title={isPlaying1 ? 'Stop Audio 1' : 'Play Audio 1'}
        >
          {isPlaying1 ? 'Stop 1' : 'Play 1'}
        </button>
        <button 
          onClick={handlePlayToggle2}
          style={{
            width: '90px',
            height: '40px',
            border: '2px solid green',
            backgroundColor: 'rgba(0, 20, 0, 0.8)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: '10px',
            filter: 'drop-shadow(0px 0px 10px rgba(0, 255, 0, 0.5))',
            color: 'green'
          }}
          title={isPlaying2 ? 'Stop Audio 2' : 'Play Audio 2'}
        >
          {isPlaying2 ? 'Stop 2' : 'Play 2'}
        </button>
      </div>

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
        Audio 1: {isPlaying1 ? 'Playing' : 'Stopped'} | Level: {currentAudioLevel1}
        <br />
        Audio 2: {isPlaying2 ? 'Playing' : 'Stopped'} | Level: {currentAudioLevel2}
      </div>
    </div>
  );
}

export default App;
