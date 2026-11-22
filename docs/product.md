# Product vision and scope

Lumen is a domain-agnostic ticket assistant that classifies requests and drafts responses grounded in configurable documentation for human review and approval. It is a reproducible portfolio demo, independent of existing ticketing systems.

A support operator manages documents, creates and reviews tickets, checks sources, edits drafts and approves the final text. Approval stores the text without sending it externally.

| Example profile | Documentation | Tickets |
| --- | --- | --- |
| Online retail | Shipping, returns and warranty | Late order, defective product, duplicate charge |
| IT support | VPN, access and device incidents | Connection failure, locked account, undocumented issue |

Each profile has its own documentation and configurable categories. Retrieval is scoped to the selected knowledge base. This separation does not itself provide secure tenant isolation.

The current application supports text and Markdown knowledge ingestion, lexical retrieval, on-demand response suggestions, source inspection, insufficient-evidence results, execution diagnostics and human approval. A decision LLM handles classification; a separately configured response LLM drafts grounded answers. Profile management, restorable fictional examples and a simulated response mode remain planned. Exact models and additional decision boundaries remain open.

No external ticketing integration, outbound messages, OCR, real customer data or real actions on orders or IT systems are in scope. Local accounts use administrator and operator roles in one shared workspace. Email invitations, secure multitenancy and high availability are outside the demo.

Success means both profiles work through the same core; the simulated demo runs without model credentials; real-AI drafts expose sources; missing evidence is presented for human review; and approval persists the final text. Document what has actually been implemented and checked. Do not create or run tests without explicit user instruction.

