"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, SkipForward, Radio, Volume2, Mic } from 'lucide-react';

const TRACKS = [
  { id: 1, title: "Station Intro", artist: "QFZZ AI", url: "http://localhost:8000/intro.wav", genre: "Station ID" },
  { id: 2, title: "Test Tone 440Hz", artist: "Physics", url: "http://localhost:8000/test_tone.wav", genre: "Test" }
];

export default function AudioPlayer() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(0.8);
  const [currentTrackIndex, setCurrentTrackIndex] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [djMessage, setDjMessage] = useState("Welcome to QFZZ, the Pulse of the Quantum Realm.");

  const audioRef = useRef<HTMLAudioElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);

  const currentTrack = TRACKS[currentTrackIndex];

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume;
    }
  }, [volume]);

  // Visualizer Animation
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw fake visualizer bars
      const barWidth = 4;
      const gap = 2;
      const barCount = Math.floor(canvas.width / (barWidth + gap));

      for (let i = 0; i < barCount; i++) {
        // Random height based on playing state
        const height = isPlaying ? Math.random() * 40 + 5 : 2;

        ctx.fillStyle = '#8b5cf6';
        ctx.fillRect(i * (barWidth + gap), canvas.height / 2 - height / 2, barWidth, height);
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, [isPlaying]);

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
      setDuration(audioRef.current.duration || 0);
    }
  };

  const handleNext = () => {
    setCurrentTrackIndex((prev) => (prev + 1) % TRACKS.length);
    setIsPlaying(false);
    setTimeout(() => {
      if (audioRef.current) {
        audioRef.current.load();
        audioRef.current.play();
        setIsPlaying(true);
      }
    }, 100);
    setDjMessage("Switching tracks... Quantum tunnel engaged.");
  };

  const formatTime = (time: number) => {
    const mins = Math.floor(time / 60);
    const secs = Math.floor(time % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8 gap-8 font-mono relative overflow-hidden">

      {/* Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-900/20 rounded-full blur-[100px] -z-10 animate-pulse"></div>

      {/* Header */}
      <div className="text-center space-y-2 z-10">
        <h1 className="text-4xl font-bold tracking-tighter text-white flex items-center justify-center gap-3">
          <Radio className="w-8 h-8 text-purple-400" />
          QFZZ Prime
        </h1>
        <p className="text-slate-400 text-sm tracking-widest uppercase">The Pulse of the Quantum Realm</p>
      </div>

      {/* Main Player Card */}
      <div className="w-full max-w-md bg-slate-900/80 backdrop-blur-xl border border-white/10 rounded-3xl p-6 shadow-2xl relative">

        {/* DJ Message Area */}
        <div className="bg-black/40 rounded-xl p-4 mb-6 border border-white/5 flex gap-3 items-start">
          <Mic className="w-5 h-5 text-green-400 mt-1 shrink-0" />
          <p className="text-green-400/90 text-sm leading-relaxed typing-effect">
            {djMessage}
          </p>
        </div>

        {/* Visualizer */}
        <div className="h-16 w-full mb-6 bg-black/20 rounded-lg overflow-hidden flex items-center justify-center">
          <canvas ref={canvasRef} width={360} height={64} className="w-full h-full opacity-80" />
        </div>

        {/* Track Info */}
        <div className="text-center mb-8 space-y-1">
          <h2 className="text-xl font-bold text-white truncate">{currentTrack.title}</h2>
          <p className="text-purple-300 text-sm">{currentTrack.artist}</p>
          <span className="inline-block px-2 py-0.5 mt-2 bg-purple-500/10 border border-purple-500/20 rounded text-[10px] text-purple-300 uppercase tracking-wider">
            {currentTrack.genre}
          </span>
        </div>

        {/* Progress */}
        <div className="w-full bg-slate-800 rounded-full h-1.5 mb-2 overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-purple-500 to-blue-500 transition-all duration-100 ease-linear"
            style={{ width: `${(currentTime / (duration || 1)) * 100}%` }}
          ></div>
        </div>
        <div className="flex justify-between text-xs text-slate-500 font-medium mb-6">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-center gap-8 mb-6">
          <button
            onClick={togglePlay}
            className="w-16 h-16 bg-white rounded-full flex items-center justify-center text-slate-900 hover:scale-105 transition-transform active:scale-95 shadow-lg shadow-purple-500/20"
          >
            {isPlaying ? (
              <Pause className="w-6 h-6 fill-current" />
            ) : (
              <Play className="w-6 h-6 fill-current ml-1" />
            )}
          </button>

          <button
            onClick={handleNext}
            className="text-slate-400 hover:text-white transition-colors"
          >
            <SkipForward className="w-8 h-8" />
          </button>
        </div>

        {/* Volume */}
        <div className="flex items-center gap-3 px-4 py-3 bg-white/5 rounded-xl">
          <Volume2 className="w-4 h-4 text-slate-400" />
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={volume}
            onChange={(e) => setVolume(parseFloat(e.target.value))}
            className="w-full h-1 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
          />
        </div>

        {/* Audio Element */}
        <audio
          ref={audioRef}
          src={currentTrack.url}
          onTimeUpdate={handleTimeUpdate}
          onEnded={handleNext}
        />
      </div>
    </div>
  );
}
