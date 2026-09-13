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
        data-link-count={props.graphData.links.length}
        data-colors={colors.join(",")}
      />
    );
  },
}));

describe("KnowledgeGraphVisualizer", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("loads graph data and passes nodes/links to ForceGraph2D", async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({
        nodes: [
          { id: "track:1", type: "track" },
          { id: "artist:a", type: "artist" },
          { id: "genre:g", type: "genre" },
          { id: "other", type: "concept" },
        ],
        links: [{ source: "track:1", target: "artist:a" }],
      }),
    } as Response);

    const { getByTestId } = render(<KnowledgeGraphVisualizer />);

    await waitFor(() => {
      expect(getByTestId("force-graph").getAttribute("data-node-count")).toBe("4");
    });
    expect(getByTestId("force-graph").getAttribute("data-link-count")).toBe("1");
    expect(fetch).toHaveBeenCalledWith("http://localhost:8001/graph.json");
    const colors = getByTestId("force-graph").getAttribute("data-colors") || "";
    expect(colors).toContain("#8b5cf6");
    expect(colors).toContain("#3b82f6");
    expect(colors).toContain("#ec4899");
    expect(colors).toContain("#94a3b8");
  });

  it("defaults to empty graph when payload lacks nodes/links", async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({}),
    } as Response);

    const { getByTestId } = render(<KnowledgeGraphVisualizer />);
    await waitFor(() => {
      expect(getByTestId("force-graph").getAttribute("data-node-count")).toBe("0");
    });
  });

  it("survives fetch failures without crashing", async () => {
    const errSpy = vi.spyOn(console, "error").mockImplementation(() => {});
    vi.mocked(fetch).mockRejectedValue(new Error("offline"));

    const { getByTestId } = render(<KnowledgeGraphVisualizer />);
    await waitFor(() => {
      expect(getByTestId("force-graph")).toBeInTheDocument();
    });
    expect(getByTestId("force-graph").getAttribute("data-node-count")).toBe("0");
    errSpy.mockRestore();
  });

  it("ignores null JSON payload", async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => null,
    } as Response);
    const { getByTestId } = render(<KnowledgeGraphVisualizer />);
    await waitFor(() => {
      expect(getByTestId("force-graph").getAttribute("data-node-count")).toBe("0");
    });
  });

  it("defaults missing links and colors unknown node types grey", async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({
        nodes: [{ id: "n1" }, { id: "n2", type: "track" }],
      }),
    } as Response);
    const { getByTestId } = render(<KnowledgeGraphVisualizer />);
    await waitFor(() => {
      expect(getByTestId("force-graph").getAttribute("data-node-count")).toBe("2");
    });
    expect(getByTestId("force-graph").getAttribute("data-link-count")).toBe("0");
    const colors = getByTestId("force-graph").getAttribute("data-colors") || "";
    expect(colors).toContain("#94a3b8");
    expect(colors).toContain("#8b5cf6");
  });
});
