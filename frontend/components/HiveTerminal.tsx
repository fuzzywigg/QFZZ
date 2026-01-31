"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Send, Hexagon } from 'lucide-react';

export default function HiveTerminal() {
    const [messages, setMessages] = useState<{ sender: 'AI' | 'USER' | 'SYSTEM', text: string }[]>([
        { sender: 'SYSTEM', text: 'CONNECTING TO HIVE NET...' },
        { sender: 'SYSTEM', text: 'QUEEN NODE: ONLINE' },
        { sender: 'AI', text: 'Greetings, Drone. The Hive is listening. What is your frequency?' }
    ]);
    const [input, setInput] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Poll for real DJ Messages and inject them as AI chatter
    useEffect(() => {
        const poll = setInterval(() => {
            fetch('http://localhost:8001/dj_message.json')
                .then(res => res.json())
                .then(data => {
                    if (data && data.message) {
                        setMessages(prev => {
                            // Deduplicate last AI message
                            if (prev.length > 0 && prev[prev.length - 1].text === data.message) return prev;
                            return [...prev, { sender: 'AI', text: data.message }];
                        });
                    }
                })
                .catch(() => { });
        }, 5000);
        return () => clearInterval(poll);
    }, []);

    const handleSend = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        // Add user message
        const userMsg = input;
        setMessages(prev => [...prev, { sender: 'USER', text: userMsg }]);
        setInput('');

        // Simulate Agency (for now) until actual Chat API is ready
        setTimeout(() => {
            const responses = [
                "Processing signal...",
                "The Queen acknowledges your input.",
                "Frequency aligned. Scanning...",
                "Pattern recognized."
            ];
            const randomResponse = responses[Math.floor(Math.random() * responses.length)];
            setMessages(prev => [...prev, { sender: 'AI', text: randomResponse }]);
        }, 1000);
    };

    return (
        <div className="w-full max-w-4xl bg-black/80 border border-amber-500/30 rounded-xl overflow-hidden shadow-[0_0_30px_rgba(245,158,11,0.1)] flex flex-col h-[300px]">
            {/* Header */}
            <div className="bg-amber-900/20 px-4 py-2 flex items-center justify-between border-b border-amber-500/20">
                <div className="flex items-center gap-2 text-amber-500/80">
                    <Hexagon size={16} className="fill-amber-500/10" />
                    <span className="text-xs font-mono tracking-widest uppercase font-bold">HiveOS v2.0 // Interactive Link</span>
                </div>
                <div className="flex gap-1">
                    <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div>
                    <div className="w-2 h-2 rounded-full bg-amber-500/50"></div>
                    <div className="w-2 h-2 rounded-full bg-amber-500/20"></div>
                </div>
            </div>

            {/* Terminal Output */}
            <div className="flex-1 p-4 overflow-y-auto font-mono text-sm space-y-2 scrollbar-thin scrollbar-thumb-amber-900 scrollbar-track-transparent">
                {messages.map((msg, i) => (
                    <div key={i} className={`flex gap-3 ${msg.sender === 'USER' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] px-3 py-1.5 rounded ${msg.sender === 'USER'
                            ? 'bg-amber-500/10 text-amber-100 border border-amber-500/20'
                            : msg.sender === 'SYSTEM'
                                ? 'text-green-500 italic text-xs'
                                : 'text-amber-400'
                            }`}>
                            <span className="text-[10px] opacity-50 block mb-0.5">
                                {msg.sender === 'AI' ? 'QUEEN' : msg.sender}
                            </span>
                            {msg.text}
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <form onSubmit={handleSend} className="p-2 border-t border-amber-500/20 bg-black/50 flex gap-2">
                <div className="flex-1 relative">
                    <Terminal size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-amber-600" />
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Transmit to Hive..."
                        className="w-full bg-amber-900/10 border border-amber-500/20 rounded-md pl-9 pr-4 py-2 text-amber-100 text-sm focus:outline-none focus:border-amber-500 transition-colors font-mono"
                    />
                </div>
                <button
                    type="submit"
                    title="Send"
                    aria-label="Send Message"
                    className="bg-amber-600 hover:bg-amber-500 text-black font-bold p-2 rounded-md transition-colors"
                >
                    <Send size={16} />
                </button>
            </form>
        </div>
    );
}
