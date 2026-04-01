// AI-PA Billing Monitor Plugin
// Checks API billing health and alerts owner on errors

import type { OpenClawPlugin } from "@openclaw/sdk";

interface BillingConfig {
  adminPhone?: string;
  checkInterval?: number;
}

const PROVIDERS = [
  {
    name: "Anthropic",
    check: async (apiKey: string) => {
      const res = await fetch("https://api.anthropic.com/v1/models", {
        headers: {
          "x-api-key": apiKey,
          "anthropic-version": "2023-06-01"
        }
      });
      return res.status; // 200=ok, 401=invalid key, 402=billing
    },
    envKey: "ANTHROPIC_API_KEY"
  },
  {
    name: "OpenAI",
    check: async (apiKey: string) => {
      const res = await fetch("https://api.openai.com/v1/models", {
        headers: { "Authorization": `Bearer ${apiKey}` }
      });
      return res.status;
    },
    envKey: "OPENAI_API_KEY"
  }
];

function interpretStatus(status: number): "ok" | "billing_error" | "invalid_key" | "unknown" {
  if (status === 200) return "ok";
  if (status === 402) return "billing_error";
  if (status === 401) return "invalid_key";
  return "unknown";
}

export default {
  id: "ai-pa-billing-monitor",

  async onHeartbeat(ctx) {
    const config: BillingConfig = ctx.config ?? {};
    const results: string[] = [];

    for (const provider of PROVIDERS) {
      const apiKey = process.env[provider.envKey];
      if (!apiKey) continue;

      try {
        const status = await provider.check(apiKey);
        const result = interpretStatus(status);

        if (result === "billing_error") {
          const msg = `⚠️ Billing error: ${provider.name} API key is out of credits.`;
          results.push(msg);

          // Alert admin if configured
          if (config.adminPhone) {
            await ctx.sendMessage({
              to: config.adminPhone,
              channel: "whatsapp",
              message: msg + " Check your provider's billing dashboard."
            });
          }
        } else if (result === "invalid_key") {
          results.push(`❌ Invalid key: ${provider.name} API key is not valid.`);
        }
      } catch (err) {
        results.push(`? ${provider.name}: check failed (network error)`);
      }
    }

    return {
      status: results.length === 0 ? "ok" : "issues_found",
      issues: results
    };
  }
} satisfies OpenClawPlugin;
