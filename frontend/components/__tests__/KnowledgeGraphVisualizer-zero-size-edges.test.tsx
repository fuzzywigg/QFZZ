// KnowledgeGraphVisualizer applies zero container dimensions.

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, waitFor } from "@testing-library/react";
import KnowledgeGraphVisualizer from "@/components/KnowledgeGraphVisualizer";

vi.mock("react-force-graph-2d", () => ({
  default: (props: {
    graphData: { nodes: unknown[]; links: unknown[] };
    width?: number;
    height?: number;
  }) => (
    <div
      data-testid="force-graph"
      data-width={String(props.width ?? "")}
      data-height={String(props.height ?? "")}
    />
  ),
}));

describe("KnowledgeGraphVisualizer zero-size edges", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("propagates zero offsetWidth/Height to ForceGraph2D", async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({ nodes: [], links: [] }),
    } as Response);

    const widthSpy = vi
      .spyOn(HTMLElement.prototype, "offsetWidth", "get")
      .mockReturnValue(0);
    const heightSpy = vi
      .spyOn(HTMLElement.prototype, "offsetHeight", "get")
      .mockReturnValue(0);

    const { getByTestId } = render(<KnowledgeGraphVisualizer />);
    await waitFor(() => {
      expect(getByTestId("force-graph").getAttribute("data-width")).toBe("0");
    });
    expect(getByTestId("force-graph").getAttribute("data-height")).toBe("0");
    widthSpy.mockRestore();
    heightSpy.mockRestore();
  });
});
