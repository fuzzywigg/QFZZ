import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, waitFor } from "@testing-library/react";

vi.mock("react-force-graph-2d", () => ({
  default: (props: { graphData: { nodes: unknown[]; links: unknown[] } }) => (
    <div
      data-testid="force-graph"
      data-node-count={props.graphData.nodes.length}
    />
  ),
}));

describe("KnowledgeGraphVisualizer API base env", () => {
  beforeEach(() => {
    vi.resetModules();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ nodes: [], links: [] }),
    }));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
  });

  it("uses NEXT_PUBLIC_QFZZ_API_BASE when set", async () => {
    vi.stubEnv("NEXT_PUBLIC_QFZZ_API_BASE", "http://api.example.test:9000");
    const { default: KnowledgeGraphVisualizer } = await import(
      "@/components/KnowledgeGraphVisualizer"
    );
    render(<KnowledgeGraphVisualizer />);
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        "http://api.example.test:9000/graph.json",
      );
    });
  });

  it("defaults to localhost:8001 when API base unset", async () => {
    vi.stubEnv("NEXT_PUBLIC_QFZZ_API_BASE", "");
    const { default: KnowledgeGraphVisualizer } = await import(
      "@/components/KnowledgeGraphVisualizer"
    );
    render(<KnowledgeGraphVisualizer />);
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith("http://localhost:8001/graph.json");
    });
  });
});
