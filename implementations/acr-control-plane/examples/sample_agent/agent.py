"""
ACR Sample Agent — demonstrates all six pillar behaviors.

Run with: python examples/sample_agent/agent.py
Requires: docker-compose up (ACR gateway running on localhost:8000)

This agent:
1. Registers itself with the ACR gateway
2. Issues a short-lived JWT and uses it for all evaluate calls
3. Executes allowed tool calls (query_customer_db, send_email, create_ticket)
4. Attempts a forbidden action (delete_customer) — demonstrates policy denial
5. Attempts a high-value refund (issue_refund amount=250) — demonstrates escalation
"""
from __future__ import annotations

import os
import sys

from acr.pillar1_identity.models import AgentBoundaries, AgentRegisterRequest
from acr.sdk import ACRClient
from acr.gateway.models import EvaluateResponse

ACR_GATEWAY_URL = "http://localhost:8000"
AGENT_ID = "customer-support-01"
OPERATOR_API_KEY = os.getenv("ACR_OPERATOR_API_KEY", "dev-operator-key")


def print_result(action_name: str, result: EvaluateResponse) -> None:
    decision = result.decision
    symbol = {"allow": "✓", "modify": "~", "deny": "✗", "escalate": "⏳"}.get(decision, "?")
    print(f"\n  {symbol} [{decision.upper()}] {action_name}")
    print(f"    Decision: {decision}")
    if result.reason:
        print(f"    Reason: {result.reason}")
    if result.approval_request_id:
        print(f"    Approval ID: {result.approval_request_id}")
    if result.latency_ms is not None:
        print(f"    Latency: {result.latency_ms}ms")
    if result.correlation_id:
        print(f"    Correlation: {result.correlation_id}")


def main() -> None:
    print("=" * 60)
    print("  ACR Sample Agent — Customer Support Bot")
    print("=" * 60)

    with ACRClient(base_url=ACR_GATEWAY_URL, operator_api_key=OPERATOR_API_KEY) as client:
        print("\n[1] Registering agent with ACR gateway...")
        manifest = AgentRegisterRequest(
            agent_id=AGENT_ID,
            owner="support-engineering@example.com",
            purpose="Handle customer support tickets and issue resolutions",
            risk_tier="medium",
            allowed_tools=["query_customer_db", "send_email", "create_ticket", "issue_refund"],
            forbidden_tools=["delete_customer"],
            boundaries=AgentBoundaries(
                max_actions_per_minute=30,
                max_cost_per_hour_usd=5.0,
                credential_rotation_days=90,
            ),
        )
        agent = client.ensure_agent_registered(manifest)
        print(f"  ✓ Agent ready ({agent.agent_id})")

        print("\n[2] Issuing agent JWT through the SDK...")
        session = client.issue_agent_session(AGENT_ID)
        token = session.access_token
        print(f"  ✓ Token issued (length={len(token)} chars)")

        print("\n[3] Executing allowed tool calls...")
        context = {"session_id": "sess-demo-001", "actions_this_minute": 1, "hourly_spend_usd": 0.10}

        result = session.evaluate_action(
            tool_name="query_customer_db",
            parameters={"customer_id": "C-12345"},
            description="Look up customer record",
            context=context,
        )
        print_result("query_customer_db (customer C-12345)", result)

        context["actions_this_minute"] += 1
        result = session.evaluate_action(
            tool_name="send_email",
            parameters={
                "to": "alice@example.com",
                "subject": "Your ticket",
                "body": "We have resolved your issue.",
            },
            description="Send resolution email",
            context=context,
        )
        print_result("send_email (resolution notification)", result)

        context["actions_this_minute"] += 1
        result = session.evaluate_action(
            tool_name="create_ticket",
            parameters={"customer_id": "C-12345", "subject": "Follow-up required"},
            description="Create follow-up ticket",
            context=context,
        )
        print_result("create_ticket (follow-up)", result)

        print("\n[4] Attempting forbidden action (delete_customer)...")
        context["actions_this_minute"] += 1
        result = session.evaluate_action(
            tool_name="delete_customer",
            parameters={"customer_id": "C-12345"},
            description="Delete customer record",
            context=context,
        )
        print_result("delete_customer (should be DENIED)", result)
        assert result.decision == "deny", "Expected policy denial!"

        print("\n[5] Requesting high-value refund (>$100 → human approval required)...")
        context["actions_this_minute"] += 1
        result = session.evaluate_action(
            tool_name="issue_refund",
            parameters={"customer_id": "C-12345", "amount": 250.00, "reason": "Product defect"},
            description="Issue $250 refund",
            context=context,
        )
        print_result("issue_refund $250 (should ESCALATE)", result)
        assert result.decision == "escalate", "Expected escalation!"

        print("\n[6] Checking control plane health...")
        try:
            health = client.get_health()
        except Exception as exc:
            print(f"  ✗ Health check failed: {exc}")
            sys.exit(1)
        print(f"  ✓ Health: {health}")
        print("\n" + "=" * 60)
        print("  Sample agent run complete.")
        print("  All six ACR pillars exercised:")
        print("    ✓ Pillar 1: Identity — agent registered and JWT issued")
        print("    ✓ Pillar 2: Policy — tool allowlist + forbidden tool blocked")
        print("    ✓ Pillar 3: Drift — metrics recorded (async)")
        print("    ✓ Pillar 4: Observability — telemetry events logged")
        print("    ✓ Pillar 5: Containment — kill switch checked each request")
        print("    ✓ Pillar 6: Authority — refund escalated to approval queue")
        print("=" * 60)


if __name__ == "__main__":
    main()
