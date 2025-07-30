import { useState, useRef, useEffect, useCallback } from 'react';

const AUDIO_THRESHOLD = 7; // Lowered threshold for better sensitivity (0-255)
const MOUTH_OPEN_DISTANCE = 15; // pixels to move mouth down when "talking"

export const useAudioAnalysis = (audioSrc) => {
  const [mouthY, setMouthY] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioInitialized, setAudioInitialized] = useState(false);
  const [currentAudioLevel, setCurrentAudioLevel] = useState(0);

  // Audio analysis refs
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const dataArrayRef = useRef(null);
  const animationIdRef = useRef(null);
  const sourceRef = useRef(null);

  const analyzeAudio = useCallback(() => {
    if (!analyserRef.current || !dataArrayRef.current || !sourceRef.current) {
      if (animationIdRef.current) {
        cancelAnimationFrame(animationIdRef.current);
        animationIdRef.current = null;
      }
      return;
    }
    
    analyserRef.current.getByteTimeDomainData(dataArrayRef.current);
    
    let sum = 0;
    for (let i = 0; i < dataArrayRef.current.length; i++) {
      const sample = (dataArrayRef.current[i] - 128) / 128; // Normalize to -1 to 1
      sum += sample * sample;
    }
    const rms = Math.sqrt(sum / dataArrayRef.current.length);
    const volume = rms * 255; // Scale back to 0-255 range
    
    setCurrentAudioLevel(Math.round(volume));
    
    if (volume > AUDIO_THRESHOLD) {
      setMouthY(MOUTH_OPEN_DISTANCE);
    } else {
      setMouthY(0);
    }
    
    animationIdRef.current = requestAnimationFrame(analyzeAudio);
  }, []);

  const stopAudio = useCallback(() => {
    console.log(`Stopping audio for ${audioSrc}`);
    if (sourceRef.current) {
      sourceRef.current.stop();
      sourceRef.current.disconnect();
      sourceRef.current = null;
    }
    if (animationIdRef.current) {
      cancelAnimationFrame(animationIdRef.current);
      animationIdRef.current = null;
    }
    setIsPlaying(false);
    setMouthY(0);
  }, [audioSrc]);

  const setupAudio = useCallback(async () => {
    try {
      console.log(`Setting up audio for ${audioSrc}...`);
      
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      }
      
      if (audioContextRef.current.state === 'suspended') {
        await audioContextRef.current.resume();
      }
      
      const response = await fetch(audioSrc);
      const arrayBuffer = await response.arrayBuffer();
      const audioBuffer = await audioContextRef.current.decodeAudioData(arrayBuffer);
      
      sourceRef.current = audioContextRef.current.createBufferSource();
      sourceRef.current.buffer = audioBuffer;
      
      if (!analyserRef.current) {
        analyserRef.current = audioContextRef.current.createAnalyser();
        analyserRef.current.fftSize = 256;
        const bufferLength = analyserRef.current.frequencyBinCount;
        dataArrayRef.current = new Uint8Array(bufferLength);
      }
      
      sourceRef.current.connect(analyserRef.current);
      analyserRef.current.connect(audioContextRef.current.destination);
      
      sourceRef.current.loop = true;
      sourceRef.current.start();
      
      setAudioInitialized(true);
      setIsPlaying(true);
      
      analyzeAudio();
      
    } catch (error) {
      console.error(`Error setting up audio for ${audioSrc}:`, error);
    }
  }, [audioSrc, analyzeAudio]);

  const handlePlayToggle = async () => {
    if (!audioInitialized) {
      await setupAudio();
    } else {
      if (isPlaying) {
        stopAudio();
      } else {
        await setupAudio();
      }
    }
  };

  useEffect(() => {
    return () => {
      if (sourceRef.current) {
        sourceRef.current.stop();
        sourceRef.current.disconnect();
      }
      if (animationIdRef.current) {
        cancelAnimationFrame(animationIdRef.current);
      }
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close();
      }
    };
  }, []);

  return { mouthY, isPlaying, handlePlayToggle, currentAudioLevel };
}; 