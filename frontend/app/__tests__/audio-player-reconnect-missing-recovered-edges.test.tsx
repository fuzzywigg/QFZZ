// AudioPlayer reconnect body missing recovered key stays Reconnecting.

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

describe("AudioPlayer reconnect missing recovered edges", () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    mockAudioElement();
    vi.stubGlobal("fetch", vi.fn());
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

  it("leaves Reconnecting when reconnect JSON omits recovered", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/stream/reconnect") && init?.method === "POST") {
        return {
          ok: true,
          json: async () => ({}),
        } as Response;
      }
      if (url.includes("/stream/session.json")) {
        return {
          ok: true,
          json: async () => ({
            state: "playing",
            current_track: {
              title: "Pulse",
              artist: "Qubit",
              url: "http://localhost/a.wav",
              genre: "x",
            },
            prefetch_tracks: [],
            buffer_seconds: 3,
            reconnect: { attempts: 0, max_attempts: 3 },
            error: null,
          }),
        } as Response;
      }
      return { ok: true, json: async () => ([]) } as Response;
    });

    const { container } = render(<AudioPlayer />);
    await waitFor(() => expect(screen.getByText("Pulse")).toBeInTheDocument());

    const audio = container.querySelector("audio");
    expect(audio).toBeTruthy();
    await act(async () => {
      fireEvent.error(audio!);
    });

    await waitFor(() => {
      expect(screen.getByText(/Reconnecting/)).toBeInTheDocument();
    });
  });
});
