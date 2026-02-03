import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import DeviceImage from "./DeviceImage";

describe("DeviceImage Component", () => {
  it("should render device image with correct src", () => {
    render(<DeviceImage deviceType="SoundTouch 10" />);
    const img = screen.getByRole("img");
    expect(img).toHaveAttribute("src", "/images/devices/st10.svg");
  });

  it("should render device image with default fallback for unknown model", () => {
    render(<DeviceImage deviceType="Unknown Model" />);
    const img = screen.getByRole("img");
    expect(img).toHaveAttribute("src", "/images/devices/default.svg");
  });

  it("should show device label when showLabel is true", () => {
    render(<DeviceImage deviceType="SoundTouch 20" showLabel={true} />);
    expect(screen.getByText("SoundTouch 20")).toBeInTheDocument();
  });

  it("should NOT show device label when showLabel is false", () => {
    render(<DeviceImage deviceType="SoundTouch 30" showLabel={false} />);
    expect(screen.queryByText("SoundTouch 30")).not.toBeInTheDocument();
  });

  it("should apply custom alt text", () => {
    render(<DeviceImage deviceType="ST10" alt="My Speaker" />);
    const img = screen.getByRole("img");
    expect(img).toHaveAttribute("alt", "My Speaker");
  });

  it("should apply size classes correctly", () => {
    const { container } = render(
      <DeviceImage deviceType="ST20" size="large" />,
    );
    const imageContainer = container.querySelector(
      ".device-image-container > div",
    );
    expect(imageContainer).toHaveClass("w-48", "h-48");
  });

  it("should apply custom className", () => {
    const { container } = render(
      <DeviceImage deviceType="ST30" className="custom-class" />,
    );
    const imageContainer = container.querySelector(".device-image-container");
    expect(imageContainer).toHaveClass("custom-class");
  });

  it("should use lazy loading", () => {
    render(<DeviceImage deviceType="ST300" />);
    const img = screen.getByRole("img");
    expect(img).toHaveAttribute("loading", "lazy");
  });
});
