# Resumo dos testes – 18/11/2026 11:33 a 18/11/2026 15:32

Modelo solicitado: `gemini-3.6-flash` · versões retornadas: gemini-3.6-flash
Respostas válidas: 3 de 30 previstas · **bateria interrompida:** tarefa2_padrao_rep1: sem resposta válida após 40 tentativas
Novas tentativas por falha da API: 4 (429: 1, 503: 3)
Respostas cortadas por MAX_TOKENS: 0

Valores: média ± desvio-padrão (mínimo–máximo).

| Tarefa | Condição | n | Tempo de resposta (s) | Bloco [ETAPAS] (caracteres) | Resposta final (caracteres) | Tokens de saída | Tokens de raciocínio nativo | [ETAPAS] presente | MAX_TOKENS | Novas tentativas |
|---|---|---|---|---|---|---|---|---|---|---|
| Tarefa 1 - Estruturação de seção de TCC | ChaTinho (com prompt de direcionamento) | 1 | 13,88 ± 0,00 (13,88–13,88) | 453 ± 0 (453–453) | 4803 ± 0 (4803–4803) | 1344 ± 0 (1344–1344) | 572 ± 0 (572–572) | 100% | 0 | 0 |
| Tarefa 1 - Estruturação de seção de TCC | Gemini padrão (sem prompt de direcionamento) | 1 | 62,97 ± 0,00 (62,97–62,97) | 0 ± 0 (0–0) | 5107 ± 0 (5107–5107) | 1314 ± 0 (1314–1314) | 966 ± 0 (966–966) | 0% | 0 | 4 |
| Tarefa 2 - Análise multimodal de PDF | ChaTinho (com prompt de direcionamento) | 1 | 44,94 ± 0,00 (44,94–44,94) | 505 ± 0 (505–505) | 4489 ± 0 (4489–4489) | 1426 ± 0 (1426–1426) | - | 100% | 0 | 0 |
| Tarefa 2 - Análise multimodal de PDF | Gemini padrão (sem prompt de direcionamento) | 0 | - | - | - | - | - | - | 0 | 0 |
| Tarefa 3 - Self-Attention, CoT e 4 referências ABNT | ChaTinho (com prompt de direcionamento) | 0 | - | - | - | - | - | - | 0 | 0 |
| Tarefa 3 - Self-Attention, CoT e 4 referências ABNT | Gemini padrão (sem prompt de direcionamento) | 0 | - | - | - | - | - | - | 0 | 0 |

## Configuração (idêntica nas duas condições)

- temperature: 1.0 · top_p: 0.95 · top_k: 64
- max_output_tokens: 8192 · thinking_level: low · candidate_count: 1
- seed: não definida · safety_settings: padrão do serviço · system_instruction: não utilizado
- prompt do ChaTinho concatenado à mensagem do usuário · conversa nova a cada execução
- Python 3.14.3 · google-genai 3.2.0
