2000 input + 600 output tokens per note, bursts of 20 concurrent, p95 under 8s, current spend $2000/month.

Commercial option is Gemini (cheapest between OpenAI and Anthropic).

- Gemini 3.1 Flash-Lite: $0.25 / 1M input, $1.50 / 1M output
- Gemini 3.7 Flash: $1.50 / 1M input, $7.50 / 1M output

Output prices include thinking tokens.

NOTE: The same Llama weights show up as two different options, because the delivery mode is what drives the cost, not the model:

| Option | What it is | How it's billed |
|---|---|---|
| Commercial hosted | Gemini Flash-Lite / Flash | Per token |
| Hosted open-weight | Llama via 3rd party hosting platform | Per token / per hour cost (depends) |
| Self-hosted open-weight | The same Llama weights on our own GPU | No per-token cost at all, just one-time GPU bill + maintenance |

# Cost per note

(2000 x input rate + 600 x output rate) / 1000000

| Option | Rate in/out per 1M | Per note |
|---|---|---|
| Gemini 3.1 Flash-Lite | $0.25 / $1.50 | $0.001400 |
| Gemini 3.7 Flash | $1.50 / $7.50 | $0.007500 |
| Gemini routed mix (Flash-Lite / Flash 75/25) | - | $0.002925 |
| Self-hosted Llama (either size) | no per-token cost | $0.000000 |

- Self-hosted has no per-note rate - that's the point of it. Its cost is the GPU bill divided by however many notes you push through.
- Flash-Lite as the economy tier, Flash as the strong tier for escalated notes.

NOTE: The other recurring problem with commercial models is that they get retired. Version names move fast, rates change under a name, and a model you validated can be retired with a few months' notice. That forces a re-run of the evaluation gate on a vendor's schedule rather than ours, and there's no option to pin a version indefinitely. 

# Monthly cost - the three options

| Notes/month | Flash-Lite | Flash | Gemini mix | Self-hosted (1 GPU) |
|---|---|---|---|---|
| 10000 | $14 | $75 | $29 | ~$1460 |
| 50000 | $70 | $375 | $146 | ~$1460 |
| 250000 | $350 | $1875 | $731 | ~$1460 |

Self-hosted is flat (assuming one rented GPU, 730 hours, at $2.00/GPU-hour). Everything else scales linearly. Renting is opex only, no capex. Buying adds capex plus depreciation and needs steady high utilisation.

> NOTE: $2000 at 50000 notes is $0.04/note. The routed Gemini mix is $0.0029, ~14x cheaper. Even sending every note to Flash is $0.0075, still 5x cheaper.

# Utilisation

Using 2.0s per call (estimated):

- 50000 notes x 2.0s = 27.8 GPU-hours, out of 730 (365 x 24 / 12) in a month.
- 3.8% busy, 96.2% idle.

You'd also size for the 20-concurrent burst, which is peak capacity left idle almost always.

# Break-even

Break-even = (self-hosted monthly cost) / (hosted cost per note). At ~$1460/month:

| Compared against | Break-even | Can one GPU serve it? |
|---|---|---|
| Gemini 3.7 Flash | 194667 notes/mo | Yes - 15% of one GPU |
| Gemini routed mix | 499145 notes/mo | Yes - 38% |
| Gemini 3.1 Flash-Lite | 1042857 notes/mo | Just - 79%, no burst headroom |

One GPU at 2.0s/note flat out for 730 hours tops out at 1314000 notes/month. That ceiling matters, because a break-even is only meaningful if the fixed cost stays fixed at that volume. past the ceiling you buy another GPU and break-even moves further away.

> NOTE: Self-hosting is a PHI decision, not a cost decision in this scenario.

# Operational overhead

eval runs on every model change. re-testing when a provider swaps a model, and the LLM-as-judge calls in the evaluation and causes operational overhead. Self-hosting adds GPU ops.

# Latency

- Serial 8B via the router: ~2.0s (estimated).
- 25% of traffic goes to the strong tier, which is slower in response, so p95 is set here.
- 20 concurrent through a shared router depends on which path it goes through.

# The $2000 assumption

$2000 is nowhere near the limit: it buys 1.4 million notes/month on Flash-Lite, 684000 on the routed Gemini mix, 267000 on Flash. At the stated 50000 notes the token bill is $8 to $375. The binding constraint isn't cost, it's throughput, p95 latency under the 20-concurrent burst, provider rate limits, and cold starts. As mentioned previously, self-hosting is more of a PHI issue than a cost issue.

# What actually caps throughput

1. Concurrency against the p95 budget: At ~2.0s per call an 8s budget fits 4 calls
serially. So clearing a burst of 20 within 8s needs at least 5 parallel inference slots.

2. Provider rate limits.

3. Cold starts on self-hosted.

> NOTE: Escalation rate is free on open-weight, not on Gemini, and will scale accordingly.
