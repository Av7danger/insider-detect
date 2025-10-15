const API_BASE = '/api';

export type HealthResponse = { status: string };
export type ModelInfoResponse = {
  model_name?: string;
  xgb_version?: string;
  requests_per_min?: number;
};
export type StatisticsResponse = {
  total_requests?: number;
  requests_per_min?: number;
  uptime_seconds?: number;
};

export async function getHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health ${res.status}`);
  return res.json();
}

export async function getModelInfo(): Promise<ModelInfoResponse> {
  const res = await fetch(`${API_BASE}/model_info`);
  if (!res.ok) throw new Error(`ModelInfo ${res.status}`);
  return res.json();
}

export async function getStatistics(): Promise<StatisticsResponse> {
  const res = await fetch(`${API_BASE}/statistics`);
  if (!res.ok) throw new Error(`Statistics ${res.status}`);
  return res.json();
}

export function formatThroughputFromStats(stats?: StatisticsResponse | null): string {
  if (!stats) return '-- req/s';
  const rpm = typeof stats.requests_per_min === 'number' ? stats.requests_per_min : undefined;
  if (rpm === undefined) return '-- req/s';
  return `${(rpm / 60).toFixed(2)} req/s`;
}
