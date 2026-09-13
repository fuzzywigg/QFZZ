// HiveTerminal whitespace-truthy poll message injects AI bubble.

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, act } from "@testing-library/react";
import HiveTerminal from "@/components/HiveTerminal";

describe("HiveTerminal whitespace poll edges", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
    Element.prototype.scrollIntoView = vi.fn();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  it("injects whitespace-only poll message because it is truthy", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({ message: "   " }),
    } as Response);

    render(<HiveTerminal />);
    expect(screen.getAllByText("QUEEN")).toHaveLength(1);

    await act(async () => {
      vi.advanceTimersByTime(5000);
    });

    // Whitespace-only message is truthy, so poll injects another AI/QUEEN bubble.
    // DOM text normalizes spaces, so assert via QUEEN count rather than raw "   ".
    expect(screen.getAllByText("QUEEN")).toHaveLength(2);
  });
});
