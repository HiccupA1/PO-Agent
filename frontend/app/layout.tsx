import "./styles.css";

import type { ReactNode } from "react";

export const metadata = {
  title: "PO Agent",
  description: "Product Owner Backlog Architect"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
