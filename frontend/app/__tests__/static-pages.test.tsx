import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import AboutPage from "@/app/about/page";
import ContactPage from "@/app/contact/page";
import GuidePage from "@/app/guide/page";
import LibraryPage from "@/app/library/page";

describe("static marketing pages", () => {
  it("renders About with return link", () => {
    render(<AboutPage />);
    expect(screen.getByText("About QFZZ")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Return to Stream" })).toHaveAttribute(
      "href",
      "/",
    );
  });

  it("renders Contact", () => {
    render(<ContactPage />);
    expect(screen.getByText("Contact the Hive")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Return to Stream" })).toBeInTheDocument();
  });

  it("renders Guide interaction tips", () => {
    render(<GuidePage />);
    expect(screen.getByText("Listener Guide")).toBeInTheDocument();
    expect(screen.getByText(/Request Track/)).toBeInTheDocument();
    expect(screen.getByText(/Hive Terminal/)).toBeInTheDocument();
  });

  it("renders Library placeholder", () => {
    render(<LibraryPage />);
    expect(screen.getByText("Music Library")).toBeInTheDocument();
    expect(screen.getByText(/public domain frequencies/i)).toBeInTheDocument();
  });
});
