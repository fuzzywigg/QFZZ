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

  it("reconnects successfully when recovered is true", async () => {
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
              genre: "jazz",
            },
            prefetch_tracks: [],
            buffer_seconds: 1,
            reconnect: { attempts: 0, max_attempts: 3 },
            error: null,
          }),
        } as Response;
      }
      return { ok: true, json: async () => [] } as Response;
    });

    const { container } = render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("Live")).toBeInTheDocument());
    expect(screen.getByText("jazz")).toBeInTheDocument();
    const audio = container.querySelector("audio");
    fireEvent.error(audio!);
    await waitFor(() => expect(screen.getByText(/Reconnecting/)).toBeInTheDocument());
    await act(async () => {
      vi.advanceTimersByTime(500);
    });
    await waitFor(() => expect(screen.getByText(/Playing/)).toBeInTheDocument());
    expect(window.HTMLAudioElement.prototype.load).toHaveBeenCalled();
  });

  it("stays Reconnecting when recovered is false", async () => {
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
            reconnect: { attempts: 1, max_attempts: 3 },
            error: null,
          }),
        } as Response;
      }
      return { ok: true, json: async () => [] } as Response;
    });

    const { container } = render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("Stuck")).toBeInTheDocument());
    fireEvent.error(container.querySelector("audio")!);
    await waitFor(() => expect(screen.getByText(/Reconnecting/)).toBeInTheDocument());
    await act(async () => {
      vi.advanceTimersByTime(500);
    });
    expect(screen.getByText(/Reconnecting/)).toBeInTheDocument();
  });

  it("sets Error when reconnect fetch rejects", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/stream/reconnect")) {
        throw new Error("network");
      }
      if (url.includes("/stream/session.json")) {
        return {
          ok: true,
          json: async () => ({
            state: "playing",
            current_track: {
              title: "Drop",
              artist: "A",
              url: "http://localhost/d.wav",
              genre: "x",
            },
            prefetch_tracks: [],
            buffer_seconds: 1,
            reconnect: { attempts: 0, max_attempts: 3 },
            error: null,
          }),
        } as Response;
      }
      return { ok: true, json: async () => [] } as Response;
    });

    const { container } = render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("Drop")).toBeInTheDocument());
    fireEvent.error(container.querySelector("audio")!);
    await waitFor(() => expect(screen.getByText(/Error/)).toBeInTheDocument());
  });

  it("uses playlist.json array when session is empty", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
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
      if (url.includes("/playlist.json")) {
        return {
          ok: true,
          json: async () => [
            {
              title: "FromPlaylist",
              artist: "Lib",
              url: "http://localhost/p.wav",
              genre: "ambient",
            },
          ],
        } as Response;
      }
      return { ok: true, json: async () => ({}) } as Response;
    });

    render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("FromPlaylist")).toBeInTheDocument());
    expect(screen.getByText("Lib")).toBeInTheDocument();
  });

  it("pauses after play and advances on ended / timeupdate", async () => {
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
      return { ok: true, json: async () => [] } as Response;
    });

    const { container } = render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("One")).toBeInTheDocument());

    await user.click(screen.getByTitle("Toggle Play/Pause"));
    expect(window.HTMLAudioElement.prototype.play).toHaveBeenCalled();
    await user.click(screen.getByTitle("Toggle Play/Pause"));
    expect(window.HTMLAudioElement.prototype.pause).toHaveBeenCalled();

    const audio = container.querySelector("audio")!;
    Object.defineProperty(audio, "currentTime", { value: 65, configurable: true });
    Object.defineProperty(audio, "duration", { value: 125, configurable: true });
    fireEvent.timeUpdate(audio);
    await waitFor(() => {
      expect(screen.getByText("1:05")).toBeInTheDocument();
      expect(screen.getByText("2:05")).toBeInTheDocument();
    });

    fireEvent.ended(audio);
    await waitFor(() => expect(screen.getByText("Two")).toBeInTheDocument());
  });

  it("toggles menu closed after open", async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    render(<AudioPlayer />);
    const headerButtons = screen
      .getAllByRole("button")
      .filter((b) => !b.getAttribute("title"));
    await user.click(headerButtons[0]);
    expect(screen.getByRole("link", { name: "Music Library" })).toBeInTheDocument();
    await user.click(headerButtons[0]);
    expect(screen.queryByRole("link", { name: "Music Library" })).not.toBeInTheDocument();
  });

  it("does not prefetch Audio when prefetch_tracks empty", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/stream/session.json")) {
        return {
          ok: true,
          json: async () => ({
            state: "playing",
            current_track: {
              title: "Solo",
              artist: "A",
              url: "http://localhost/solo.wav",
              genre: "x",
            },
            prefetch_tracks: [],
            buffer_seconds: 2,
            reconnect: { attempts: 0, max_attempts: 3 },
            error: null,
          }),
        } as Response;
      }
      return { ok: true, json: async () => [] } as Response;
    });
    render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("Solo")).toBeInTheDocument());
    expect(Audio).not.toHaveBeenCalled();
  });
});
