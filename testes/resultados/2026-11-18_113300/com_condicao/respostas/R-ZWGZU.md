# R-ZWGZU | Tarefa 1 - Estruturação de seção de TCC | Gemini padrão (sem prompt de direcionamento) | repetição 4

- Data: 24/11/2026 · início 21:53:19 · fim 21:53:34
- Tempo de resposta: 14.67 s · tentativas: 1
- finish_reason: STOP · modelo: gemini-3.6-flash
- Conversa nova, sem histórico. Prompt do usuário: Preciso de um guia estruturado para redigir a justificativa e os objetivos (geral e específicos) do meu TCC em Ciência da Computação, cujo tema é um assistente virtual acadêmico.

## Resposta integral

Aqui está um guia prático e estruturado para você redigir a **Justificativa** e os **Objetivos** do seu TCC em Ciência da Computação.

---

# PARTE 1: Justificativa (O "Porquê?")

A justificativa deve convencer a banca de que seu projeto resolve um **problema real**, é **relevante** para a Ciência da Computação e traz **benefícios** para a comunidade acadêmica.

### Estrutura em 4 Parágrafos (Fórmula Prática):

1. **Contextualização e Problema:**
   * *O que falar:* Fale sobre a alta demanda de dúvidas recorrentes de alunos (prazos, ementas, procedimentos) e como as secretarias/coordenações ficam sobrecarregadas ou têm atendimento limitado ao horário comercial.
2. **Impacto e Motivação:**
   * *O que falar:* A frustração dos alunos com a demora nas respostas e a perda de eficiência da equipe acadêmica, que gasta tempo respondendo perguntas repetitivas em vez de focar em tarefas complexas.
3. **Relevância Técnica (Computacional):**
   * *O que falar:* Como a Ciência da Computação resolve isso hoje (IA, Processamento de Linguagem Natural - PLN, Chatbots, Arquitetura RAG/LLMs ou Engenharia de Software). Mostre que é um tema atual e viável.
4. **Contribuição Esperada:**
   * *O que falar:* O que a instituição ou a área ganha com a sua solução (ex: atendimento 24/7, redução de filas, base de conhecimento centralizada).

> **Exemplo de trecho para a Justificativa:**
> *"Na rotina universitária, a busca por informações acadêmicas gera um alto volume de chamados repetitivos às secretarias. Com o avanço do Processamento de Linguagem Natural (PLN) e das arquiteturas modernas de IA, torna-se viável a criação de um assistente virtual capaz de interpretar a intenção do estudante e fornecer respostas precisas instantaneamente. Justifica-se este trabalho, portanto, pela oportunidade de aplicar técnicas avançadas de [sua tecnologia: ex: LLMs / Rasa / Python] para otimizar a comunicação institucional, reduzindo a carga operacional dos servidores e oferecendo aos discentes um canal de atendimento acessível 24 horas por dia."*

---

# PARTE 2: Objetivo Geral (O "O quê?")

O Objetivo Geral define a **entrega principal** do seu TCC. Deve ser **apenas uma frase**, clara e direta, começando com um **verbo no infinitivo**.

### Fórmula do Objetivo Geral:
> **[Verbo no Infinitivo]** + **[O que você vai criar]** + **[Tecnologia/Abordagem]** + **[Para qual finalidade]**.

### Exemplos para o seu tema:
* **Opção 1 (Foco em IA/PLN):**
  > "Desenvolver um assistente virtual acadêmico baseado em Processamento de Linguagem Natural para automatizar o atendimento a dúvidas frequentes de estudantes de graduação."
* **Opção 2 (Foco em LLM / RAG):**
  > "Implementar um assistente virtual para suporte acadêmico utilizando a arquitetura RAG (*Retrieval-Augmented Generation*) integrando a base de dados do curso de Ciência da Computação."

---

# PARTE 3: Objetivos Específicos (O "Como?")

Os Objetivos Específicos são o **passo a passo lógico/tecnológico** necessário para alcançar o Objetivo Geral. Em Ciência da Computação, eles costumam seguir o ciclo de vida do desenvolvimento de software.

Separe em **3 a 5 itens**, todos iniciando com **verbos no infinitivo**.

### Roteiro Padrão para TCC de Computação:

1. **Fase de Levantamento/Dados (Requisitos):**
   * *Exemplo:* **Mapear** os requisitos do sistema e as principais dúvidas recorrentes dos alunos (consultando secretarias, formulários ou histórico de e-mails).
2. **Fase de Modelagem/Dados:**
   * *Exemplo:* **Estruturar** a base de conhecimento acadêmica (editais, matrizes curriculares, calendários) e os modelos de Intenções/Entidades para o processamento de texto.
3. **Fase de Desenvolvimento/Integração:**
   * *Exemplo:* **Implementar** o assistente virtual utilizando o *framework* [Ex: Rasa, Dialogflow, LangChain/OpenAI] e integrar à interface de usuário [Ex: Telegram, Web, WhatsApp].
4. **Fase de Testes e Validação:**
   * *Exemplo:* **Avaliar** o desempenho do assistente em termos de acurácia das respostas e usabilidade, por meio de testes com uma amostra de estudantes e secretários.

---

# Dicas de Ouro para a Redação Acadêmica

### 1. Verbos Recomendados (Ttaxonomia de Bloom para TCCs):
* **Para a Investigação:** *Mapear, Identificar, Coletar, Analisar.*
* **Para a Criação/Engenharia:** *Projetar, Modelar, Implementar, Desenvolver, Construir, Integrar.*
* **Para a Avaliação:** *Testar, Validar, Avaliar, Comparar, Mensurar.*

### 2. Erros Comuns para EVITAR:
* ❌ **Não confundir objetivo com metodologia:** Evite colocar "Fazer revisão bibliográfica sobre Chatbots" como objetivo específico. A revisão é um meio/metodologia, não um resultado técnico do produto.
* ❌ **Não ser vago:** Evite termos como "Melhorar a faculdade". Prefira "Otimizar o tempo de resposta a solicitações discentes".
* ❌ **Prometer o impossível:** Não coloque objetivos que você não terá tempo de testar (ex: "Instalar o bot em todas as universidades do Brasil"). Restrinja ao escopo do seu protótipo/estudo de caso.
