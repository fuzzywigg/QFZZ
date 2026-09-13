import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import RequestTrack from "@/components/RequestTrack";

describe("RequestTrack", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  it("renders request form and allowed domains hint", () => {
    render(<RequestTrack />);
    expect(screen.getByText("Request Content")).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText(/Paste URL \(Archive.org, FMA only\)/),
    ).toBeInTheDocument();
    expect(screen.getByText(/Allowed: archive.org/)).toBeInTheDocument();
  });

  it("rejects non-whitelisted URLs without calling the API", async () => {
    const user = userEvent.setup();
    render(<RequestTrack />);

    await user.type(
      screen.getByPlaceholderText(/Paste URL/),
      "https://evil.example/track",
    );
    await user.click(screen.getByRole("button", { name: "Queue" }));

    expect(
      screen.getByText(/URL blocked. Only trusted public domain sources/),
    ).toBeInTheDocument();
    expect(fetch).not.toHaveBeenCalled();
  });

  it("queues a whitelisted URL on success", async () => {
    const user = userEvent.setup();
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({}),
    } as Response);

    render(<RequestTrack />);
    await user.type(
      screen.getByPlaceholderText(/Paste URL/),
      "https://archive.org/details/demo",
    );
    await user.click(screen.getByRole("button", { name: "Queue" }));

    await waitFor(() => {
      expect(screen.getByText("Track queued successfully!")).toBeInTheDocument();
    });
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/request",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ url: "https://archive.org/details/demo" }),
      }),
    );
  });

  it("shows connection failed when fetch throws", async () => {
    const user = userEvent.setup();
    vi.mocked(fetch).mockRejectedValue(new Error("offline"));

    render(<RequestTrack />);
    await user.type(
      screen.getByPlaceholderText(/Paste URL/),
      "https://musopen.org/music/1",
    );
    await user.click(screen.getByRole("button", { name: "Queue" }));

    await waitFor(() => {
      expect(screen.getByText("Connection failed.")).toBeInTheDocument();
    });
  });

  it("ignores empty URL submit", async () => {
    const user = userEvent.setup();
    render(<RequestTrack />);
    await user.click(screen.getByRole("button", { name: "Queue" }));
    expect(fetch).not.toHaveBeenCalled();
    expect(screen.queryByText(/queued|blocked|failed|Ingesting/i)).not.toBeInTheDocument();
  });

  it("shows server failure when response is not ok", async () => {
    const user = userEvent.setup();
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({}),
    } as Response);

    render(<RequestTrack />);
    await user.type(
      screen.getByPlaceholderText(/Paste URL/),
      "https://freemusicarchive.org/track/1",
    );
    await user.click(screen.getByRole("button", { name: "Queue" }));

    await waitFor(() => {
      expect(
        screen.getByText("Failed to process request. Check server logs."),
      ).toBeInTheDocument();
    });
  });

  it("shows loading state then resets after success timeout", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    let resolveFetch: (value: Response) => void = () => undefined;
    vi.mocked(fetch).mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveFetch = resolve;
        }),
    );

    render(<RequestTrack />);
    await user.type(
      screen.getByPlaceholderText(/Paste URL/),
      "https://librivox.org/book/1",
    );
    await user.click(screen.getByRole("button", { name: "Queue" }));

    expect(screen.getByRole("button", { name: "..." })).toBeDisabled();
    expect(screen.getByText("Ingesting content...")).toBeInTheDocument();

    await act(async () => {
      resolveFetch({ ok: true, json: async () => ({}) } as Response);
    });
    await waitFor(() => {
      expect(screen.getByText("Track queued successfully!")).toBeInTheDocument();
    });

    await act(async () => {
      vi.advanceTimersByTime(3000);
    });
    await waitFor(() => {
      expect(screen.queryByText("Track queued successfully!")).not.toBeInTheDocument();
    });
  });
});
