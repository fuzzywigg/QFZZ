import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, act, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

vi.mock("next/dynamic", () => ({
  default: () => {
    const Stub = () => <div data-testid="dynamic-stub" />;
    Stub.displayName = "DynamicStub";
    return Stub;
  },
}));

import AudioPlayer from "@/app/page";

function mockAudioElement() {
  const audioProto = window.HTMLAudioElement.prototype;
  vi.spyOn(audioProto, "play").mockResolvedValue(undefined as never);
  vi.spyOn(audioProto, "pause").mockImplementation(() => undefined);
  vi.spyOn(audioProto, "load").mockImplementation(() => undefined);
}

describe("AudioPlayer page", () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    mockAudioElement();
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new Error("offline")),
    );
    vi.stubGlobal(
      "Audio",
      vi.fn().mockImplementation(() => ({
        preload: "",
        src: "",
      })),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("shows connecting fallback when fetches fail", async () => {
    render(<AudioPlayer />);
    expect(screen.getByText("Connecting to Quantum Stream...")).toBeInTheDocument();
    expect(screen.getByText("QFZZ System")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText(/Offline/)).toBeInTheDocument();
    });
    expect(screen.getByText(/Buffer 0s/)).toBeInTheDocument();
  });

  it("merges session tracks and polls ledger stats", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/stream/session.json")) {
        return {
          ok: true,
          json: async () => ({
            state: "playing",
            current_track: {
              title: "Pulse",
              artist: "Qubit",
              url: "http://localhost/a.wav",
              genre: "",
            },
            prefetch_tracks: [
              {
                title: "Next",
                artist: "Qubit",
                url: "http://localhost/b.wav",
                genre: "ambient",
              },
              { title: "NoUrl", artist: "X", url: "", genre: "x" },
            ],
            buffer_seconds: 12,
            reconnect: { attempts: 0, max_attempts: 3 },
            error: null,
          }),
        } as Response;
      }
      if (url.includes("/playlist.json")) {
        return { ok: true, json: async () => ({}) } as Response;
      }
      if (url.includes("/ledger.json")) {
        return {
          ok: true,
          json: async () => ({ height: 42, status: "Trusted" }),
        } as Response;
      }
      return { ok: true, json: async () => ({}) } as Response;
    });

    render(<AudioPlayer />);

    await waitFor(() => {
      expect(screen.getByText("Pulse")).toBeInTheDocument();
    });
    expect(screen.getByText("Qubit")).toBeInTheDocument();
    expect(screen.getByText("Unknown")).toBeInTheDocument();
    expect(screen.getByText(/Buffer 12s/)).toBeInTheDocument();

    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    await waitFor(() => {
      expect(screen.getByText("Ledger Height: 42")).toBeInTheDocument();
    });
    expect(screen.getByText("Trust Status: Trusted")).toBeInTheDocument();
    expect(Audio).toHaveBeenCalled();
  });

  it("toggles play/pause and advances next track", async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/stream/session.json")) {
        return {
          ok: true,
          json: async () => ({
            state: "stopped",
            current_track: {
              title: "One",
              artist: "A",
              url: "http://localhost/1.wav",
              genre: "jazz",
            },
            prefetch_tracks: [
              {
                title: "Two",
                artist: "B",
                url: "http://localhost/2.wav",
                genre: "jazz",
              },
            ],
            buffer_seconds: 4,
            reconnect: { attempts: 0, max_attempts: 3 },
            error: null,
          }),
        } as Response;
      }
      return { ok: true, json: async () => ([]) } as Response;
    });

    render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("One")).toBeInTheDocument());

    await user.click(screen.getByTitle("Toggle Play/Pause"));
    expect(window.HTMLAudioElement.prototype.play).toHaveBeenCalled();

    await user.click(screen.getByTitle("Next Track"));
    await waitFor(() => expect(screen.getByText("Two")).toBeInTheDocument());
    await act(async () => {
      vi.advanceTimersByTime(120);
    });
    expect(window.HTMLAudioElement.prototype.load).toHaveBeenCalled();
  });

  it("sets Error status when reconnect fails", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/stream/reconnect")) {
        return { ok: false, status: 503, json: async () => ({}) } as Response;
      }
      if (url.includes("/stream/session.json")) {
        return {
          ok: true,
          json: async () => ({
            state: "playing",
            current_track: {
              title: "Live",
              artist: "A",
              url: "http://localhost/l.wav",
              genre: "x",
            },
            prefetch_tracks: [],
            buffer_seconds: 1,
            reconnect: { attempts: 0, max_attempts: 3 },
            error: null,
          }),
        } as Response;
      }
      return { ok: true, json: async () => ([]) } as Response;
    });

    const { container } = render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("Live")).toBeInTheDocument());
    const audio = container.querySelector("audio");
    expect(audio).toBeTruthy();
    fireEvent.error(audio!);
    await waitFor(() => {
      expect(screen.getByText(/Error/)).toBeInTheDocument();
    });
  });

  it("exposes volume control and menu links", async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    render(<AudioPlayer />);
    const volume = screen.getByLabelText("Volume Control");
    fireEvent.change(volume, { target: { value: "0.3" } });
    expect((volume as HTMLInputElement).value).toBe("0.3");

    // First unlabeled header button toggles the nav overlay
    const headerButtons = screen
      .getAllByRole("button")
      .filter((b) => !b.getAttribute("title"));
    await user.click(headerButtons[0]);
    expect(screen.getByRole("link", { name: "Music Library" })).toHaveAttribute(
      "href",
      "/library",
    );
    expect(screen.getByRole("link", { name: "Listener Guide" })).toHaveAttribute(
      "href",
      "/guide",
    );
    expect(screen.getByRole("link", { name: "About QFZZ" })).toHaveAttribute(
      "href",
      "/about",
    );
    expect(screen.getByRole("link", { name: "Contact" })).toHaveAttribute(
      "href",
      "/contact",
    );
  });

  it("next with empty playlist is a no-op", async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    render(<AudioPlayer />);
    await user.click(screen.getByTitle("Next Track"));
    expect(screen.getByText("Connecting to Quantum Stream...")).toBeInTheDocument();
  });

  it("loads playlist.json array when session has no tracks", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/playlist.json")) {
        return {
          ok: true,
          json: async () => [
            {
              title: "FromPlaylist",
              artist: "PL",
              url: "http://localhost/p.wav",
              genre: "ambient",
            },
          ],
        } as Response;
      }
      if (url.includes("/stream/session.json")) {
        return {
          ok: true,
          json: async () => ({
            state: "stopped",
            current_track: null,
            prefetch_tracks: [],
            buffer_seconds: 0,
            reconnect: { attempts: 0, max_attempts: 3 },
            error: null,
          }),
        } as Response;
      }
      return { ok: true, json: async () => ({}) } as Response;
    });

    render(<AudioPlayer />);
    await waitFor(() => {
      expect(screen.getByText("FromPlaylist")).toBeInTheDocument();
    });
    expect(screen.getByText("ambient")).toBeInTheDocument();
  });

  it("pauses on second toggle and recovers on reconnect success", async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/stream/reconnect")) {
        return {
          ok: true,
          json: async () => ({ recovered: true }),
        } as Response;
      }
      if (url.includes("/stream/session.json")) {
        return {
          ok: true,
          json: async () => ({
            state: "playing",
            current_track: {
              title: "Live",
              artist: "A",
              url: "http://localhost/l.wav",
              genre: "x",
            },
            prefetch_tracks: [
              { title: "P1", artist: "A", url: "http://localhost/p1.wav", genre: "x" },
              { title: "Empty", artist: "A", url: "", genre: "x" },
              { title: "P2", artist: "A", url: "http://localhost/p2.wav", genre: "x" },
            ],
            buffer_seconds: 2,
            reconnect: { attempts: 0, max_attempts: 3 },
            error: null,
          }),
        } as Response;
      }
      return { ok: true, json: async () => ([]) } as Response;
    });

    const { container } = render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("Live")).toBeInTheDocument());

    await user.click(screen.getByTitle("Toggle Play/Pause"));
    expect(window.HTMLAudioElement.prototype.play).toHaveBeenCalled();
    await user.click(screen.getByTitle("Toggle Play/Pause"));
    expect(window.HTMLAudioElement.prototype.pause).toHaveBeenCalled();

    // Prefetch only non-empty URLs, capped at 2
    const audioCalls = vi.mocked(Audio).mock.calls.length;
    expect(audioCalls).toBeGreaterThanOrEqual(1);
    expect(audioCalls).toBeLessThanOrEqual(2);

    const audio = container.querySelector("audio");
    fireEvent.error(audio!);
    await waitFor(() => expect(screen.getByText(/Reconnecting|Playing/)).toBeInTheDocument());
    await act(async () => {
      vi.advanceTimersByTime(500);
    });
    await waitFor(() => {
      expect(screen.getByText(/Playing/)).toBeInTheDocument();
    });
  });

  it("wraps next from last track and updates time display on timeupdate", async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/stream/session.json")) {
        return {
          ok: true,
          json: async () => ({
            state: "stopped",
            current_track: {
              title: "First",
              artist: "A",
              url: "http://localhost/1.wav",
              genre: "g",
            },
            prefetch_tracks: [
              {
                title: "Second",
                artist: "B",
                url: "http://localhost/2.wav",
                genre: "g",
              },
            ],
            buffer_seconds: 3,
            reconnect: { attempts: 0, max_attempts: 3 },
            error: null,
          }),
        } as Response;
      }
      return { ok: true, json: async () => ([]) } as Response;
    });

    const { container } = render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("First")).toBeInTheDocument());

    await user.click(screen.getByTitle("Next Track"));
    await waitFor(() => expect(screen.getByText("Second")).toBeInTheDocument());
    await user.click(screen.getByTitle("Next Track"));
    await waitFor(() => expect(screen.getByText("First")).toBeInTheDocument());

    const audio = container.querySelector("audio") as HTMLAudioElement;
    Object.defineProperty(audio, "currentTime", { configurable: true, value: 65 });
    Object.defineProperty(audio, "duration", { configurable: true, value: 125 });
    fireEvent.timeUpdate(audio);
    await waitFor(() => {
      expect(screen.getByText("1:05")).toBeInTheDocument();
      expect(screen.getByText("2:05")).toBeInTheDocument();
    });

    fireEvent.ended(audio);
    await waitFor(() => expect(screen.getByText("Second")).toBeInTheDocument());
  });

  it("closes menu overlay on second click and keeps Init ledger on reject", async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/ledger.json")) {
        return Promise.reject(new Error("ledger down"));
      }
      if (url.includes("/stream/session.json")) {
        return {
          ok: true,
          json: async () => ({
            state: "Offline",
            current_track: null,
            prefetch_tracks: [],
            buffer_seconds: 0,
            reconnect: { attempts: 0, max_attempts: 3 },
            error: null,
          }),
        } as Response;
      }
      return { ok: true, json: async () => ([]) } as Response;
    });

    render(<AudioPlayer />);
    const headerButtons = screen
      .getAllByRole("button")
      .filter((b) => !b.getAttribute("title"));
    await user.click(headerButtons[0]);
    expect(screen.getByRole("link", { name: "Music Library" })).toBeInTheDocument();
    await user.click(headerButtons[0]);
    expect(screen.queryByRole("link", { name: "Music Library" })).not.toBeInTheDocument();

    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    expect(screen.getByText("Ledger Height: 0")).toBeInTheDocument();
    expect(screen.getByText("Trust Status: Init")).toBeInTheDocument();
  });

  it("logs play failures without crashing", async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    const errSpy = vi.spyOn(console, "error").mockImplementation(() => {});
    vi.spyOn(window.HTMLAudioElement.prototype, "play").mockRejectedValue(
      new Error("autoplay blocked"),
    );
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/stream/session.json")) {
        return {
          ok: true,
          json: async () => ({
            state: "stopped",
            current_track: {
              title: "Blocked",
              artist: "A",
              url: "http://localhost/b.wav",
              genre: "g",
            },
            prefetch_tracks: [],
            buffer_seconds: 1,
            reconnect: { attempts: 0, max_attempts: 3 },
            error: null,
          }),
        } as Response;
      }
      return { ok: true, json: async () => ([]) } as Response;
    });

    render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("Blocked")).toBeInTheDocument());
    await user.click(screen.getByTitle("Toggle Play/Pause"));
    await waitFor(() => {
      expect(errSpy).toHaveBeenCalled();
    });
    errSpy.mockRestore();
  });

  it("leaves Reconnecting when recovered is false", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/stream/reconnect")) {
        return {
          ok: true,
          json: async () => ({ recovered: false }),
        } as Response;
      }
      if (url.includes("/stream/session.json")) {
        return {
          ok: true,
          json: async () => ({
            state: "playing",
            current_track: {
              title: "Stuck",
              artist: "A",
              url: "http://localhost/s.wav",
              genre: "x",
            },
            prefetch_tracks: [],
            buffer_seconds: 1,
            reconnect: { attempts: 0, max_attempts: 3 },
            error: null,
          }),
        } as Response;
      }
      return { ok: true, json: async () => ([]) } as Response;
    });

    const { container } = render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("Stuck")).toBeInTheDocument());
    const loadCalls = vi.mocked(window.HTMLAudioElement.prototype.load).mock.calls.length;
    fireEvent.error(container.querySelector("audio")!);
    await waitFor(() => {
      expect(screen.getByText(/Reconnecting/)).toBeInTheDocument();
    });
    await act(async () => {
      vi.advanceTimersByTime(500);
    });
    expect(screen.getByText(/Reconnecting/)).toBeInTheDocument();
    expect(screen.queryByText(/^Error$/)).not.toBeInTheDocument();
    expect(vi.mocked(window.HTMLAudioElement.prototype.load).mock.calls.length).toBe(
      loadCalls,
    );
  });

  it("sets Error when reconnect fetch rejects", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/stream/reconnect")) {
        return Promise.reject(new Error("network"));
      }
      if (url.includes("/stream/session.json")) {
        return {
          ok: true,
          json: async () => ({
            state: "playing",
            current_track: {
              title: "Fail",
              artist: "A",
              url: "http://localhost/f.wav",
              genre: "x",
            },
            prefetch_tracks: [],
            buffer_seconds: 1,
            reconnect: { attempts: 0, max_attempts: 3 },
            error: null,
          }),
        } as Response;
      }
      return { ok: true, json: async () => ([]) } as Response;
    });

    const { container } = render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("Fail")).toBeInTheDocument());
    fireEvent.error(container.querySelector("audio")!);
    await waitFor(() => {
      expect(screen.getByText(/Error/)).toBeInTheDocument();
    });
  });

  it("POSTs /stream/reconnect on audio error", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/stream/reconnect")) {
        return {
          ok: true,
          json: async () => ({ recovered: true }),
        } as Response;
      }
      if (url.includes("/stream/session.json")) {
        return {
          ok: true,
          json: async () => ({
            state: "playing",
            current_track: {
              title: "Post",
              artist: "A",
              url: "http://localhost/p.wav",
              genre: "x",
            },
            prefetch_tracks: [],
            buffer_seconds: 1,
            reconnect: { attempts: 0, max_attempts: 3 },
            error: null,
          }),
        } as Response;
      }
      return { ok: true, json: async () => ([]) } as Response;
    });

    const { container } = render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("Post")).toBeInTheDocument());
    fireEvent.error(container.querySelector("audio")!);
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        "http://localhost:8000/stream/reconnect",
        expect.objectContaining({ method: "POST" }),
      );
    });
  });

  it("builds playlist from prefetch_tracks only", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/stream/session.json")) {
        return {
          ok: true,
          json: async () => ({
            state: "stopped",
            current_track: null,
            prefetch_tracks: [
              {
                title: "OnlyPrefetch",
                artist: "P",
                url: "http://localhost/only.wav",
                genre: "ambient",
              },
            ],
            buffer_seconds: 2,
            reconnect: { attempts: 0, max_attempts: 3 },
            error: null,
          }),
        } as Response;
      }
      return { ok: true, json: async () => ([]) } as Response;
    });

    render(<AudioPlayer />);
    await waitFor(() => {
      expect(screen.getByText("OnlyPrefetch")).toBeInTheDocument();
    });
    expect(screen.queryByText("Connecting to Quantum Stream...")).not.toBeInTheDocument();
  });

  it("sets audio src from current track url", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/stream/session.json")) {
        return {
          ok: true,
          json: async () => ({
            state: "playing",
            current_track: {
              title: "Src",
              artist: "A",
              url: "http://localhost/src.wav",
              genre: "g",
            },
            prefetch_tracks: [],
            buffer_seconds: 1,
            reconnect: { attempts: 0, max_attempts: 3 },
            error: null,
          }),
        } as Response;
      }
      return { ok: true, json: async () => ([]) } as Response;
    });

    const { container } = render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("Src")).toBeInTheDocument());
    expect(container.querySelector("audio")?.getAttribute("src")).toBe(
      "http://localhost/src.wav",
    );
  });

  it("formats 0:00 when duration is missing", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/stream/session.json")) {
        return {
          ok: true,
          json: async () => ({
            state: "playing",
            current_track: {
              title: "NaNDur",
              artist: "A",
              url: "http://localhost/n.wav",
              genre: "g",
            },
            prefetch_tracks: [],
            buffer_seconds: 1,
            reconnect: { attempts: 0, max_attempts: 3 },
            error: null,
          }),
        } as Response;
      }
      return { ok: true, json: async () => ([]) } as Response;
    });

    const { container } = render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("NaNDur")).toBeInTheDocument());
    const audio = container.querySelector("audio") as HTMLAudioElement;
    Object.defineProperty(audio, "currentTime", { configurable: true, value: 0 });
    Object.defineProperty(audio, "duration", { configurable: true, value: NaN });
    fireEvent.timeUpdate(audio);
    await waitFor(() => {
      expect(screen.getAllByText("0:00").length).toBeGreaterThanOrEqual(1);
    });
  });

  it("stops ledger polling on unmount", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/ledger.json")) {
        return {
          ok: true,
          json: async () => ({ height: 1, status: "Ok" }),
        } as Response;
      }
      if (url.includes("/stream/session.json")) {
        return {
          ok: true,
          json: async () => ({
            state: "Offline",
            current_track: null,
            prefetch_tracks: [],
            buffer_seconds: 0,
            reconnect: { attempts: 0, max_attempts: 3 },
            error: null,
          }),
        } as Response;
      }
      return { ok: true, json: async () => ([]) } as Response;
    });

    const { unmount } = render(<AudioPlayer />);
    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    const callsBefore = vi.mocked(fetch).mock.calls.length;
    unmount();
    await act(async () => {
      vi.advanceTimersByTime(15000);
    });
    expect(vi.mocked(fetch).mock.calls.length).toBe(callsBefore);
  });

  it("renders three client-island dynamic stubs", async () => {
    render(<AudioPlayer />);
    expect(screen.getAllByTestId("dynamic-stub")).toHaveLength(3);
  });
});
