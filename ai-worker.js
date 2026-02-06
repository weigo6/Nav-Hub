/**
 * Cloudflare Worker for AI Chat (SiliconFlow Adapter)
 * 
 * Deployment Instructions:
 * 1. Log in to Cloudflare Dashboard -> Workers & Pages -> Create Application -> Create Worker.
 * 2. Name it (e.g., 'nav-hub-ai').
 * 3. Copy-paste this code into the editor (main.js or worker.js).
 * 4. Go to Settings -> Variables -> Add Variable:
 *    - Variable name: SILICONFLOW_API_KEY
 *    - Value: Your SiliconFlow API Key (sk-...)
 *    - Encrypt: Yes
 * 5. Save and Deploy.
 * 6. Copy the Worker URL (e.g., https://nav-hub-ai.username.workers.dev) and update your frontend config.
 */

export default {
  async fetch(request, env, ctx) {
    // === CONFIGURATION ===
    const ALLOWED_ORIGINS = [
      "*" // For development/testing. In production, change this to your specific domain(s), e.g., "https://nav.example.com"
      // "https://another-site.com" 
    ];
    
    // Default model (can be overridden by client if allowed, but hardcoded here for safety)
    const MODEL_NAME = "deepseek-ai/DeepSeek-V3";
    const API_URL = "https://api.siliconflow.cn/v1/chat/completions";

    // === CORS HANDLING ===
    const origin = request.headers.get("Origin");
    const isAllowedOrigin = ALLOWED_ORIGINS.includes("*") || ALLOWED_ORIGINS.includes(origin);
    
    const corsHeaders = {
      "Access-Control-Allow-Origin": isAllowedOrigin ? origin : "null",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Access-Control-Max-Age": "86400",
    };

    // Handle preflight requests
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    // Only allow POST requests
    if (request.method !== "POST") {
      return new Response("Method Not Allowed", { status: 405, headers: corsHeaders });
    }

    // === API KEY CHECK ===
    const apiKey = env.SILICONFLOW_API_KEY;
    if (!apiKey) {
      return new Response(JSON.stringify({ error: "Server Configuration Error: API Key missing." }), {
        status: 500,
        headers: { "Content-Type": "application/json", ...corsHeaders }
      });
    }

    try {
      // === REQUEST PROCESSING ===
      const { messages } = await request.json();

      if (!messages || !Array.isArray(messages)) {
        return new Response(JSON.stringify({ error: "Invalid request body" }), { 
          status: 400, 
          headers: { "Content-Type": "application/json", ...corsHeaders } 
        });
      }

      // === UPSTREAM REQUEST ===
      const upstreamResponse = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${apiKey}`
        },
        body: JSON.stringify({
          model: MODEL_NAME,
          messages: messages,
          stream: true
        })
      });

      if (!upstreamResponse.ok) {
        const errorText = await upstreamResponse.text();
        return new Response(JSON.stringify({ error: `Upstream API Error: ${upstreamResponse.statusText}`, details: errorText }), {
          status: upstreamResponse.status,
          headers: { "Content-Type": "application/json", ...corsHeaders }
        });
      }

      // === STREAMING RESPONSE ===
      const { readable, writable } = new TransformStream();
      upstreamResponse.body.pipeTo(writable);

      return new Response(readable, {
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          "Connection": "keep-alive",
          ...corsHeaders
        }
      });

    } catch (error) {
      return new Response(JSON.stringify({ error: `Worker Error: ${error.message}` }), {
        status: 500,
        headers: { "Content-Type": "application/json", ...corsHeaders }
      });
    }
  }
};
