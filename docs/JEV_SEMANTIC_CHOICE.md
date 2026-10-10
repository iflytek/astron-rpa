# Optional Jev provider

The generic [semantic choice component](SEMANTIC_CHOICE.md) defaults to the
existing OpenAI-compatible service. To explicitly select Jev, add these values
to `docker/.env`:

```dotenv
SEMANTIC_CHOICE_ENABLED=true
SEMANTIC_CHOICE_PROVIDER=jev
JEV_API_KEY=your-typesafe-api-key
JEV_MODEL=jev-latest
```

The shared `SEMANTIC_CHOICE_TIMEOUT_SECONDS` and `SEMANTIC_CHOICE_POINTS_COST`
settings also apply. Restart the AI and robot services after changing settings.
A missing key disables availability and execution reports `JEV_API_KEY`.
The provider uses `https://api.typesafe.ai/v1/systemone` directly; no SDK is
required. Credentials never belong in client metadata or workflow variables.

`jev-latest` follows stable model releases. Pin a supported version through
`JEV_MODEL` when reproducibility is required. Responses preserve Jev's native
confidence; it is distinct from the winning option's probability. Probability
distributions and token usage are not exposed in the workflow result.

There are at most 254 business options plus an explicit abstention option.
`__abstain__` is an integration-defined choice, not a native API response status.
Unlike the SDK, this integration does not retry 429/529 responses automatically;
provider failures remain workflow errors and do not deduct application points.
Jev 1.13 supports text inputs and limits state plus the longest question to 32k
tokens. Application character bounds cannot guarantee that token limit.

English is the model's strongest documented language; evaluate Chinese inputs
on actual workload samples. Three live Chinese smoke examples previously
validated refund/shipping/abstention with `jev-1.13.0`; this is not a quality or
speed benchmark and does not validate subsequent alias changes.

References: [Quick start](https://docs.typesafe.ai/introduction/quickstart),
[API](https://docs.typesafe.ai/api), [Models](https://docs.typesafe.ai/models).
