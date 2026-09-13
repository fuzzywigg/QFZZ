import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, waitFor } from "@testing-library/react";
import KnowledgeGraphVisualizer from "@/components/KnowledgeGraphVisualizer";

vi.mock("react-force-graph-2d", () => ({
  default: (props: {
    graphData: { nodes: unknown[]; links: unknown[] };
  }) => (
    <div
      data-testid="force-graph"
      data-node-count={props.graphData.nodes.length}
      data-link-count={props.graphData.links.length}
    />
  ),
}));

describe("KnowledgeGraphVisualizer null top-level payload", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("keeps empty graph when json() returns null", async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => null,
    } as Response);

    const { getByTestId } = render(<KnowledgeGraphVisualizer />);
    await waitFor(() => {
      expect(getByTestId("force-graph").getAttribute("data-node-count")).toBe("0");
    });
    expect(getByTestId("force-graph").getAttribute("data-link-count")).toBe("0");
  });
});
