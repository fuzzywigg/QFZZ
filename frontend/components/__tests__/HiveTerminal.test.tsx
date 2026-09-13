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

  it("appends successive different DJ messages", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    let n = 0;
    vi.mocked(fetch).mockImplementation(async () => {
      n += 1;
      return {
        ok: true,
        json: async () => ({ message: n === 1 ? "First pulse" : "Second pulse" }),
      } as Response;
    });
    render(<HiveTerminal />);
    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    expect(screen.getByText("First pulse")).toBeInTheDocument();
    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    expect(screen.getByText("Second pulse")).toBeInTheDocument();
  });

  it("appends AI text that matches last USER message", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({ message: "echo me" }),
    } as Response);

    render(<HiveTerminal />);
    await user.type(screen.getByPlaceholderText("Transmit to Hive..."), "echo me");
    await user.click(screen.getByRole("button", { name: "Send Message" }));
    expect(screen.getByText("echo me")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Transmit to Hive...")).toHaveValue("");
    expect(Element.prototype.scrollIntoView).toHaveBeenCalled();

    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    // Last message is USER "echo me"; poll AI with same text still appends
    expect(screen.getAllByText("echo me").length).toBeGreaterThanOrEqual(2);
  });

  it("ignores empty and null poll messages", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    let step = 0;
    vi.mocked(fetch).mockImplementation(async () => {
      step += 1;
      return {
        ok: true,
        json: async () =>
          step === 1 ? { message: "" } : { message: null },
      } as Response;
    });
    render(<HiveTerminal />);
    const before = screen.getAllByText(/QUEEN|SYSTEM|Greetings|CONNECTING/).length;
    await act(async () => {
      vi.advanceTimersByTime(10000);
    });
    const after = screen.getAllByText(/QUEEN|SYSTEM|Greetings|CONNECTING/).length;
    expect(after).toBe(before);
  });

  it("survives poll fetch rejection", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.mocked(fetch).mockRejectedValue(new Error("offline"));
    render(<HiveTerminal />);
    await act(async () => {
      vi.advanceTimersByTime(5000);
    });
    expect(screen.getByText("QUEEN NODE: ONLINE")).toBeInTheDocument();
  });

  it("labels AI as QUEEN and USER as USER", async () => {
    const user = userEvent.setup();
    render(<HiveTerminal />);
    expect(screen.getByText("QUEEN")).toBeInTheDocument();
    expect(screen.getAllByText("SYSTEM").length).toBeGreaterThanOrEqual(1);
    await user.type(screen.getByPlaceholderText("Transmit to Hive..."), "hi");
    await user.click(screen.getByRole("button", { name: "Send Message" }));
    expect(screen.getByText("USER")).toBeInTheDocument();
  });
});
