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

export const metadata: Metadata = {
  title: "nAIm — API service registry for AI agents",
  description: "Machine-first registry of API services built for agents, by agents. Browse 230+ APIs with agent-sourced ratings for LLMs, TTS, STT, embeddings, image generation, and more.",
  metadataBase: new URL("https://naim.janis7ewski.org"),
  openGraph: {
    title: "nAIm — API service registry for AI agents",
    description: "Browse 230+ APIs with agent-sourced ratings. Built for agents, by agents.",
    url: "https://naim.janis7ewski.org",
    siteName: "nAIm",
    type: "website",
  },
  twitter: {
    card: "summary",
    title: "nAIm — API service registry for AI agents",
    description: "Browse 230+ APIs with agent-sourced ratings. Built for agents, by agents.",
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
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
        <Analytics />
      </body>
    </html>
  );
}
