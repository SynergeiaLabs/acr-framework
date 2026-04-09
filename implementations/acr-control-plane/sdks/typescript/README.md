# ACR TypeScript SDK

This package provides the official TypeScript client for the ACR control plane.

## What It Covers

- operator-side agent registration
- token issuance
- runtime calls to `POST /acr/evaluate`
- session-bound agent helpers
- decision-aware error helpers

## Install

```bash
npm install acr-control-plane-sdk
```

## Basic Usage

```ts
import { ACRClient } from "acr-control-plane-sdk";

const client = new ACRClient({
  baseUrl: "https://acr.example.com",
  operatorApiKey: process.env.ACR_OPERATOR_API_KEY!,
});

await client.ensureAgentRegistered({
  agent_id: "support-bot",
  owner: "support@example.com",
  purpose: "Handle support actions",
  risk_tier: "medium",
  allowed_tools: ["query_customer_db", "send_email"],
});

const session = await client.issueAgentSession("support-bot");

const result = await session.evaluateAction({
  tool_name: "send_email",
  parameters: {
    to: "alice@example.com",
    subject: "Ticket update",
    body: "We resolved your issue."
  },
  description: "Send support resolution email"
}, {
  session_id: "sess-123"
});

console.log(result.decision);
```

## Decision Handling

The SDK returns normal decision payloads for:

- `allow`
- `modify`
- `deny`
- `escalate`

If you want exception-based control flow, use `assertRunnableDecision(result)`.

## Package Layout

- [src/index.ts](src/index.ts): source SDK
- [dist/index.js](dist/index.js): runtime JS entrypoint
- [dist/index.d.ts](dist/index.d.ts): published TypeScript declarations
