import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, waitFor } from "@testing-library/react";
import KnowledgeGraphVisualizer from "@/components/KnowledgeGraphVisualizer";

vi.mock("react-force-graph-2d", () => ({
  default: () => <div data-testid="force-graph" data-node-count="0" />,
}));

describe("KnowledgeGraphVisualizer fetch reject log", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("logs Failed to load knowledge graph when fetch rejects", async () => {
    const errSpy = vi.spyOn(console, "error").mockImplementation(() => {});
    vi.mocked(fetch).mockRejectedValue(new Error("offline"));

    render(<KnowledgeGraphVisualizer />);
    await waitFor(() => {
      expect(errSpy).toHaveBeenCalledWith(
        "Failed to load knowledge graph",
        expect.any(Error),
      );
    });
    errSpy.mockRestore();
  });
});
