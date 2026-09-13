import { describe, it, expect, vi } from "vitest";

vi.mock("next/font/google", () => ({
  Geist: () => ({ variable: "--font-geist-sans" }),
  Geist_Mono: () => ({ variable: "--font-geist-mono" }),
}));

describe("root layout metadata", () => {
  it("exports QFZZ branding instead of Next.js scaffold defaults", async () => {
    const layout = await import("@/app/layout");
    expect(layout.metadata.title).toBe("QFZZ Prime");
    expect(String(layout.metadata.description)).toMatch(/Hive Mind/i);
    expect(String(layout.metadata.title)).not.toMatch(/Create Next App/i);
  });
});
