// AudioPlayer empty track url omits audio src attribute.

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

describe("AudioPlayer empty url src edges", () => {
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

  it("renders audio without src when current track url is empty", async () => {
    vi.mocked(fetch).mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/stream/session.json")) {
        return {
          ok: true,
          json: async () => ({
            state: "playing",
            current_track: {
              title: "NoSrc",
              artist: "Ghost",
              url: "",
              genre: "void",
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
    await waitFor(() => expect(screen.getByText("NoSrc")).toBeInTheDocument());
    const audio = container.querySelector("audio");
    expect(audio).toBeTruthy();
    expect(audio?.getAttribute("src")).toBeNull();
  });
});
