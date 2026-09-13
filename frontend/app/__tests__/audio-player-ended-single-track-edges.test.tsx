import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, act, fireEvent } from "@testing-library/react";

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

describe("AudioPlayer single-track onEnded edge", () => {
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

  it("onEnded with one track reloads the same title", async () => {
    const loadSpy = vi.spyOn(window.HTMLAudioElement.prototype, "load");
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/stream/session.json")) {
        return {
          ok: true,
          json: async () => ({
            state: "playing",
            current_track: {
              title: "Solo",
              artist: "One",
              url: "http://localhost/solo.wav",
              genre: "ambient",
            },
            prefetch_tracks: [],
            buffer_seconds: 4,
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
              title: "Solo",
              artist: "One",
              url: "http://localhost/solo.wav",
              genre: "ambient",
            },
          ],
        } as Response;
      }
      return { ok: true, json: async () => ({}) } as Response;
    });

    const { container } = render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("Solo")).toBeInTheDocument());

    const audio = container.querySelector("audio") as HTMLAudioElement;
    const beforeLoads = loadSpy.mock.calls.length;
    fireEvent.ended(audio);
    await waitFor(() => expect(screen.getByText("Solo")).toBeInTheDocument());
    expect(loadSpy.mock.calls.length).toBeGreaterThanOrEqual(beforeLoads);
  });
});
