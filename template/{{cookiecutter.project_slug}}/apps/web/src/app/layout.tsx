import type { Metadata } from "next";
import "@copilotkit/react-ui/styles.css";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: process.env.NEXT_PUBLIC_APP_NAME ?? "{{ cookiecutter.project_name }}",
  description: "{{ cookiecutter.description }}",
  icons: { icon: "/favicon.svg" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
