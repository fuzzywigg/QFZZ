import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
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

describe("AudioPlayer progress / chrome edges", () => {
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
              state: "stopped",
              current_track: {
                title: "ChromeTrack",
                artist: "Viz",
                url: "http://localhost/c.wav",
                genre: "",
              },
              prefetch_tracks: [
                {
                  title: "NextChrome",
                  artist: "Viz",
                  url: "http://localhost/n.wav",
                  genre: "x",
                },
              ],
              buffer_seconds: 2,
              reconnect: { attempts: 0, max_attempts: 3 },
              error: null,
            }),
          } as Response;
        }
        return { ok: true, json: async () => ([]) } as Response;
      }),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("zero duration progress uses safe divisor and empty genre shows Unknown", async () => {
    const { container } = render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("ChromeTrack")).toBeInTheDocument());
    expect(screen.getByText("Unknown")).toBeInTheDocument();

    const audio = container.querySelector("audio") as HTMLAudioElement;
    Object.defineProperty(audio, "currentTime", { configurable: true, value: 0 });
    Object.defineProperty(audio, "duration", {
      configurable: true,
      get: () => Number.NaN,
    });
    fireEvent.timeUpdate(audio);

    const bar = container.querySelector(
      ".h-full.bg-gradient-to-r",
    ) as HTMLElement;
    expect(bar).toBeTruthy();
    // duration NaN → setDuration(0) → width uses (currentTime / (0 || 1)) * 100
    expect(bar.style.width).toBe("0%");
  });

  it("menu shows version chrome and play toggles pulse classes", async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    const { container } = render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("ChromeTrack")).toBeInTheDocument());

    const headerButtons = screen
      .getAllByRole("button")
      .filter((b) => !b.getAttribute("title"));
    await user.click(headerButtons[0]);
    expect(
      screen.getByText("v0.9.2 Beta // Quantum Stream"),
    ).toBeInTheDocument();

    const barsBefore = container.querySelectorAll(".animate-pulse");
    const countBefore = barsBefore.length;

    await user.click(screen.getByTitle("Toggle Play/Pause"));
    const barsAfter = container.querySelectorAll(
      ".w-1.h-3.bg-purple-500.animate-pulse, .w-1.h-5.bg-purple-500.animate-pulse, .w-1.h-2.bg-purple-500.animate-pulse, .w-1.h-4.bg-purple-500.animate-pulse",
    );
    expect(barsAfter.length).toBeGreaterThan(0);
    expect(container.querySelectorAll(".animate-pulse").length).toBeGreaterThanOrEqual(
      countBefore,
    );
  });

  it("volume slider writes to audio element volume", async () => {
    const { container } = render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("ChromeTrack")).toBeInTheDocument());

    const audio = container.querySelector("audio") as HTMLAudioElement;
    const slider = container.querySelector('input[type="range"]') as HTMLInputElement;
    expect(slider).toBeTruthy();
    fireEvent.change(slider, { target: { value: "0.4" } });
    expect(audio.volume).toBeCloseTo(0.4, 5);
  });
});
