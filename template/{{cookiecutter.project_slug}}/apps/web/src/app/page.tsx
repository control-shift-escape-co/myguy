"use client";

import { CopilotChat } from "@copilotkit/react-ui";

const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME ?? "{{ cookiecutter.project_name }}";

const CHAT_LABELS = {
  title: APP_NAME,
  initial: "Hey — your agent is live. Ask me anything.",
};

export default function Page() {
  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">g.</span>
          <span className="brand-name">{APP_NAME}</span>
        </div>
        <span className="pattern-badge">{{ cookiecutter.agent_pattern }}</span>
      </header>
      <CopilotChat
        className="chat"
        instructions={
          "You are the agent for this app. Follow the backend system prompt and use your tools."
        }
        labels={CHAT_LABELS}
      />
      <footer className="footer">
        <span>
          built with <a href="https://github.com/control-shift-escape-co/myguy">myg</a>
        </span>
      </footer>
    </main>
  );
}
