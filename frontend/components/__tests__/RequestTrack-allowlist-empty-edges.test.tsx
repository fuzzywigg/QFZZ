// RequestTrack librivox allowlist + empty-url submit no-op edges.

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import RequestTrack from "@/components/RequestTrack";

describe("RequestTrack allowlist / empty submit edges", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("queues librivox.org URLs", async () => {
    const user = userEvent.setup();
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({}),
    } as Response);

    render(<RequestTrack />);
    await user.type(
      screen.getByPlaceholderText(/Paste URL/),
      "https://librivox.org/some-book",
    );
    await user.click(screen.getByRole("button", { name: "Queue" }));

    await waitFor(() => {
      expect(screen.getByText("Track queued successfully!")).toBeInTheDocument();
    });
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/request",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ url: "https://librivox.org/some-book" }),
      }),
    );
  });

  it("ignores empty URL submit without calling fetch", async () => {
    const user = userEvent.setup();
    render(<RequestTrack />);
    await user.click(screen.getByRole("button", { name: "Queue" }));
    expect(fetch).not.toHaveBeenCalled();
    expect(screen.queryByText(/queued|failed|blocked|Connection/i)).not.toBeInTheDocument();
  });
});
