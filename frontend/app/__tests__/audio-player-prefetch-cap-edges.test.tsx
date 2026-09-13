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

describe("AudioPlayer prefetch cap edges", () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    mockAudioElement();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("caps prefetch Audio construction at two tracks", async () => {
    const audioCtor = vi.fn().mockImplementation(() => ({
      preload: "",
      src: "",
    }));
    vi.stubGlobal("Audio", audioCtor);
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
                title: "Now",
                artist: "A",
                url: "http://localhost/now.wav",
                genre: "x",
              },
              prefetch_tracks: [
                { title: "P1", artist: "A", url: "http://localhost/p1.wav", genre: "x" },
                { title: "P2", artist: "A", url: "http://localhost/p2.wav", genre: "x" },
                { title: "P3", artist: "A", url: "http://localhost/p3.wav", genre: "x" },
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

    render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("Now")).toBeInTheDocument());
    await waitFor(() => expect(audioCtor).toHaveBeenCalledTimes(2));
    const instances = audioCtor.mock.results.map((r) => r.value);
    expect(instances[0].preload).toBe("auto");
    expect(instances[0].src).toBe("http://localhost/p1.wav");
    expect(instances[1].src).toBe("http://localhost/p2.wav");
  });

  it("skips empty prefetch urls and still caps at two", async () => {
    const audioCtor = vi.fn().mockImplementation(() => ({
      preload: "",
      src: "",
    }));
    vi.stubGlobal("Audio", audioCtor);
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
                title: "Now2",
                artist: "A",
                url: "http://localhost/now2.wav",
                genre: "x",
              },
              prefetch_tracks: [
                { title: "Empty", artist: "A", url: "", genre: "x" },
                { title: "Ok1", artist: "A", url: "http://localhost/ok1.wav", genre: "x" },
                { title: "Ok2", artist: "A", url: "http://localhost/ok2.wav", genre: "x" },
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

    render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("Now2")).toBeInTheDocument());
    // slice(0,2) includes empty + ok1 → only ok1 constructs Audio
    expect(audioCtor).toHaveBeenCalledTimes(1);
    expect(audioCtor.mock.results[0].value.src).toBe("http://localhost/ok1.wav");
  });
});
