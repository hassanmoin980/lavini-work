2000 input + 600 output tokens per note, bursts of 20 concurrent,
p95 under 8s, current spend $2000/month.

# Cost per note

(2000 x input rate + 600 x output rate) / 1000000

| Model | Rate in/out per 1M | Per note |
|---|---|---|
| Small (Llama-3.1-8B, hosted) | $0.01 / $0.05 | $0.000050 |
| Large (Llama-3.3-70B, hosted) | $0.10 / $0.50 | $0.000500 |
| Routed mix (75% small, 25% large) | - | $0.000162 |

# Monthly cost

| Notes/month | All small | All large | Routed mix |
|---|---|---|---|
| 10000 | $0.50 | $5.00 | $1.62 |
| 50000 | $2.50 | $25.00 | $8.12 |
| 250000 | $12.50 | $125.00 | $40.62 |

At 50000 notes a month the model bill is about $8. Sending every note to the 70B
costs $25.

# The three options

- Commercial hosted: Most expensive.
- Hosted open-weight: the tables above.
- Self-hosted: Upfront capital cost.

# Utilisation

Using 2.0s per call (estimated):

- 50000 notes x 2.0s = 27.8 GPU-hours. Out of 730 (365 days × 24 hours ÷ 12 months) in a month = 3.8% busy, 96.2 idle.

# Break-even

Notes/month before self-hosting beats the routed mix:

$2000/mo ---> 12345679
(2000 ÷ 0.000162)

# Operational overhead

LLM as a Judge, hosting costs, fine-tuning costs (if needed)

# Latency
- Currently serial implementation of 8B via the router takes ~2.0s.
- Assuming 25% of traffic goes to the 70B, which is slower. p95 is set by that path.
