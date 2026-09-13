// HiveTerminal survives non-object DJ poll JSON (array / string).

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, act } from "@testing-library/react";
import HiveTerminal from "@/components/HiveTerminal";

describe("HiveTerminal poll payload shape edges", () => {
  beforeEach(() => {
    Element.prototype.scrollIntoView = vi.fn();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  it("survives array poll JSON without crashing", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ["not", "an", "object"],
      } as Response),
    );
    render(<HiveTerminal />);
    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    expect(screen.getByText("QUEEN NODE: ONLINE")).toBeInTheDocument();
  });

  it("survives string poll JSON without crashing", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => "broadcast",
      } as Response),
    );
    render(<HiveTerminal />);
    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    expect(screen.getByText("QUEEN NODE: ONLINE")).toBeInTheDocument();
  });
});
