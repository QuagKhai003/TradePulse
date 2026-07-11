/**
 * layout.js — root layout (plan §10.4: Vietnamese default).
 * @context  Wraps every page; loads the type system (Inter for UI incl. Vietnamese, JetBrains Mono
 *           for numerals — the terminal/data feel) + global CSS. HTML lang defaults to vi.
 * @affects  All routes.
 */
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const sans = Inter({ subsets: ["latin", "latin-ext", "vietnamese"], variable: "--font-sans", display: "swap" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono", display: "swap" });

export const metadata = {
  title: "TradePulse — Ra-đa nhu cầu xuất khẩu",
  description: "Nhu cầu thế giới đang dịch chuyển ở đâu — cho nhà xuất khẩu Việt Nam.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="vi" className={`${sans.variable} ${mono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
