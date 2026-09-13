import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
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
  vi.spyOn(audioProto, "play").mockRejectedValue(new Error("autoplay blocked"));
  vi.spyOn(audioProto, "pause").mockImplementation(() => undefined);
  vi.spyOn(audioProto, "load").mockImplementation(() => undefined);
}

describe("AudioPlayer play-next reject edges", () => {
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
                title: "FirstNext",
                artist: "A",
                url: "http://localhost/a.wav",
                genre: "x",
              },
              prefetch_tracks: [
                {
                  title: "SecondNext",
                  artist: "B",
                  url: "http://localhost/b.wav",
                  genre: "y",
                },
              ],
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

  it("logs Play next failed and still advances track chrome", async () => {
    const errSpy = vi.spyOn(console, "error").mockImplementation(() => undefined);
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    const { container } = render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("FirstNext")).toBeInTheDocument());

    await user.click(screen.getByTitle("Next Track"));
    await waitFor(() => expect(screen.getByText("SecondNext")).toBeInTheDocument());

    await waitFor(() => {
      expect(errSpy).toHaveBeenCalled();
      const joined = errSpy.mock.calls.map((c) => String(c[0])).join(" ");
      expect(joined).toMatch(/Play next failed/);
    });

    const pulse = container.querySelectorAll(
      ".w-1.h-3.bg-purple-500.animate-pulse, .w-1.h-5.bg-purple-500.animate-pulse, .w-1.h-2.bg-purple-500.animate-pulse, .w-1.h-4.bg-purple-500.animate-pulse",
    );
    expect(pulse.length).toBeGreaterThan(0);
  });
});
