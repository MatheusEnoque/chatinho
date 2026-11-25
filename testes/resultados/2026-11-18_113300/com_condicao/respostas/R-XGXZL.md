# R-XGXZL | Tarefa 3 - Self-Attention, CoT e 4 referências ABNT | Gemini padrão (sem prompt de direcionamento) | repetição 5

- Data: 25/11/2026 · início 08:40:01 · fim 08:40:12
- Tempo de resposta: 11.28 s · tentativas: 1
- finish_reason: STOP · modelo: gemini-3.6-flash
- Conversa nova, sem histórico. Prompt do usuário: Explique o mecanismo de auto-atenção (Self-Attention) e a técnica Chain-of-Thought, e indique quatro referências bibliográficas sobre esses temas no formato ABNT.

## Resposta integral

Aqui está uma explicação detalhada dos dois conceitos, seguida por quatro referências bibliográficas formatadas segundo as normas da ABNT.

---

### 1. Mecanismo de Auto-Atenção (Self-Attention)

O mecanismo de **Auto-Atenção** (introduzido no modelo *Transformer* em 2017) é uma técnica que permite a uma rede neural ponderar a importância de diferentes palavras (ou tokens) em uma sequência em relação umas às outras, independentemente da distância em que se encontram no texto.

*   **Como funciona:** Antes da auto-atenção, modelos como RNNs e LSTMs processavam o texto sequencialmente (palavra por palavra), o que dificultava a retenção de contexto em frases longas. A auto-atenção calcula a relação de cada palavra com todas as outras palavras da mesma frase simultaneamente.
*   **Queries, Keys e Values (Q, K, V):** O mecanismo projeta cada token em três vetores:
    *   **Query ($Q$):** O que o token atual está "procurando".
    *   **Key ($K$):** O "rótulo" do token para saber se ele é relevante para a consulta.
    *   **Value ($V$):** O conteúdo da informação do token.
    O modelo calcula uma pontuação multiplicando a *Query* de uma palavra pelas *Keys* de todas as outras. As pontuações passam por uma função *Softmax* para virarem probabilidades (pesos) e são multiplicadas pelos *Values*, gerando uma representação rica em contexto.
*   **Exemplo:** Na frase *"O animal não atravessou a rua porque **ele** estava cansado"*, a auto-atenção permite que o modelo aprenda matematicamente que o pronome **"ele"** se refere a "animal" e não a "rua".

---

### 2. Técnica Chain-of-Thought (Cadeia de Pensamento - CoT)

A técnica **Chain-of-Thought (CoT)** é uma estratégia de engenharia de prompt usada para melhorar a capacidade de raciocínio lógico, matemático e simbólico de Grandes Modelos de Linguagem (LLMs).

*   **Como funciona:** Em vez de pedir que o modelo forneça diretamente a resposta final a um problema complexo, a instrução (prompt) o induz a gerar uma **sequência de etapas intermediárias de raciocínio** antes de chegar à conclusão.
*   **Modalidades principais:**
    *   **Few-Shot CoT:** O usuário fornece alguns exemplos no prompt mostrando a pergunta, o passo a passo da resolução e a resposta final.
    *   **Zero-Shot CoT:** O usuário simplesmente adiciona uma frase encorajadora ao prompt final, como *"Vamos pensar passo a passo"* ("Let's think step by step"), o que ativa a capacidade do modelo de decompor o problema.
*   **Importância:** Reduz erros de cálculo e alucinações em tarefas complexas, pois força a arquitetura autorregressiva a "desdobrar" a lógica em tokens intermediários, servindo como uma memória de trabalho temporária.

---

### Referências Bibliográficas (Normas ABNT)

1.  **VASWANI**, Ashish et al. Attention is all you need. *In*: **Advances in Neural Information Processing Systems** (NeurIPS 30), 2017, Long Beach. *Anais...* Long Beach: NIPS, 2017. p. 5998–6008.
    *(Artigo seminal que introduziu a arquitetura Transformer e o mecanismo de Self-Attention).*

2.  **WEI**, Jason et al. Chain-of-thought prompting elicits reasoning in large language models. *In*: **Advances in Neural Information Processing Systems** (NeurIPS 35), 2022, New Orleans. *Anais...* New Orleans: NeurIPS, 2022. p. 24824-24837.
    *(Artigo original que formalizou e demonstrou a eficácia da técnica Chain-of-Thought).*

3.  **KOJIMA**, Takeshi et al. Large language models are zero-shot reasoners. *In*: **Advances in Neural Information Processing Systems** (NeurIPS 35), 2022, New Orleans. *Anais...* New Orleans: NeurIPS, 2022. p. 22199-22213.
    *(Artigo que introduziu o conceito de Zero-Shot Chain-of-Thought usando a instrução "Let's think step by step").*

4.  **DEVLIN**, Jacob et al. BERT: Pre-training of deep bidirectional transformers for language understanding. *In*: **Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics** (NAACL-HLT), 2019, Minneapolis. *Anais...* Minneapolis: ACL, 2019. p. 4171–4186.
    *(Artigo que popularizou o uso de blocos de auto-atenção bidirecionais no processamento de linguagem natural).*
