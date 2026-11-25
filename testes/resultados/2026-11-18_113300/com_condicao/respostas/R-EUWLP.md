# R-EUWLP | Tarefa 3 - Self-Attention, CoT e 4 referências ABNT | Gemini padrão (sem prompt de direcionamento) | repetição 2

- Data: 24/11/2026 · início 21:50:16 · fim 21:50:28
- Tempo de resposta: 12.11 s · tentativas: 1
- finish_reason: STOP · modelo: gemini-3.6-flash
- Conversa nova, sem histórico. Prompt do usuário: Explique o mecanismo de auto-atenção (Self-Attention) e a técnica Chain-of-Thought, e indique quatro referências bibliográficas sobre esses temas no formato ABNT.

## Resposta integral

Aqui está a explicação sobre o mecanismo de **Auto-Atenção (Self-Attention)** e a técnica **Chain-of-Thought (Cadeia de Pensamento)**, seguida das referências bibliográficas no padrão ABNT (NBR 6023).

---

### 1. Mecanismo de Auto-Atenção (Self-Attention)

O **Self-Attention** é um mecanismo fundamental da arquitetura *Transformer* (introduzida em 2017), responsável por revolucionar o Processamento de Linguagem Natural (PLN). 

**Como funciona:**
Em redes neurais tradicionais (como as RNNs), o texto é processado sequencialmente (palavra por palavra), o que gera dificuldades para manter o contexto em frases longas. O Self-Attention resolve isso ao permitir que a rede analise **todas as palavras de uma sequência simultaneamente** e atribua "pesos de importância" relacionando cada palavra às demais.

Matematicamente, o mecanismo transforma cada token de entrada em três vetores:
*   **Query ($Q$):** O que a palavra atual está buscando.
*   **Key ($K$):** O rótulo/conteúdo das outras palavras.
*   **Value ($V$):** A informação real contida na palavra.

A relevância (pontuação de atenção) é calculada pelo produto escalar entre a *Query* de uma palavra e as *Keys* de todas as outras, normalizada pela função *Softmax*. O resultado é multiplicado pelo *Value*, gerando uma representação contextualizada. Por exemplo, na frase *"O animal não atravessou a rua porque **ele** estava cansado"*, o Self-Attention permite que o modelo entenda matematicamente que a palavra **"ele"** se refere a **"animal"**, e não a "rua".

---

### 2. Técnica Chain-of-Thought (CoT / Cadeia de Pensamento)

O **Chain-of-Thought (CoT)** é uma técnica de engenharia de *prompt* projetada para melhorar a capacidade de raciocínio lógico e de resolução de problemas em Grandes Modelos de Linguagem (LLMs).

**Como funciona:**
Em vez de pedir diretamente ao modelo a resposta final para uma pergunta complexa (como um problema matemático ou um enigma lógico), o CoT induz o modelo a gerar uma **sequência de passos intermediários de raciocínio** antes de chegar à conclusão.

Existem duas abordagens principais:
1.  **Few-Shot CoT:** Fornecem-se ao modelo alguns exemplos no *prompt* que contêm a pergunta, o passo a passo da solução e a resposta final.
2.  **Zero-Shot CoT:** Adiciona-se uma instrução simples ao *prompt*, como *"Vamos pensar passo a passo"* (*"Let's think step by step"*).

Essa decomposição do problema reduz drasticamente os erros de alucinação e permite que o modelo distribua o esforço computacional ao longo do texto gerado, melhorando significativamente o desempenho em tarefas de raciocínio aritmético, simbólico e de senso comum.

---

### 3. Referências Bibliográficas (Formato ABNT)

1. **BAHDANAU, Dzmitry; CHO, Kyunghyun; BENGIO, Yoshua.** Neural machine translation by jointly learning to align and translate. *In*: INTERNATIONAL CONFERENCE ON LEARNING REPRESENTATIONS (ICLR), 3., 2015, San Diego. **Proceedings...** San Diego: ICLR, 2015. p. 1-15. *(Trabalho seminal que introduziu o conceito inicial de Atenção em PLN)*.

2. **KOJIMA, Takeshi et al.** Large language models are zero-shot reasoners. *In*: ADVANCES IN NEURAL INFORMATION PROCESSING SYSTEMS (NeurIPS), 35., 2022, New Orleans. **Proceedings...** New Orleans: NeurIPS, 2022. p. 22199-22213. *(Artigo fundamental sobre a técnica Zero-Shot Chain-of-Thought)*.

3. **VASWANI, Ashish et al.** Attention is all you need. *In*: ADVANCES IN NEURAL INFORMATION PROCESSING SYSTEMS (NIPS), 30., 2017, Long Beach. **Proceedings...** Long Beach: NIPS, 2017. p. 5998–6008. *(O artigo histórico que introduziu a arquitetura Transformer e o mecanismo de Self-Attention)*.

4. **WEI, Jason et al.** Chain-of-thought prompting elicits reasoning in large language models. *In*: ADVANCES IN NEURAL INFORMATION PROCESSING SYSTEMS (NeurIPS), 35., 2022, New Orleans. **Proceedings...** New Orleans: NeurIPS, 2022. p. 24824-24837. *(Artigo original que formalizou e nomeou a técnica Chain-of-Thought)*.
