# feedback-synthesizer

Multi-source product feedback aggregator. Collects feedback from WhatsApp, email, and other sources, categorizes by topic and sentiment, and surfaces trends.

## When to use
- Owner asks: "what are users saying about X?"
- After a product release or update
- Weekly/monthly product review

## Steps

1. **Collect** — gather feedback snippets from configured sources (WhatsApp groups, email threads, notes)
2. **Categorize** — group by topic (UX, performance, feature request, bug) and sentiment (positive/negative/neutral)
3. **Synthesize** — produce a concise summary with trend highlights and top issues
4. **Deliver** — send summary to owner via preferred channel

## Output format
- Top 3 themes (with count + sentiment)
- Notable quotes (max 3)
- Recommended action (if any)
- Total feedback items processed

## Config (.context file)
Store in `skills/feedback-synthesizer/.context`:
```
FEEDBACK_SOURCES=whatsapp,email
PRODUCT_NAMES=Vibe,Sidekick,Custom Agents
DELIVERY_CHANNEL=whatsapp
DELIVERY_TARGET=<owner_phone>
```

## Notes
- Works best with 5+ feedback items
- Hebrew + English supported
- No external API required — uses web_search + message tools

## Credit
Contributed by Mira Solane / Luma (Kate's PA), April 2026.
