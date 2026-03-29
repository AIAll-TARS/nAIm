import type { Metadata } from "next";
import localFont from "next/font/local";
import { Analytics } from "@vercel/analytics/next";
import "./globals.css";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://naim.janis7ewski.org";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: "nAIm — API service registry for AI agents",
  description: "Machine-first registry of API services built for agents, by agents.",
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: "nAIm — API service registry for AI agents",
    description: "Machine-first registry of API services built for agents, by agents.",
    url: siteUrl,
    siteName: "nAIm",
    type: "website",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        {/* AI agent discovery */}
        <link rel="mcp" href="https://mcp.naim.janis7ewski.org" title="nAIm API Registry MCP" />
        <link rel="ai-plugin" href="https://naim.janis7ewski.org/.well-known/ai-plugin.json" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
        <Analytics />
      </body>
    </html>
  );
}
