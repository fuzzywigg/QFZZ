import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, act } from "@testing-library/react";

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

describe("AudioPlayer session merge edges", () => {
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

  it("loads current_track only without prefetch Audio calls", async () => {
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
                title: "SoloPulse",
                artist: "One",
                url: "http://localhost/solo.wav",
                genre: "drone",
              },
              prefetch_tracks: [],
              buffer_seconds: 4,
              reconnect: { attempts: 0, max_attempts: 3 },
              error: null,
            }),
          } as Response;
        }
        if (url.includes("/playlist.json")) {
          return { ok: true, json: async () => ({ not: "array" }) } as Response;
        }
        return { ok: true, json: async () => ({}) } as Response;
      }),
    );

    render(<AudioPlayer />);
    await waitFor(() => {
      expect(screen.getByText("SoloPulse")).toBeInTheDocument();
    });
    expect(screen.getByText("drone")).toBeInTheDocument();
    expect(screen.getByText(/Buffer 4s/)).toBeInTheDocument();
    // empty prefetch_tracks → no Audio() prefetch constructor calls
    expect(Audio).not.toHaveBeenCalled();
  });

  it("ignores non-array playlist.json and later session poll overwrites", async () => {
    let poll = 0;
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/playlist.json")) {
          return {
            ok: true,
            json: async () => ({ tracks: "not-an-array" }),
          } as Response;
        }
        if (url.includes("/stream/session.json")) {
          poll += 1;
          if (poll === 1) {
            return {
              ok: true,
              json: async () => ({
                state: "playing",
                current_track: {
                  title: "FirstPoll",
                  artist: "A",
                  url: "http://localhost/1.wav",
                  genre: "g",
                },
                prefetch_tracks: [],
                buffer_seconds: 1,
                reconnect: { attempts: 0, max_attempts: 3 },
                error: null,
              }),
            } as Response;
          }
          return {
            ok: true,
            json: async () => ({
              state: "playing",
              current_track: {
                title: "SecondPoll",
                artist: "B",
                url: "http://localhost/2.wav",
                genre: "g",
              },
              prefetch_tracks: [],
              buffer_seconds: 9,
              reconnect: { attempts: 0, max_attempts: 3 },
              error: null,
            }),
          } as Response;
        }
        return { ok: true, json: async () => ({}) } as Response;
      }),
    );

    render(<AudioPlayer />);
    await waitFor(() => {
      expect(screen.getByText("FirstPoll")).toBeInTheDocument();
    });

    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    await waitFor(() => {
      expect(screen.getByText("SecondPoll")).toBeInTheDocument();
    });
    expect(screen.getByText(/Buffer 9s/)).toBeInTheDocument();
  });
});
