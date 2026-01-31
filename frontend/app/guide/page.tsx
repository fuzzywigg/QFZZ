export default function GuidePage() {
    return (
        <div className="min-h-screen p-8 text-white flex flex-col items-center">
            <h1 className="text-4xl font-bold mb-4 text-purple-400">Listener Guide</h1>
            <div className="max-w-xl text-white/80 space-y-4">
                <p>Welcome to QFZZ Prime, the pulse of the Quantum Realm.</p>
                <h2 className="text-xl font-semibold text-white mt-6">How to Interact</h2>
                <ul className="list-disc pl-5 space-y-2">
                    <li>Use the <strong>Request Track</strong> input to queue verified public domain songs.</li>
                    <li>Watch the <strong>Hive Terminal</strong> for updates from the Queen Node.</li>
                    <li>Observe the <strong>Semantic Knowledge Graph</strong> as it maps concepts in real-time.</li>
                </ul>
            </div>
            <a href="/" className="mt-8 px-4 py-2 bg-white/10 rounded hover:bg-white/20 transition">
                Return to Stream
            </a>
        </div>
    );
}
