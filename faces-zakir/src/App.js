import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  // State for mouth positions (in pixels, applied on top of CSS)
  const [mouth1Y, setMouth1Y] = useState(0);
  const [mouth2Y, setMouth2Y] = useState(0);

  // 🎯 ADD YOUR ANIMATION LOGIC HERE
  useEffect(() => {
    // Simple example animation: mouth moves down 10px and back up
    const animateSimple = () => {
      // Move down
      setMouth1Y(10);
      setMouth2Y(10);
      
      setTimeout(() => {
        // Move back up
        setMouth1Y(0);
        setMouth2Y(0);
      }, 500);
    };

    // Run animation every 1 second
    const interval = setInterval(animateSimple, 1000);
    
    return () => clearInterval(interval);
  }, []);

  // Helper function to combine CSS positioning with JavaScript offsets
  const getMouthStyle = (yOffset) => ({
    transform: `translateX(-50%) translateY(${yOffset}px)`,
    transition: 'transform 0.2s ease-in-out'
  });

  return (
    <div className="App">
      <div className="faces-container">
        <div className="face-column">
          <img src="/head-1.png" className="head-image" alt="Head 1" />
          <img 
            src="/mouth-1.png" 
            className="mouth-image" 
            alt="Mouth 1"
            style={getMouthStyle(mouth1Y)}
          />
        </div>
        <div className="face-column">
          <img src="/head-2.png" className="head-image" alt="Head 2" />
          <img 
            src="/mouth-2.png" 
            className="mouth-image" 
            alt="Mouth 2"
            style={getMouthStyle(mouth2Y)}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
