import "./globals.css";

export const metadata = {
  title: "PR Media Monitor",
  description: "Multi-client media monitoring dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
