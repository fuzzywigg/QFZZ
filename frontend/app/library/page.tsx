export default function LibraryPage() {
    return (
        <div className="min-h-screen p-8 text-white flex flex-col items-center">
            <h1 className="text-4xl font-bold mb-4 text-purple-400">Music Library</h1>
            <p className="max-w-xl text-center text-white/60">
                Explore the Hive's vast collection of public domain frequencies.
                (This section will be populated with the full searchable catalog soon.)
            </p>
            <a href="/" className="mt-8 px-4 py-2 bg-white/10 rounded hover:bg-white/20 transition">
                Return to Stream
            </a>
        </div>
    );
}
