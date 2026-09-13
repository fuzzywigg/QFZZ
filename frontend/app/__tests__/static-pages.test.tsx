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
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
      "Contact the Hive",
    );
    expect(screen.getByRole("link", { name: "Return to Stream" })).toHaveAttribute(
      "href",
      "/",
    );
  });

  it("renders Guide interaction tips", () => {
    render(<GuidePage />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
      "Listener Guide",
    );
    expect(screen.getByText(/Request Track/)).toBeInTheDocument();
    expect(screen.getByText(/Hive Terminal/)).toBeInTheDocument();
    expect(screen.getByText(/Knowledge Graph/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Return to Stream" })).toHaveAttribute(
      "href",
      "/",
    );
  });

  it("renders Library placeholder", () => {
    render(<LibraryPage />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
      "Music Library",
    );
    expect(screen.getByText(/public domain frequencies/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Return to Stream" })).toHaveAttribute(
      "href",
      "/",
    );
  });
});
