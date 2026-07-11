/**
 * layout.js — root layout (plan §10.4: Vietnamese default).
 * @context  Three-role type system: Space Grotesk (display — brand + titles), Inter (UI/body, incl.
 *           Vietnamese), JetBrains Mono (numerals). HTML lang defaults to vi.
 * @affects  All routes.
 */
import { Inter, Space_Grotesk, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const sans = Inter({ subsets: ["latin", "vietnamese"], variable: "--font-sans", display: "swap" });
const display = Space_Grotesk({ subsets: ["latin", "vietnamese"], variable: "--font-display", display: "swap", weight: ["600", "700"] });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono", display: "swap" });

export const metadata = {
  title: "TradePulse — Ra-đa nhu cầu xuất khẩu",
  description: "Nhu cầu thế giới đang dịch chuyển ở đâu — cho nhà xuất khẩu Việt Nam.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="vi" className={`${sans.variable} ${display.variable} ${mono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
