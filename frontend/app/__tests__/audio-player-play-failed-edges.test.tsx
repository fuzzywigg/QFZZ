import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, act } from "@testing-library/react";
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

describe("AudioPlayer Play failed edge", () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    mockAudioElement();
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
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

  it("logs Play failed when toggle play rejects", async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    const errSpy = vi.spyOn(console, "error").mockImplementation(() => {});
    vi.mocked(window.HTMLAudioElement.prototype.play).mockRejectedValue(
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
              title: "ToggleTrack",
              artist: "A",
              url: "http://localhost/t.wav",
              genre: "g",
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
    await waitFor(() => expect(screen.getByText("ToggleTrack")).toBeInTheDocument());

    await user.click(screen.getByTitle("Toggle Play/Pause"));
    await act(async () => {
      await Promise.resolve();
    });

    await waitFor(() => {
      expect(errSpy).toHaveBeenCalledWith("Play failed:", expect.any(Error));
    });
    errSpy.mockRestore();
  });
});
