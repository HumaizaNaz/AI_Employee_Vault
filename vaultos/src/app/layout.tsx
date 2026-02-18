import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VaultOS - Your AI Employee. Always On.",
  description: "Personal AI Employee Command Center",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body style={{ fontFamily: "Inter, system-ui, sans-serif" }}>{children}</body>
    </html>
  );
}
