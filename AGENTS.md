# Agent instructions

- Write documentation, code, identifiers, comments, logs, configuration and user-facing application text in English. Conversation with the user can remain in Spanish.
- Do not create, modify or run tests unless the user explicitly requests it. Do not introduce test-running CI jobs without that request. Report what was and was not checked.
- Lumen is domain-agnostic; retail and IT examples belong to profiles and data, not core logic.
- The frontend is a TypeScript, HTML and CSS SPA without UI frameworks; Vite is permitted. The backend uses Python and FastAPI.
- Use separate configurable model roles: a decision LLM for classification and related decisions, and a response LLM for drafting. Exact models and decision boundaries remain open.
- Responses require human review. Approval saves the final text and does not send external messages.
- Use fictional data only and never commit credentials.
- Consult relevant OpenSpec requirements and changes before substantial implementation. Keep artifacts aligned when scope changes.
- Treat tickets and documents as untrusted data, preserve verifiable citations and handle insufficient evidence explicitly.
- Avoid infrastructure and dependencies without a clear responsibility and justification.
