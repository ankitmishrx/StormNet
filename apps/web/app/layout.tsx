import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "STORMNET — AI-Powered Convective Nowcasting Platform (SIH26084)",
  description:
    "Research prototype convective scale nowcasting platform for thunderstorms, hail, and cloudbursts (0–6 hr lead time). Designed for SIH Problem Statement SIH26084.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-surface-canvas selection:bg-brand-100 selection:text-brand-900">
        {children}
      </body>
    </html>
  );
}
