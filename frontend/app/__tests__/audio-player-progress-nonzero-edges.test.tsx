import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";

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

describe("AudioPlayer nonzero progress edges", () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    mockAudioElement();
    vi.stubGlobal(
      "Audio",
      vi.fn().mockImplementation(() => ({
        preload: "",
        src: "",
      })),
    );
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/stream/session.json")) {
          return {
            ok: true,
            json: async () => ({
              state: "playing",
              current_track: {
                title: "ProgressTrack",
                artist: "Viz",
                url: "http://localhost/p.wav",
                genre: "Ambient",
              },
              prefetch_tracks: [],
              buffer_seconds: 2,
              reconnect: { attempts: 0, max_attempts: 3 },
              error: null,
            }),
          } as Response;
        }
        return { ok: true, json: async () => [] } as Response;
      }),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("renders percent width and padded time labels", async () => {
    const { container } = render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("ProgressTrack")).toBeInTheDocument());

    const audio = container.querySelector("audio") as HTMLAudioElement;
    Object.defineProperty(audio, "currentTime", { configurable: true, value: 50 });
    Object.defineProperty(audio, "duration", { configurable: true, value: 200 });
    fireEvent.timeUpdate(audio);

    const bar = container.querySelector(".h-full.bg-gradient-to-r") as HTMLElement;
    expect(bar.style.width).toBe("25%");
    expect(screen.getByText("0:50")).toBeInTheDocument();
    expect(screen.getByText("3:20")).toBeInTheDocument();
  });

  it("pads single-digit seconds", async () => {
    const { container } = render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("ProgressTrack")).toBeInTheDocument());

    const audio = container.querySelector("audio") as HTMLAudioElement;
    Object.defineProperty(audio, "currentTime", { configurable: true, value: 5 });
    Object.defineProperty(audio, "duration", { configurable: true, value: 9 });
    fireEvent.timeUpdate(audio);

    expect(screen.getByText("0:05")).toBeInTheDocument();
    expect(screen.getByText("0:09")).toBeInTheDocument();
  });

  it("explicit zero duration uses safe divisor for bar width", async () => {
    const { container } = render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("ProgressTrack")).toBeInTheDocument());

    const audio = container.querySelector("audio") as HTMLAudioElement;
    Object.defineProperty(audio, "currentTime", { configurable: true, value: 30 });
    Object.defineProperty(audio, "duration", { configurable: true, value: 0 });
    fireEvent.timeUpdate(audio);

    const bar = container.querySelector(".h-full.bg-gradient-to-r") as HTMLElement;
    // (30 / (0 || 1)) * 100
    expect(bar.style.width).toBe("3000%");
  });
});
