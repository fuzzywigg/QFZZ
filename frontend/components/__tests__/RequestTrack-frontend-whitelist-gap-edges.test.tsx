// RequestTrack frontend whitelist gap (jamendo/wikipedia blocked).

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import RequestTrack from "@/components/RequestTrack";

describe("RequestTrack frontend whitelist gap edges", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it.each([
    "https://www.jamendo.com/track/123",
    "https://en.wikipedia.org/wiki/Music",
  ])("blocks %s without calling fetch", async (url) => {
    const user = userEvent.setup();
    render(<RequestTrack />);
    await user.type(screen.getByPlaceholderText(/Paste URL/), url);
    await user.click(screen.getByRole("button", { name: "Queue" }));

    expect(
      screen.getByText(/URL blocked. Only trusted public domain sources/),
    ).toBeInTheDocument();
    expect(fetch).not.toHaveBeenCalled();
  });
});
