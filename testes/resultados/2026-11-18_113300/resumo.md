# Resumo dos testes – 18/11/2026 11:33 a 25/11/2026 08:40

Modelo solicitado: `gemini-3.6-flash` · versões retornadas: gemini-3.6-flash
Sessões de execução: 18/11/2026 11:33–15:32; 24/11/2026 21:47–21:53 (pausada: cota diária); 25/11/2026 08:35–08:40
Datas das respostas válidas: 18/11/2026, 24/11/2026, 25/11/2026
Respostas válidas: 30 de 30 previstas
Novas tentativas por falha da API: 45 (429: 29, 503: 16)
Respostas cortadas por MAX_TOKENS: 0

Valores: média ± desvio-padrão (mínimo–máximo).

| Tarefa | Condição | n | Tempo de resposta (s) | Bloco [ETAPAS] (caracteres) | Resposta final (caracteres) | Tokens de saída | Tokens de raciocínio nativo | [ETAPAS] presente | MAX_TOKENS | Novas tentativas |
|---|---|---|---|---|---|---|---|---|---|---|
| Tarefa 1 - Estruturação de seção de TCC | ChaTinho (com prompt de direcionamento) | 5 | 13,60 ± 1,99 (11,44–15,94) | 634 ± 156 (453–783) | 4734 ± 431 (4298–5368) | 1359 ± 135 (1260–1593) | 570 ± 55 (478–619) | 100% | 0 | 0 |
| Tarefa 1 - Estruturação de seção de TCC | Gemini padrão (sem prompt de direcionamento) | 5 | 28,04 ± 20,77 (14,67–62,97) | 0 ± 0 (0–0) | 5423 ± 780 (4845–6770) | 1422 ± 176 (1314–1735) | 939 ± 69 (831–1018) | 0% | 0 | 4 |
| Tarefa 2 - Análise multimodal de PDF | ChaTinho (com prompt de direcionamento) | 5 | 19,18 ± 14,59 (10,10–44,94) | 487 ± 108 (340–644) | 3895 ± 498 (3228–4489) | 1308 ± 137 (1119–1426) | 621 ± 107 (545–697) | 100% | 0 | 0 |
| Tarefa 2 - Análise multimodal de PDF | Gemini padrão (sem prompt de direcionamento) | 5 | 11,90 ± 5,23 (6,75–18,98) | 0 ± 0 (0–0) | 2496 ± 412 (1851–2850) | 727 ± 104 (554–797) | - | 0% | 0 | 41 |
| Tarefa 3 - Self-Attention, CoT e 4 referências ABNT | ChaTinho (com prompt de direcionamento) | 5 | 11,96 ± 1,86 (10,44–15,19) | 630 ± 102 (485–747) | 4896 ± 457 (4441–5546) | 1518 ± 142 (1355–1723) | 755 ± 121 (671–894) | 100% | 0 | 0 |
| Tarefa 3 - Self-Attention, CoT e 4 referências ABNT | Gemini padrão (sem prompt de direcionamento) | 5 | 19,18 ± 16,93 (10,51–49,43) | 0 ± 0 (0–0) | 4249 ± 216 (3961–4543) | 1175 ± 72 (1096–1290) | 1199 ± 188 (1016–1481) | 0% | 0 | 0 |

## Configuração (idêntica nas duas condições)

- temperature: 1.0 · top_p: 0.95 · top_k: 64
- max_output_tokens: 8192 · thinking_level: low · candidate_count: 1
- seed: não definida · safety_settings: padrão do serviço · system_instruction: não utilizado
- prompt do ChaTinho concatenado à mensagem do usuário · conversa nova a cada execução
- Python 3.14.3 · google-genai 3.2.0
