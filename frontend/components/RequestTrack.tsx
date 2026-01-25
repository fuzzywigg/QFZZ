"use client";

import React, { useState } from 'react';
import { Download, AlertCircle, CheckCircle } from 'lucide-react';

export default function RequestTrack() {
    const [url, setUrl] = useState('');
    const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
    const [message, setMessage] = useState('');

    const handleRequest = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!url) return;

        // Basic client-side validation for instant feedback
        const whitelist = ['archive.org', 'freemusicarchive.org', 'musopen.org', 'librivox.org'];
        const isValid = whitelist.some(domain => url.includes(domain));

        if (!isValid) {
            setStatus('error');
            setMessage('URL blocked. Only trusted public domain sources allowed (Archive.org, FMA, etc).');
            return;
        }

        setStatus('loading');
        setMessage('Ingesting content...');

        try {
            const res = await fetch('http://localhost:8001/request', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });

            if (res.ok) {
                setStatus('success');
                setMessage('Track queued successfully!');
                setUrl('');
                // Reset after 3s
                setTimeout(() => {
                    setStatus('idle');
                    setMessage('');
                }, 3000);
            } else {
                setStatus('error');
                setMessage('Failed to process request. Check server logs.');
            }
        } catch (err) {
            setStatus('error');
            setMessage('Connection failed.');
        }
    };

    return (
        <div className="mt-6 p-4 rounded-xl bg-white/5 border border-white/10 backdrop-blur-md">
            <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
                <Download size={20} className="text-purple-400" />
                Request Content
            </h3>

            <form onSubmit={handleRequest} className="flex gap-2">
                <input
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="Paste URL (Archive.org, FMA only)..."
                    className="flex-1 bg-black/40 border border-white/20 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-purple-500 transition-colors"
                />
                <button
                    type="submit"
                    disabled={status === 'loading'}
                    className="bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white rounded-lg px-4 py-2 text-sm font-medium transition-colors"
                >
                    {status === 'loading' ? '...' : 'Queue'}
                </button>
            </form>

            {/* Allowed Domains Hint */}
            <p className="text-xs text-white/40 mt-2">
                Allowed: archive.org, freemusicarchive.org, musopen.org, librivox.org
            </p>

            {/* Feedback Message */}
            {message && (
                <div className={`mt-3 text-sm flex items-center gap-2 ${status === 'error' ? 'text-red-400' :
                        status === 'success' ? 'text-green-400' : 'text-blue-400'
                    }`}>
                    {status === 'error' ? <AlertCircle size={16} /> :
                        status === 'success' ? <CheckCircle size={16} /> : null}
                    {message}
                </div>
            )}
        </div>
    );
}
