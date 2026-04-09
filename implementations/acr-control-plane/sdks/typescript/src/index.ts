export type Decision = "allow" | "deny" | "modify" | "escalate";

export interface ActionRequest {
  tool_name: string;
  parameters?: Record<string, unknown>;
  description?: string;
}

export interface IntentRequest {
  goal?: string;
  justification?: string;
  expected_effects?: string[];
  requested_by_step?: string;
  metadata?: Record<string, unknown>;
}

export interface EvaluateRequest {
  agent_id: string;
  action: ActionRequest;
  context?: Record<string, unknown>;
  intent?: IntentRequest;
}

export interface PolicyDecision {
  policy_id: string;
  decision: Decision;
  reason?: string | null;
  latency_ms?: number | null;
}

export interface EvaluateResponse {
  decision: Decision;
  correlation_id?: string | null;
  reason?: string | null;
  error_code?: string | null;
  approval_request_id?: string | null;
  approval_queue?: string | null;
  sla_minutes?: number | null;
  policy_decisions?: PolicyDecision[];
  drift_score?: number | null;
  latency_ms?: number | null;
  estimated_cost_usd?: number | null;
  authoritative_hourly_spend_usd?: number | null;
  modified_action?: ActionRequest | null;
  execution_result?: Record<string, unknown> | null;
}

export interface AgentBoundaries {
  max_actions_per_minute?: number;
  max_cost_per_hour_usd?: number;
  default_action_cost_usd?: number | null;
  tool_costs_usd?: Record<string, number>;
  allowed_regions?: string[];
  credential_rotation_days?: number;
}

export interface DataAccessEntry {
  resource: string;
  permission?: "READ" | "READ_WRITE" | "WRITE" | "NONE";
}

export interface AgentRegisterRequest {
  agent_id: string;
  owner: string;
  purpose: string;
  risk_tier?: "low" | "medium" | "high";
  allowed_tools?: string[];
  forbidden_tools?: string[];
  data_access?: DataAccessEntry[];
  boundaries?: AgentBoundaries;
  version?: string;
  parent_agent_id?: string | null;
  capabilities?: string[];
  lifecycle_state?: "draft" | "active" | "deprecated" | "retired";
}

export interface AgentResponse extends AgentRegisterRequest {
  is_active: boolean;
  health_status: "unknown" | "healthy" | "degraded" | "unhealthy";
  last_heartbeat_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  agent_id: string;
  access_token: string;
  token_type: string;
  expires_in_seconds: number;
}

export interface ACRClientOptions {
  baseUrl: string;
  operatorApiKey?: string;
  fetchImpl?: typeof fetch;
}

export class ACRHttpError extends Error {
  readonly statusCode: number;
  readonly body: unknown;

  constructor(statusCode: number, message: string, body?: unknown) {
    super(message);
    this.name = "ACRHttpError";
    this.statusCode = statusCode;
    this.body = body;
  }
}

export class ACRDecisionError extends Error {
  readonly response: EvaluateResponse;

  constructor(response: EvaluateResponse) {
    super(response.reason ?? `ACR decision '${response.decision}' blocked execution`);
    this.name = "ACRDecisionError";
    this.response = response;
  }
}

export class ACRDeniedError extends ACRDecisionError {
  constructor(response: EvaluateResponse) {
    super(response);
    this.name = "ACRDeniedError";
  }
}

export class ACREscalatedError extends ACRDecisionError {
  constructor(response: EvaluateResponse) {
    super(response);
    this.name = "ACREscalatedError";
  }
}

function normalizeBaseUrl(baseUrl: string): string {
  return baseUrl.replace(/\/+$/, "");
}

function ensureOperatorApiKey(apiKey: string | undefined): string {
  if (!apiKey) {
    throw new Error("operatorApiKey is required for operator endpoints");
  }
  return apiKey;
}

async function parseResponseBody(response: Response): Promise<unknown> {
  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return response.json();
  }
  return response.text();
}

function assertRunnableDecision(response: EvaluateResponse): EvaluateResponse {
  if (response.decision === "deny") {
    throw new ACRDeniedError(response);
  }
  if (response.decision === "escalate") {
    throw new ACREscalatedError(response);
  }
  return response;
}

export { assertRunnableDecision };

export class ACRClient {
  private readonly baseUrl: string;
  private readonly operatorApiKey?: string;
  private readonly fetchImpl: typeof fetch;

  constructor(options: ACRClientOptions) {
    this.baseUrl = normalizeBaseUrl(options.baseUrl);
    this.operatorApiKey = options.operatorApiKey;
    this.fetchImpl = options.fetchImpl ?? fetch;
  }

  private operatorHeaders(): HeadersInit {
    return {
      "Content-Type": "application/json",
      "X-Operator-API-Key": ensureOperatorApiKey(this.operatorApiKey)
    };
  }

  private agentHeaders(accessToken: string): HeadersInit {
    return {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${accessToken}`
    };
  }

  private async requestJson<T>(path: string, init: RequestInit, expectedStatuses: number[] = [200, 201]): Promise<T> {
    const response = await this.fetchImpl(`${this.baseUrl}${path}`, init);
    const body = await parseResponseBody(response);
    if (!expectedStatuses.includes(response.status)) {
      throw new ACRHttpError(response.status, `ACR API request failed with status ${response.status}`, body);
    }
    return body as T;
  }

  async registerAgent(request: AgentRegisterRequest): Promise<AgentResponse> {
    return this.requestJson<AgentResponse>("/acr/agents", {
      method: "POST",
      headers: this.operatorHeaders(),
      body: JSON.stringify(request)
    });
  }

  async ensureAgentRegistered(request: AgentRegisterRequest): Promise<AgentResponse> {
    const response = await this.fetchImpl(`${this.baseUrl}/acr/agents`, {
      method: "POST",
      headers: this.operatorHeaders(),
      body: JSON.stringify(request)
    });
    const body = await parseResponseBody(response);
    if (response.status === 409) {
      return this.getAgent(request.agent_id);
    }
    if (response.status !== 201) {
      throw new ACRHttpError(response.status, `ACR API request failed with status ${response.status}`, body);
    }
    return body as AgentResponse;
  }

  async getAgent(agentId: string): Promise<AgentResponse> {
    return this.requestJson<AgentResponse>(`/acr/agents/${agentId}`, {
      method: "GET",
      headers: this.operatorHeaders()
    });
  }

  async issueAgentToken(agentId: string): Promise<TokenResponse> {
    return this.requestJson<TokenResponse>(`/acr/agents/${agentId}/token`, {
      method: "POST",
      headers: this.operatorHeaders()
    });
  }

  createAgentSession(agentId: string, accessToken: string): ACRAgentSession {
    return new ACRAgentSession(this, agentId, accessToken);
  }

  async issueAgentSession(agentId: string): Promise<ACRAgentSession> {
    const token = await this.issueAgentToken(agentId);
    return this.createAgentSession(token.agent_id, token.access_token);
  }

  async evaluate(request: EvaluateRequest, accessToken: string): Promise<EvaluateResponse> {
    const response = await this.fetchImpl(`${this.baseUrl}/acr/evaluate`, {
      method: "POST",
      headers: this.agentHeaders(accessToken),
      body: JSON.stringify(request)
    });
    const body = await parseResponseBody(response);
    const expectedStatuses = new Set([200, 202, 403, 500, 503]);
    if (!expectedStatuses.has(response.status)) {
      throw new ACRHttpError(response.status, `Unexpected evaluate response status ${response.status}`, body);
    }
    return body as EvaluateResponse;
  }

  async evaluateAction(
    agentId: string,
    accessToken: string,
    action: ActionRequest,
    context: Record<string, unknown> = {},
    intent?: IntentRequest
  ): Promise<EvaluateResponse> {
    return this.evaluate({
      agent_id: agentId,
      action: {
        tool_name: action.tool_name,
        parameters: action.parameters ?? {},
        description: action.description
      },
      context,
      intent
    }, accessToken);
  }

  async getHealth(): Promise<Record<string, unknown>> {
    return this.requestJson<Record<string, unknown>>("/acr/health", {
      method: "GET"
    }, [200]);
  }

  async getReady(): Promise<Record<string, unknown>> {
    return this.requestJson<Record<string, unknown>>("/acr/ready", {
      method: "GET"
    }, [200, 503]);
  }
}

export class ACRAgentSession {
  private readonly client: ACRClient;
  readonly agentId: string;
  accessToken: string;

  constructor(client: ACRClient, agentId: string, accessToken: string) {
    this.client = client;
    this.agentId = agentId;
    this.accessToken = accessToken;
  }

  async refreshToken(): Promise<TokenResponse> {
    const token = await this.client.issueAgentToken(this.agentId);
    this.accessToken = token.access_token;
    return token;
  }

  async evaluate(request: EvaluateRequest): Promise<EvaluateResponse> {
    if (request.agent_id !== this.agentId) {
      throw new Error("EvaluateRequest.agent_id does not match the bound session agentId");
    }
    return this.client.evaluate(request, this.accessToken);
  }

  async evaluateAction(
    action: ActionRequest,
    context: Record<string, unknown> = {},
    intent?: IntentRequest
  ): Promise<EvaluateResponse> {
    return this.client.evaluateAction(this.agentId, this.accessToken, action, context, intent);
  }
}
