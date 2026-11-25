# R-TVZMT | Tarefa 1 - Estruturação de seção de TCC | Gemini padrão (sem prompt de direcionamento) | repetição 3

- Data: 24/11/2026 · início 21:51:00 · fim 21:51:15
- Tempo de resposta: 15.25 s · tentativas: 1
- finish_reason: STOP · modelo: gemini-3.6-flash
- Conversa nova, sem histórico. Prompt do usuário: Preciso de um guia estruturado para redigir a justificativa e os objetivos (geral e específicos) do meu TCC em Ciência da Computação, cujo tema é um assistente virtual acadêmico.

## Resposta integral

Aqui está um guia prático e estruturado, projetado especificamente para a área de Ciência da Computação, para ajudar você a redigir a **Justificativa** e os **Objetivos** do seu TCC sobre um **Assistente Virtual Acadêmico**.

---

# PARTE 1: Justificativa

A justificativa responde à pergunta: **"Por que este trabalho é importante e deve ser feito?"** 
Na Ciência da Computação, uma boa justificativa aborda o problema sob **três pilares**: Prático/Social, Técnico e Acadêmico.

### Estrutura em 4 Parágrafos (Roteiro):

1. **Parágrafo 1: Contextualização do Problema (O Cenário)**
   * *O que abordar:* A dificuldade que os alunos enfrentam para encontrar informações acadêmicas (horários, ementas, prazos, secretarias) que costumam estar espalhadas em sistemas legados, PDFs ou sites institucionais complexos.
   * *Termos-chave:* Sobrecarga de informação, descentralização de dados, burocracia acadêmica.

2. **Parágrafo 2: A Solução Tecnológica (O "Porquê da Computação")**
   * *O que abordar:* Como a inteligência artificial, o Processamento de Linguagem Natural (PLN) e os modelos de linguagem (LLMs ou Chatbots) podem resolver esse problema.
   * *Termos-chave:* Atendimento 24/7, automação de respostas, interfaces conversacionais, acessibilidade.

3. **Parágrafo 3: Relevância Prática e Impacto**
   * *O que abordar:* Quem ganha com isso? Os alunos (respostas rápidas e centralizadas) e a gestão universitária/professores (redução de chamados repetitivos na secretaria).

4. **Parágrafo 4: Contribuição do Trabalho (O Diferencial)**
   * *O que abordar:* O que o *seu* projeto traz de novo ou de específico (ex: uso de uma arquitetura RAG, integração com o Moodle/WhatsApp, um modelo focado na sua instituição).

---

### Exemplo Rascunho de Justificativa:

> *"No contexto universitário atual, o acesso rápido e eficiente a informações acadêmicas — como datas de provas, ementas de disciplinas e procedimentos administrativos — é um desafio recorrente para os estudantes. Frequentemente, esses dados estão espalhados em diferentes portais, editais em PDF e sistemas de gestão acadêmica de difícil navegação, gerando ruídos na comunicação e sobrecarregando as secretarias acadêmicas com demandas repetitivas.*
>
> *Diante desse cenário, a aplicação de técnicas de Ciência da Computação, especificamente o Processamento de Linguagem Natural (PLN) e assistentes virtuais, surge como uma solução viável e promissora. Um assistente virtual é capaz de centralizar a base de conhecimento institucional e responder a dúvidas em tempo real, utilizando linguagem natural e acessível.*
>
> *A justificativa deste trabalho fundamenta-se na melhoria da experiência do estudante, promovendo a retenção de alunos e reduzindo o tempo de resposta para dúvidas frequentes. Sob a perspectiva técnica, o projeto se justifica pelo desafio de implementar [ex: uma arquitetura baseada em RAG (Retrieval-Augmented Generation) / integração via API do Telegram], garantindo que o sistema forneça respostas precisas e evite alucinações de dados.*
>
> *Portanto, o desenvolvimento deste assistente virtual acadêmico contribui tanto para a otimização dos processos de comunicação institucional quanto para o estudo prático de engenharia de software e inteligência artificial aplicadas ao ecossistema educacional."*

---

# PARTE 2: Objetivo Geral

O Objetivo Geral define a **entrega principal** do seu TCC. Ele deve ser escrito em **uma única frase**, iniciando com um **verbo no infinitivo** (Desenvolver, Construir, Implementar, Criar).

### Fórmula do Objetivo Geral:
> **[Verbo no Infinitivo]** + **[O que será feito/Sistema]** + **[Utilizando qual tecnologia/metodologia]** + **[Para qual finalidade/público]**.

### Exemplos:

* **Opção 1 (Foco em PLN/IA):**
  > *"Desenvolver um assistente virtual acadêmico baseado em Processamento de Linguagem Natural (PLN) e arquitetura RAG, capaz de responder a dúvidas frequentes de estudantes universitários sobre rotinas acadêmicas e ementas de cursos."*

* **Opção 2 (Foco em Integração/Engenharia de Software):**
  > *"Implementar um assistente virtual acadêmico integrado a plataformas de mensageria (como WhatsApp/Telegram), com o propósito de automatizar o atendimento ao aluno e centralizar o acesso a informações do sistema acadêmico."*

---

# PARTE 3: Objetivos Específicos

Os objetivos específicos representam o **passo a passo cronológico e técnico** para alcançar o objetivo geral. Eles costumam seguir o ciclo de vida de um projeto de software.

Use entre **4 e 6 tópicos**, organizados na ordem em que você executará o trabalho:

### Roteiro Padrão para Ciência da Computação:

1. **Fase 1: Levantamento e Pesquisa**
   * Mapear/Levantar as principais dúvidas e demandas dos estudantes e os requisitos do sistema.
   * Analisar o estado da arte e ferramentas existentes (frameworks de chatbot, LLMs, bancos de dados vetoriais).

2. **Fase 2: Dados e Modelagem/Arquitetura**
   * Coletar, tratar e estruturar a base de dados/conhecimento acadêmica (PDFs, FAQs, manuais).
   * Projetar a arquitetura do sistema (definir backend, banco de dados, APIs e interface).

3. **Fase 3: Desenvolvimento/Implementação**
   * Implementar o módulo de PLN/IA (treinamento, *prompt engineering* ou configuração de pipeline).
   * Desenvolver a interface de usuário (Web, aplicativo móvel ou bot de mensageria).

4. **Fase 4: Testes e Avaliação**
   * Avaliar a precisão das respostas do assistente por meio de métricas (ex: *Precision*, *Recall*, tempo de resposta) e/ou testes de usabilidade com alunos reais.

---

### Exemplo de Lista de Objetivos Específicos:

* **Mapear** os requisitos do sistema e as perguntas mais frequentes efetuadas pelos alunos na secretaria acadêmica;
* **Coletar e estruturar** a base de conhecimento institucional a partir dos documentos oficiais e regulamentos da universidade;
* **Projetar a arquitetura** do assistente virtual utilizando [mencionar tecnologias, ex: Python, Rasa, LangChain, OpenAI API];
* **Implementar** o protótipo do assistente virtual com integração a uma interface [ex: Web/Telegram];
* **Validar e avaliar** a acurácia das respostas do assistente e o nível de satisfação dos usuários através de testes funcionais e aplicação de questionários.

---

# Checklist Final para Revisão

Antes de entregar ao orientador, verifique:

- [ ] **Todos os verbos dos objetivos estão no infinitivo?** (Desenvolver, Mapear, Testar).
- [ ] **Os Objetivos Específicos não são "metas genéricas"?** (Evite objetivos como "Aprender Python" ou "Estudar IA". Foque em entregáveis do projeto).
- [ ] **A Justificativa deixa claro a relevância da COMPUTACIONAL do projeto?** (Certifique-se de ter mencionado algoritmos, dados, integração ou arquitetura de software, e não apenas o benefício educacional).
