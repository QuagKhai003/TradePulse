/**
 * layout.js — root layout (plan §10.4: Vietnamese default).
 * @context  Wraps every page; loads global CSS + metadata. HTML lang defaults to vi.
 * @affects  All routes.
 */
import "./globals.css";

export const metadata = {
  title: "TradePulse — Ra-đa nhu cầu xuất khẩu",
  description: "Nhu cầu thế giới đang dịch chuyển ở đâu — cho nhà xuất khẩu Việt Nam.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="vi">
      <body>{children}</body>
    </html>
  );
}
