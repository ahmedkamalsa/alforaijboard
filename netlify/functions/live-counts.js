const ALFORAIJ_TYPES = [1, 2, 3, 4, 5];
const ALFORAIJ_SEARCH_URL = "https://search.alforaij.com/api/internallistings/search";
const SUPABASE_URL = "https://bwspcsiazbwrrxpgoldx.supabase.co";
const SUPABASE_ANON_KEY = "sb_publishable_c84oHQS94osRqw_SiTIqMg_8icxvatZ";
const CACHE_KEY = "alforaijboard:live-counts:v1";
const CACHE_TTL_SECONDS = 180;
const RATE_LIMIT_SECONDS = 60;
const RATE_LIMIT_MAX = 120;

function json(statusCode, body) {
  return {
    statusCode,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "public, max-age=60, stale-while-revalidate=120",
      "access-control-allow-origin": "*",
    },
    body: JSON.stringify(body),
  };
}

function redisConfig() {
  const url = process.env.UPSTASH_REDIS_REST_URL;
  const token = process.env.UPSTASH_REDIS_REST_TOKEN;
  return url && token ? { url: url.replace(/\/$/, ""), token } : null;
}

async function redisCommand(command) {
  const cfg = redisConfig();
  if (!cfg) return null;
  const response = await fetch(`${cfg.url}/${command.map(encodeURIComponent).join("/")}`, {
    method: "POST",
    headers: { authorization: `Bearer ${cfg.token}` },
  });
  if (!response.ok) return null;
  return response.json();
}

async function checkRateLimit(event) {
  const cfg = redisConfig();
  if (!cfg) return { allowed: true, source: "none" };
  const ip = event.headers["x-nf-client-connection-ip"] || event.headers["x-forwarded-for"] || "unknown";
  const key = `alforaijboard:rl:${String(ip).split(",")[0].trim()}`;
  const countResult = await redisCommand(["INCR", key]);
  const count = Number(countResult?.result || 0);
  if (count === 1) await redisCommand(["EXPIRE", key, String(RATE_LIMIT_SECONDS)]);
  return { allowed: count <= RATE_LIMIT_MAX, source: "upstash", count };
}

async function getCachedCounts() {
  const cached = await redisCommand(["GET", CACHE_KEY]);
  if (!cached?.result) return null;
  try {
    return JSON.parse(cached.result);
  } catch {
    return null;
  }
}

async function setCachedCounts(payload) {
  await redisCommand(["SET", CACHE_KEY, JSON.stringify(payload), "EX", String(CACHE_TTL_SECONDS)]);
}

async function fetchAlforaijTotal() {
  const totals = await Promise.all(ALFORAIJ_TYPES.map(async (typeId) => {
    const response = await fetch(`${ALFORAIJ_SEARCH_URL}?page=1&pageSize=1&transactionType=${typeId}`, {
      headers: { accept: "application/json,text/plain,*/*" },
    });
    if (!response.ok) return 0;
    const payload = await response.json().catch(() => null);
    const total = Number(payload?.meta?.total || 0);
    return total || (Array.isArray(payload?.data) ? payload.data.length : 0);
  }));
  return totals.reduce((sum, value) => sum + Number(value || 0), 0);
}

async function fetchExternalTotal() {
  const response = await fetch(`${SUPABASE_URL}/rest/v1/market_listings?select=id&limit=1`, {
    headers: {
      apikey: SUPABASE_ANON_KEY,
      authorization: `Bearer ${SUPABASE_ANON_KEY}`,
      prefer: "count=exact",
    },
  });
  if (!response.ok) return 0;
  const range = response.headers.get("content-range") || "";
  const match = range.match(/\/(\d+)$/);
  return match ? Number(match[1]) : 0;
}

exports.handler = async (event) => {
  if (event.httpMethod === "OPTIONS") return json(200, { ok: true });

  const limited = await checkRateLimit(event).catch(() => ({ allowed: true, source: "error" }));
  if (!limited.allowed) {
    return json(429, { ok: false, error: "rate_limited", source: limited.source });
  }

  const cached = await getCachedCounts().catch(() => null);
  if (cached) return json(200, { ...cached, cached: true, cache: "upstash" });

  const [local, external] = await Promise.all([fetchAlforaijTotal(), fetchExternalTotal()]);
  const payload = {
    ok: true,
    local,
    external,
    total: local + external,
    updated_at: new Date().toISOString(),
    source: "alforaij_public_api+supabase",
    cached: false,
  };
  await setCachedCounts(payload).catch(() => {});
  return json(200, payload);
};
