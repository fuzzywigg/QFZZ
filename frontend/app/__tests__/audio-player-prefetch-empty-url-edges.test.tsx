// AudioPlayer skips prefetch Audio() when track urls are empty.

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";

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

describe("AudioPlayer prefetch empty-url edges", () => {
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
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("does not construct Audio for prefetch tracks with empty urls", async () => {
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
                title: "EmptyPrefetch",
                artist: "Edge",
                url: "http://localhost/now.wav",
                genre: "test",
              },
              prefetch_tracks: [
                { title: "A", artist: "x", url: "", genre: "g" },
                { title: "B", artist: "y", url: "", genre: "g" },
              ],
              buffer_seconds: 2,
              reconnect: { attempts: 0, max_attempts: 3 },
              error: null,
            }),
          } as Response;
        }
        if (url.includes("/playlist.json")) {
          return { ok: true, json: async () => [] } as Response;
        }
        return { ok: true, json: async () => ({}) } as Response;
      }),
    );

    render(<AudioPlayer />);
    await waitFor(() => {
      expect(screen.getByText("EmptyPrefetch")).toBeInTheDocument();
    });
    expect(Audio).not.toHaveBeenCalled();
  });
});
