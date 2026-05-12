import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Spontaneous Chat Assistant",
  description: "A witty, adaptive AI chat app with streaming responses.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
