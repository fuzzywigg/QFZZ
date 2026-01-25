"use client";

import React, { useEffect, useState, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

export default function KnowledgeGraphVisualizer() {
    const [graphData, setGraphData] = useState({ nodes: [], links: [] });
    const [dimensions, setDimensions] = useState({ width: 500, height: 400 });
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Dimension observer
        if (containerRef.current) {
            setDimensions({
                width: containerRef.current.offsetWidth,
                height: containerRef.current.offsetHeight
            });
        }

        fetch('http://localhost:8001/graph.json')
            .then(res => res.json())
            .then(data => {
                if (data) {
                    setGraphData({
                        nodes: data.nodes || [],
                        links: data.links || []
                    });
                }
            })
            .catch(err => console.error("Failed to load knowledge graph", err));
    }, []);

    return (
        <div ref={containerRef} className="w-full h-[400px] border border-white/10 rounded-xl overflow-hidden bg-black/40 backdrop-blur-sm">
            <ForceGraph2D
                width={dimensions.width}
                height={dimensions.height}
                graphData={graphData}
                nodeLabel="id"
                nodeColor={(node: any) => {
                    if (node.type === 'track') return '#8b5cf6'; // Purple
                    if (node.type === 'artist') return '#3b82f6'; // Blue
                    if (node.type === 'genre') return '#ec4899'; // Pink
                    return '#94a3b8'; // Grey
                }}
                nodeRelSize={6}
                linkColor={() => 'rgba(255,255,255,0.2)'}
                backgroundColor="transparent"
            />
        </div>
    );
}
