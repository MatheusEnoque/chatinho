# R-GLDGR | Tarefa 3 - Self-Attention, CoT e 4 referências ABNT | Gemini padrão (sem prompt de direcionamento) | repetição 4

- Data: 25/11/2026 · início 08:36:15 · fim 08:37:05
- Tempo de resposta: 49.43 s · tentativas: 1
- finish_reason: STOP · modelo: gemini-3.6-flash
- Conversa nova, sem histórico. Prompt do usuário: Explique o mecanismo de auto-atenção (Self-Attention) e a técnica Chain-of-Thought, e indique quatro referências bibliográficas sobre esses temas no formato ABNT.

## Resposta integral

### 1. Mecanismo de Auto-Atenção (Self-Attention)

O mecanismo de **Auto-Atenção** (ou *Self-Attention*) é o componente fundamental da arquitetura *Transformer* (introduzida em 2017), que revolucionou o Processamento de Linguagem Natural (PLN). 

#### Como funciona:
Ao contrário de modelos sequenciais antigos (como RNNs e LSTMs), que processavam o texto palavra por palavra, a Auto-Atenção permite que o modelo processe todas as palavras de uma sequência simultaneamente e **calcule o grau de relação/relevância que cada palavra tem com todas as outras palavras da mesma frase**.

Matematicamente, o mecanismo mapeia uma sequência de entrada em três vetores para cada token (palavra ou subpalavra):
*   **Query (Q) / Consulta:** O que a palavra atual está procurando.
*   **Key (K) / Chave:** O rótulo ou identidade de cada palavra na frase.
*   **Value (V) / Valor:** A informação real contida na palavra.

O modelo calcula a pontuação de atenção fazendo o produto escalar entre a *Query* de uma palavra e as *Keys* de todas as outras palavras. O resultado passa por uma função *Softmax* para gerar pesos percentuais (que somam 1). Por fim, esses pesos multiplicam os vetores *Value*, gerando uma representação contextualizada da palavra.

*   **Exemplo prático:** Na frase *"O animal não atravessou a rua porque **ele** estava muito cansado"*, a Auto-Atenção permite que o algoritmo identifique matematicamente que a palavra **"ele"** refere-se a **"animal"** e não a **"rua"**, atribuindo um peso de atenção muito maior entre "ele" e "animal".

---

### 2. Técnica Chain-of-Thought (Cadeia de Pensamento)

A técnica **Chain-of-Thought (CoT)** é uma estratégia de engenharia de *prompt* (instrução) utilizada para melhorar a capacidade de raciocínio lógico e resolução de problemas complexos em Grandes Modelos de Linguagem (LLMs).

#### Como funciona:
Tradicionalmente, ao fazer uma pergunta complexa a um LLM, exige-se que ele responda diretamente (ex: "Entrada $\rightarrow$ Resposta"). A técnica CoT induz o modelo a **decompor o problema em etapas intermediárias de raciocínio** antes de chegar à resposta final (ex: "Entrada $\rightarrow$ Passo 1 de Raciocínio $\rightarrow$ Passo 2 $\rightarrow$ Resposta Final").

Existem duas abordagens principais:
1.  **Few-Shot CoT:** Fornecem-se ao modelo alguns exemplos no próprio prompt que mostram a pergunta, a explicação passo a passo da solução e a resposta.
2.  **Zero-Shot CoT:** Adiciona-se simplesmente uma frase indutora ao final do prompt, como *"Vamos pensar passo a passo"* (*"Let's think step by step"*).

#### Por que é eficaz?
Modelos de linguagem geram texto prevendo o próximo token probabilístico. Ao forçar o modelo a gerar os passos intermediários do raciocínio, ele aloca mais "tempo de processamento" (tokens) para estruturar a lógica, reduzindo alucinações e erros em tarefas matemáticas, de programação e de lógica formal.

---

### 3. Referências Bibliográficas (Norma ABNT)

Abaixo estão quatro referências de artigos científicos fundamentais sobre os temas, formatadas segundo a norma **ABNT NBR 6023**:

1.  DEVLIN, Jacob et al. BERT: Pre-training of deep bidirectional transformers for language understanding. *In*: ANNUAL MEETING OF THE ASSOCIATION FOR COMPUTATIONAL LINGUISTICS, 2019, Minneapolis. **Proceedings [...]**. Minneapolis: Association for Computational Linguistics, 2019. p. 4171–4186. *(Aplica o mecanismo de Auto-Atenção em larga escala)*.

2.  KOJIMA, Takeshi et al. Large language models are zero-shot reasoners. *In*: ADVANCES IN NEURAL INFORMATION PROCESSING SYSTEMS (NeurIPS), 35., 2022, New Orleans. **Proceedings [...]**. New Orleans: NeurIPS, 2022. p. 22199-22213. *(Introduz a técnica Zero-Shot Chain-of-Thought)*.

3.  VASWANI, Ashish et al. Attention is all you need. *In*: ADVANCES IN NEURAL INFORMATION PROCESSING SYSTEMS (NIPS), 30., 2017, Long Beach. **Proceedings [...]**. Long Beach: NIPS, 2017. p. 5998–6008. *(Artigo seminal que introduziu o mecanismo de Auto-Atenção e a arquitetura Transformer)*.

4.  WEI, Jason et al. Chain-of-thought prompting elicits reasoning in large language models. *In*: ADVANCES IN NEURAL INFORMATION PROCESSING SYSTEMS (NeurIPS), 35., 2022, New Orleans. **Proceedings [...]**. New Orleans: NeurIPS, 2022. p. 24824-24837. *(Artigo original que formalizou a técnica Chain-of-Thought)*.
