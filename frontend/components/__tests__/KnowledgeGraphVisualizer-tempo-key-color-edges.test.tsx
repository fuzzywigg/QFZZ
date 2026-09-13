// KnowledgeGraphVisualizer tempo/musical_key node colors fall back to grey.

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, waitFor } from "@testing-library/react";
import KnowledgeGraphVisualizer from "@/components/KnowledgeGraphVisualizer";

vi.mock("react-force-graph-2d", () => ({
  default: (props: {
    graphData: { nodes: unknown[]; links: unknown[] };
    nodeColor?: (node: { type?: string }) => string;
  }) => {
    const colors = (props.graphData.nodes as { id: string; type?: string }[]).map((n) =>
      props.nodeColor ? props.nodeColor(n) : "",
    );
    return (
      <div
        data-testid="force-graph"
        data-node-count={props.graphData.nodes.length}
        data-colors={colors.join(",")}
      />
    );
  },
}));

describe("KnowledgeGraphVisualizer tempo/key color edges", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("colors tempo and musical_key nodes with grey fallback", async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({
        nodes: [
          { id: "tempo:120s BPM", type: "tempo" },
          { id: "key:Am", type: "musical_key" },
          { id: "track:1", type: "track" },
        ],
        links: [],
      }),
    } as Response);

    const { getByTestId } = render(<KnowledgeGraphVisualizer />);
    await waitFor(() => {
      expect(getByTestId("force-graph").getAttribute("data-node-count")).toBe("3");
    });
    const colors = getByTestId("force-graph").getAttribute("data-colors") || "";
    expect(colors.split(",")).toEqual(["#94a3b8", "#94a3b8", "#8b5cf6"]);
  });
});
