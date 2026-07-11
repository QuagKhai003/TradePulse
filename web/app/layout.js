/**
 * layout.js — root layout (plan §10.4: Vietnamese default).
 * @context  One warm humanist family (Plus Jakarta Sans) across the app — hierarchy via weight/size,
 *           numerals via tabular figures (no monospace/terminal look). Fewer fonts = faster compile.
 * @affects  All routes.
 */
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const sans = Plus_Jakarta_Sans({
  subsets: ["latin", "vietnamese"],
  variable: "--font-sans",
  display: "swap",
  weight: ["400", "500", "600", "700", "800"],
});

export const metadata = {
  title: "TradePulse — Ra-đa nhu cầu xuất khẩu",
  description: "Nhu cầu thế giới đang dịch chuyển ở đâu — cho nhà xuất khẩu Việt Nam.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="vi" className={sans.variable}>
      <body>{children}</body>
    </html>
  );
}
