# AI providers and models

Netra AI supports OpenAI, Google AI Studio, Google Vertex AI, Anthropic, Azure OpenAI,
AWS Bedrock, and OpenAI-compatible endpoints, including local models through Ollama.

Set `AI_PROVIDER` and configure your provider's credentials and model IDs using
the [installation guide](INSTALLATION.md#ai-provider-configuration) and
[configuration template](../.env.example). Reasoning and coding can use the same
model or different models. Choose models that support structured tool calls;
answer quality, speed, and cost vary by model.

## Model reference

This list builds on
[Tako's AI provider guide](https://github.com/fctr-id/okta-ai-agent#ai-provider-support)
for the shared agent harness, with Netra AI's selected model updates. It is not a
separate Netra AI compatibility certification or a guarantee of current provider
availability.

| Provider | Model |
| --- | --- |
| DeepSeek | DeepSeek V4.1 Flash |
| Z.ai | GLM 5.3 |
| Google | Gemini 3.8 Flash |
| OpenAI | GPT-5.6 Terra |
| Anthropic | Claude Haiku 5.5 |

DeepSeek and Z.ai connect through `openai_compatible`. Use the model identifier
provided by your chosen service and test representative Entra questions before
relying on its results. Smaller, older, or untested models may give less reliable
answers.

## Reasoning setting

`AI_REASONING_EFFORT` optionally requests a shared reasoning setting for the
agents. Netra AI accepts `minimal`, `low`, `medium`, `high`, `xhigh`, `true`, `false`,
and `none`; support for individual values depends on the provider and model.
Higher effort can increase response time and cost.

The sample configuration leaves this unset. To request more reasoning, add
`AI_REASONING_EFFORT=high` to your configuration and restart Netra AI. If the model
rejects it, use `none` or remove the setting and restart. An unset, blank, or
`none` value sends no reasoning override; it does not disable a model's default
reasoning. Use only settings supported by your chosen provider and model.

## Data sent to the model

Prompts and selected directory context go to your configured model provider,
even when Netra AI itself runs locally. A compatible local model keeps inference
on your infrastructure. Review your chosen provider's data-handling terms before
sending tenant data.
