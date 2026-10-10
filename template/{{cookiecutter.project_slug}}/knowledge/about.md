# About {{ cookiecutter.project_name }}

{{ cookiecutter.description }}

This app was scaffolded by [myg](https://github.com/control-shift-escape-co/myguy).
The backend is a LangGraph agent using the `{{ cookiecutter.agent_pattern }}`
pattern, served over AG-UI to a Next.js + CopilotKit frontend. Conversation
threads persist in {{ cookiecutter.db }}.

## Using the knowledge base

Drop `.md` or `.txt` files in this directory. The agent's
`search_knowledge_base` tool retrieves the most relevant passages and cites the
file they came from. Replace this file with your own docs — product specs,
FAQs, policies, domain notes.
