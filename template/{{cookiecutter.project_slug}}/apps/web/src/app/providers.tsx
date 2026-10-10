"use client";

import { CopilotKit } from "@copilotkit/react-core";

// `agent` must match the key registered in api/copilotkit/route.ts.
export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit" agent="agent">
      {children}
    </CopilotKit>
  );
}
