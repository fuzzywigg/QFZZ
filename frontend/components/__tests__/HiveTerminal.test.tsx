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

  it("polls dj_message.json and injects AI chatter", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({ message: "Queen pulse detected" }),
    } as Response);

    render(<HiveTerminal />);

    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    await act(async () => {
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(screen.getByText("Queen pulse detected")).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith(
      expect.stringMatching(/\/dj_message\.json$/),
    );
  });

  it("dedupes poll when last AI message matches", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({
        message:
          "Greetings, Drone. The Hive is listening. What is your frequency?",
      }),
    } as Response);

    render(<HiveTerminal />);

    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    await act(async () => {
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(
      screen.getAllByText(
        "Greetings, Drone. The Hive is listening. What is your frequency?",
      ),
    ).toHaveLength(1);
  });
});
