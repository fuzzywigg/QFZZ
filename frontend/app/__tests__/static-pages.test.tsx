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

  it("About mentions Hive Mind and public domain", () => {
    render(<AboutPage />);
    expect(screen.getByText(/Hive/i)).toBeInTheDocument();
    expect(screen.getByText(/public domain/i)).toBeInTheDocument();
  });

  it("Contact points users to Hive Terminal", () => {
    render(<ContactPage />);
    expect(screen.getByText(/Hive Terminal/i)).toBeInTheDocument();
  });

  it("Guide welcomes Quantum Realm and names Queen Node", () => {
    render(<GuidePage />);
    expect(screen.getByText(/Quantum Realm/i)).toBeInTheDocument();
    expect(screen.getByText(/Queen Node/i)).toBeInTheDocument();
    expect(screen.getByText(/Semantic Knowledge Graph/i)).toBeInTheDocument();
  });

  it("Library mentions searchable catalog placeholder", () => {
    render(<LibraryPage />);
    expect(screen.getByText(/searchable catalog/i)).toBeInTheDocument();
  });
});
