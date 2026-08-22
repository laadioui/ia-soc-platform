import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI SOC Platform - Security Operations Center",
  description: "AI-powered Security Operations Center for threat detection and incident response",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>{children}</body>
    </html>
  );
}
