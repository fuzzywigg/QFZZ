export default function AboutPage() {
    return (
        <div className="min-h-screen p-8 text-white flex flex-col items-center">
            <h1 className="text-4xl font-bold mb-4 text-purple-400">About QFZZ</h1>
            <p className="max-w-xl text-center text-white/60">
                QFZZ is an autonomous, agentic radio station powered by the Hive Mind.
                It leverages advanced AI to curate, introduce, and visualize reliable content
                from the public domain.
            </p>
            <a href="/" className="mt-8 px-4 py-2 bg-white/10 rounded hover:bg-white/20 transition">
                Return to Stream
            </a>
        </div>
    );
}
