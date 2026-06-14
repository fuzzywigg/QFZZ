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

interface StreamSession {
  state: string;
  current_track: Track | null;
  prefetch_tracks: Track[];
  buffer_seconds: number;
  reconnect: {
    attempts: number;
    max_attempts: number;
  };
  error: string | null;
}

const API_BASE = process.env.NEXT_PUBLIC_QFZZ_API_BASE || 'http://localhost:8000';

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
  const [streamSession, setStreamSession] = useState<StreamSession | null>(null);
  const [streamStatus, setStreamStatus] = useState('Connecting');
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    const loadSession = () => {
      fetch(`${API_BASE}/stream/session.json`)
        .then(res => res.json())
        .then((data: StreamSession) => {
          setStreamSession(data);
          setStreamStatus(data.state);
          const merged: Track[] = [];
          if (data.current_track) {
            merged.push(data.current_track);
          }
          if (Array.isArray(data.prefetch_tracks)) {
            merged.push(...data.prefetch_tracks);
          }
          if (merged.length > 0) {
            setPlaylist(merged);
            setCurrentTrackIndex(0);
          }
        })
        .catch(() => setStreamStatus('Offline'));
    };

    // 1. Fetch playlist/session
    fetch(`${API_BASE}/playlist.json`)
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          setPlaylist(data);
        }
      })
      .catch(() => undefined);
    loadSession();

    // 2. Poll for Ledger (every 5 seconds)
    const pollStats = setInterval(() => {
      fetch(`${API_BASE}/ledger.json`)
        .then(res => res.json())
        .then(data => {
          if (data) setLedgerStats(data);
        })
        .catch(() => undefined);
      loadSession();
    }, 5000);

    return () => clearInterval(pollStats);
  }, []);

  useEffect(() => {
    if (!streamSession || streamSession.prefetch_tracks.length === 0) {
      return;
    }
    streamSession.prefetch_tracks.slice(0, 2).forEach((track) => {
      if (!track.url) {
        return;
      }
      const prefetchAudio = new Audio();
      prefetchAudio.preload = 'auto';
      prefetchAudio.src = track.url;
    });
  }, [streamSession]);

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

  const handleAudioError = () => {
    setStreamStatus('Reconnecting');
    fetch(`${API_BASE}/stream/reconnect`, { method: 'POST' })
      .then((res) => {
        if (!res.ok) {
          throw new Error('reconnect failed');
        }
        return res.json() as Promise<{ recovered: boolean }>;
      })
      .then((body) => {
        if (!body.recovered || !audioRef.current) {
          return;
        }
        setTimeout(() => {
          audioRef.current?.load();
          audioRef.current?.play().catch(() => undefined);
          setStreamStatus('Playing');
        }, 400);
      })
      .catch(() => setStreamStatus('Error'));
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
          <p className="text-xs text-slate-400 uppercase tracking-wider">
            {streamStatus} • Buffer {streamSession?.buffer_seconds ?? 0}s
          </p>
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
          preload="auto"
          onTimeUpdate={handleTimeUpdate}
          onEnded={handleNext}
          onError={handleAudioError}
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
