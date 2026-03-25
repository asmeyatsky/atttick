import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Staff Echo",
  description: "AI chatbot trained on staff expertise",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        style={{
          margin: 0,
          fontFamily:
            '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
          backgroundColor: "#f9fafb",
          color: "#1f2937",
        }}
      >
        {children}
      </body>
    </html>
  );
}
