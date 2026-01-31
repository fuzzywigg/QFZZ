"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, SkipForward, Radio, Volume2, Menu, X } from 'lucide-react';
import dynamic from 'next/dynamic';

const KnowledgeGraphVisualizer = dynamic(() => import('../components/KnowledgeGraphVisualizer'), {
  ssr: false,
  loading: () => <div className="h-[400px] w-full animate-pulse bg-white/5 rounded-xl"></div>
});

const HiveTerminal = dynamic(() => import('../components/HiveTerminal'), {
  ssr: false
});

const RequestTrack = dynamic(() => import('../components/RequestTrack'), {
  ssr: false
});

interface Track {
  title: string;
  artist: string;
  url: string;
  genre: string;
}

export default function AudioPlayer() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(0.8);
  const [playlist, setPlaylist] = useState<Track[]>([]);
  const [currentTrackIndex, setCurrentTrackIndex] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  // DJ Message is now handled by HiveTerminal, but we might want to keep track of "Now Playing" context if needed.
  // We'll keep the poller for playlist updates/ledger.
  const [ledgerStats, setLedgerStats] = useState({ height: 0, status: "Init" });
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    // 1. Fetch playlist
    fetch('http://localhost:8001/playlist.json')
      .then(res => res.json())
      .then(data => {
        if (data && data.length > 0) {
          setPlaylist(data);
          console.log("Loaded playlist:", data);
        }
      })
      .catch(err => console.error("Failed to load playlist:", err));

    // 2. Poll for Ledger (every 5 seconds)
    const pollStats = setInterval(() => {
      fetch('http://localhost:8001/ledger.json')
        .then(res => res.json())
        .then(data => {
          if (data) setLedgerStats(data);
        })
        .catch(e => console.error("Ledger poll failed", e));
    }, 5000);

    return () => clearInterval(pollStats);
  }, []);

  const currentTrack = playlist[currentTrackIndex] || {
    title: "Connecting to Quantum Stream...",
    artist: "QFZZ System",
    url: "",
    genre: "System"
  };

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume;
    }
  }, [volume]);

  // Removed Canvas Visualizer logic (waste of resources, replaced with CSS bars)

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play().catch(e => console.error("Play failed:", e));
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
    if (playlist.length === 0) return;

    setCurrentTrackIndex((prev) => (prev + 1) % playlist.length);
    setIsPlaying(false);
    setTimeout(() => {
      if (audioRef.current) {
        audioRef.current.load();
        audioRef.current.play().catch(e => console.error("Play next failed:", e));
        setIsPlaying(true);
      }
    }, 100);
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
      <div className="absolute top-0 left-0 w-full p-6 flex justify-between items-center z-50">
        <div className="flex items-center gap-3">
          <Radio className="w-6 h-6 text-purple-400" />
          <h1 className="text-xl font-bold tracking-tighter text-white">
            QFZZ Prime
          </h1>
        </div>

        <button
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          className="p-2 text-white/70 hover:text-white hover:bg-white/10 rounded-lg transition-colors z-50"
        >
          {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Navigation Overlay */}
      {isMenuOpen && (
        <div className="fixed inset-0 bg-black/90 backdrop-blur-xl z-40 flex flex-col items-center justify-center space-y-8 animate-in fade-in duration-200">
          <nav className="flex flex-col items-center gap-6 text-2xl font-light tracking-widest text-white/80">
            <a href="/library" className="hover:text-purple-400 hover:scale-110 transition-all">Music Library</a>
            <a href="/guide" className="hover:text-purple-400 hover:scale-110 transition-all">Listener Guide</a>
            <a href="/about" className="hover:text-purple-400 hover:scale-110 transition-all">About QFZZ</a>
            <a href="/contact" className="hover:text-purple-400 hover:scale-110 transition-all">Contact</a>
          </nav>
          <div className="w-16 h-[1px] bg-white/20"></div>
          <p className="text-sm text-white/40 font-mono">v0.9.2 Beta // Quantum Stream</p>
        </div>
      )}

      <div className="text-center space-y-2 z-10 mt-12">
        <p className="text-slate-400 text-sm tracking-widest uppercase">The Pulse of the Quantum Realm</p>
      </div>

      {/* Main Player Card */}
      <div className="w-full max-w-md bg-slate-900/80 backdrop-blur-xl border border-white/10 rounded-3xl p-6 shadow-2xl relative">

        {/* Minimal Visualizer (replaces canvas) */}
        <div className="h-4 w-full mb-6 bg-transparent flex items-end justify-center gap-1 opacity-50">
          <div className={`w-1 h-3 bg-purple-500 rounded-full ${isPlaying ? 'animate-pulse' : ''}`}></div>
          <div className={`w-1 h-5 bg-purple-500 rounded-full ${isPlaying ? 'animate-pulse' : ''} delay-75`}></div>
          <div className={`w-1 h-2 bg-purple-500 rounded-full ${isPlaying ? 'animate-pulse' : ''} delay-150`}></div>
          <div className={`w-1 h-4 bg-purple-500 rounded-full ${isPlaying ? 'animate-pulse' : ''} delay-100`}></div>
          <div className={`w-1 h-2 bg-purple-500 rounded-full ${isPlaying ? 'animate-pulse' : ''} delay-200`}></div>
        </div>

        {/* Track Info */}
        <div className="text-center mb-8 space-y-1">
          <h2 className="text-xl font-bold text-white truncate">{currentTrack.title}</h2>
          <p className="text-purple-300 text-sm">{currentTrack.artist}</p>
          <span className="inline-block px-2 py-0.5 mt-2 bg-purple-500/10 border border-purple-500/20 rounded text-[10px] text-purple-300 uppercase tracking-wider">
            {currentTrack.genre || 'Unknown'}
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
            type="button"
            title="Toggle Play/Pause"
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
            type="button"
            title="Next Track"
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
            aria-label="Volume Control"
            title="Volume Control"
            className="w-full h-1 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
          />
        </div>

        {/* Audio Element */}
        <audio
          ref={audioRef}
          src={currentTrack.url || undefined}
          onTimeUpdate={handleTimeUpdate}
          onEnded={handleNext}
        />
      </div>

      {/* Hive Terminal (Replaces old static DJ message) */}
      <HiveTerminal />

      {/* Knowledge Graph Visualization */}
      <div className="w-full max-w-4xl space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="text-xl font-bold text-white/50 uppercase tracking-widest">
            Semantic Knowledge Graph
          </h3>
          <div className="text-xs text-green-400 font-mono flex gap-4">
            <span>Ledger Height: {ledgerStats.height}</span>
            <span>Trust Status: {ledgerStats.status}</span>
          </div>
        </div>
        <KnowledgeGraphVisualizer />
      </div>

      {/* Request Track */}
      <RequestTrack />
    </div>
  );
}
