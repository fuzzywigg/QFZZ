import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import HiveTerminal from "@/components/HiveTerminal";

describe("HiveTerminal scroll-smooth edges", () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    Element.prototype.scrollIntoView = vi.fn();
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new Error("offline")),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("scrolls with smooth behavior after user transmit", async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    render(<HiveTerminal />);
    // Initial mount scrolls once; clear then assert send-triggered scroll
    vi.mocked(Element.prototype.scrollIntoView).mockClear();

    await user.type(screen.getByPlaceholderText("Transmit to Hive..."), "hello hive");
    await user.click(screen.getByRole("button", { name: "Send Message" }));

    await waitFor(() => {
      expect(Element.prototype.scrollIntoView).toHaveBeenCalledWith({
        behavior: "smooth",
      });
    });
  });
});
