import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import HiveTerminal from "@/components/HiveTerminal";

describe("HiveTerminal", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new Error("offline")),
    );
    Element.prototype.scrollIntoView = vi.fn();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  it("renders hive header and initial system messages", () => {
    render(<HiveTerminal />);
    expect(screen.getByText(/HiveOS v2.0/)).toBeInTheDocument();
    expect(screen.getByText("CONNECTING TO HIVE NET...")).toBeInTheDocument();
    expect(screen.getByText("QUEEN NODE: ONLINE")).toBeInTheDocument();
    expect(
      screen.getByText(/Greetings, Drone. The Hive is listening/),
    ).toBeInTheDocument();
  });

  it("appends user message and AI reply after send", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    render(<HiveTerminal />);

    await user.type(screen.getByPlaceholderText("Transmit to Hive..."), "ping");
    await user.click(screen.getByRole("button", { name: "Send Message" }));

    expect(screen.getByText("ping")).toBeInTheDocument();

    await act(async () => {
      vi.advanceTimersByTime(1100);
    });

    expect(
      screen.getByText(
        /Processing signal|The Queen acknowledges|Frequency aligned|Pattern recognized/,
      ),
    ).toBeInTheDocument();
  });

  it("ignores empty transmits", async () => {
    const user = userEvent.setup();
    render(<HiveTerminal />);
    const before = screen.getAllByText(/CONNECTING TO HIVE NET|QUEEN NODE|Greetings/).length;
    await user.click(screen.getByRole("button", { name: "Send Message" }));
    const after = screen.getAllByText(/CONNECTING TO HIVE NET|QUEEN NODE|Greetings/).length;
    expect(after).toBe(before);
  });

  it("ignores whitespace-only transmits", async () => {
    const user = userEvent.setup();
    render(<HiveTerminal />);
    await user.type(screen.getByPlaceholderText("Transmit to Hive..."), "   ");
    await user.click(screen.getByRole("button", { name: "Send Message" }));
    expect(screen.queryByText("   ")).not.toBeInTheDocument();
  });

  it("injects DJ poll messages and dedupes identical ones", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({ message: "Queen broadcast" }),
    } as Response);

    render(<HiveTerminal />);
    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    expect(screen.getAllByText("Queen broadcast")).toHaveLength(1);

    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    expect(screen.getAllByText("Queen broadcast")).toHaveLength(1);
  });

  it("survives junk poll payloads", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({}),
    } as Response);
    render(<HiveTerminal />);
    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    expect(screen.getByText("QUEEN NODE: ONLINE")).toBeInTheDocument();
  });

  it("ignores falsy DJ poll message", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({ message: "" }),
    } as Response);
    render(<HiveTerminal />);
    const before = screen.getAllByText(/CONNECTING TO HIVE NET|QUEEN NODE|Greetings/).length;
    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    const after = screen.getAllByText(/CONNECTING TO HIVE NET|QUEEN NODE|Greetings/).length;
    expect(after).toBe(before);
    expect(screen.getByText("QUEEN NODE: ONLINE")).toBeInTheDocument();
  });

  it("survives poll rejection and clears input after send", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    vi.mocked(fetch).mockRejectedValue(new Error("poll fail"));
    render(<HiveTerminal />);
    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    expect(screen.getByText("QUEEN NODE: ONLINE")).toBeInTheDocument();

    const input = screen.getByPlaceholderText("Transmit to Hive...") as HTMLInputElement;
    await user.type(input, "hello hive");
    await user.click(screen.getByRole("button", { name: "Send Message" }));
    expect(input.value).toBe("");
    expect(screen.getByText("hello hive")).toBeInTheDocument();
    expect(screen.getByText("USER")).toBeInTheDocument();
  });

  it("pins AI reply via Math.random and stops polling on unmount", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    vi.spyOn(Math, "random").mockReturnValue(0);
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({ message: "later" }),
    } as Response);

    const { unmount } = render(<HiveTerminal />);
    await user.type(screen.getByPlaceholderText("Transmit to Hive..."), "ping");
    await user.click(screen.getByRole("button", { name: "Send Message" }));
    await act(async () => {
      vi.advanceTimersByTime(1100);
    });
    expect(screen.getByText("Processing signal...")).toBeInTheDocument();
    expect(Element.prototype.scrollIntoView).toHaveBeenCalled();

    const callsBefore = vi.mocked(fetch).mock.calls.length;
    unmount();
    await act(async () => {
      vi.advanceTimersByTime(15000);
    });
    expect(vi.mocked(fetch).mock.calls.length).toBe(callsBefore);
  });

  it("transmits on Enter key", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    render(<HiveTerminal />);
    await user.type(
      screen.getByPlaceholderText("Transmit to Hive..."),
      "enter-msg{Enter}",
    );
    expect(screen.getByText("enter-msg")).toBeInTheDocument();
  });

  it("appends distinct successive DJ poll messages", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.mocked(fetch)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: "msg-a" }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: "msg-b" }),
      } as Response);

    render(<HiveTerminal />);
    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    expect(screen.getByText("msg-a")).toBeInTheDocument();
    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    expect(screen.getByText("msg-b")).toBeInTheDocument();
  });

  it("dedupes only against last bubble so USER in between allows repeat AI", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({ message: "repeat-me" }),
    } as Response);

    render(<HiveTerminal />);
    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    expect(screen.getAllByText("repeat-me")).toHaveLength(1);

    await user.type(screen.getByPlaceholderText("Transmit to Hive..."), "break{Enter}");
    expect(screen.getByText("break")).toBeInTheDocument();

    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    expect(screen.getAllByText("repeat-me").length).toBeGreaterThanOrEqual(2);
  });

  it("survives poll json() rejection", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => {
        throw new Error("bad json");
      },
    } as Response);
    render(<HiveTerminal />);
    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    expect(screen.getByText("QUEEN NODE: ONLINE")).toBeInTheDocument();
  });

  it("rapid double-send yields two USER and two AI replies", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    vi.spyOn(Math, "random").mockReturnValue(0.25);
    render(<HiveTerminal />);

    await user.type(screen.getByPlaceholderText("Transmit to Hive..."), "one{Enter}");
    await user.type(screen.getByPlaceholderText("Transmit to Hive..."), "two{Enter}");
    expect(screen.getByText("one")).toBeInTheDocument();
    expect(screen.getByText("two")).toBeInTheDocument();

    await act(async () => {
      vi.advanceTimersByTime(1100);
    });
    await act(async () => {
      vi.advanceTimersByTime(1100);
    });
    expect(screen.getAllByText("The Queen acknowledges your input.")).toHaveLength(2);
  });

  it.each([
    [0.0, "Processing signal..."],
    [0.25, "The Queen acknowledges your input."],
    [0.5, "Frequency aligned. Scanning..."],
    [0.75, "Pattern recognized."],
  ] as const)("Math.random %s maps to canned reply %#", async (rand, reply) => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    vi.spyOn(Math, "random").mockReturnValue(rand);
    render(<HiveTerminal />);

    await user.type(screen.getByPlaceholderText("Transmit to Hive..."), `msg-${rand}`);
    await user.click(screen.getByRole("button", { name: "Send Message" }));
    await act(async () => {
      vi.advanceTimersByTime(1100);
    });
    expect(screen.getByText(reply)).toBeInTheDocument();
    expect(screen.getAllByText("QUEEN").length).toBeGreaterThanOrEqual(2);
  });

  it("labels SYSTEM bubbles with SYSTEM sender text", () => {
    render(<HiveTerminal />);
    expect(screen.getAllByText("SYSTEM").length).toBeGreaterThanOrEqual(1);
  });

  it("ignores null DJ poll JSON body", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => null,
    } as Response);
    render(<HiveTerminal />);
    const before = screen.getAllByText(/CONNECTING TO HIVE NET|QUEEN NODE|Greetings/).length;
    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    const after = screen.getAllByText(/CONNECTING TO HIVE NET|QUEEN NODE|Greetings/).length;
    expect(after).toBe(before);
    expect(screen.getByText("QUEEN NODE: ONLINE")).toBeInTheDocument();
  });
});
