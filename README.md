# ChaTinho 🤖 | Consultor Inteligente

Assistente acadêmico desenvolvido com **Streamlit** e a API **Google Gemini** (SDK `google-genai`) como parte de um Trabalho de Conclusão de Curso em Ciência da Computação. O app tem conversas salvas localmente, envio de anexos (PDF, imagem, texto), geração de imagens com o comando `/imagem` (Pollinations AI, modelo Flux), três temas visuais e a seção "Etapas verificadas", que separa da resposta final os critérios usados pelo modelo.

> **Aviso de privacidade:** as mensagens e os anexos são enviados a serviços externos (Google Gemini e Pollinations). Não envie dados pessoais, informações sigilosas nem trabalhos ainda não publicados.

---

## Versões utilizadas

| Componente | Versão |
|---|---|
| Python | 3.14.3 (ambiente dos testes de novembro de 2026) |
| google-genai | 3.2.0 |
| Streamlit | 1.67.0 |
| requests | 2.34.2 |
| python-dotenv | 1.2.4 |
| Modelo padrão | `gemini-3.6-flash` (opções: `gemini-3.5-flash`, `gemini-3.8-flash`) |

As versões das bibliotecas estão fixadas em `requirements.txt`.

---

## Instalação

1. Tenha o Python instalado e uma chave de API do Gemini, gerada no [Google AI Studio](https://aistudio.google.com/).
2. Clone o repositório e instale as dependências:

   ```bash
   git clone https://github.com/MatheusEnoque/chatinho.git
   cd chatinho
   pip install -r requirements.txt
   ```

3. Copie o arquivo de exemplo e coloque sua chave no `.env`:

   ```bash
   copy .env.example .env
   ```

   ```env
   GEMINI_API_KEY=sua_chave_aqui
   ```

   O `.env` está no `.gitignore` e não deve ser enviado ao repositório.

## Execução

```bash
streamlit run main.py
```

O app abre no navegador em `http://localhost:8501`.

---

## Configuração do modelo

Os parâmetros de geração e a instrução de sistema ficam em `config_modelo.py`, compartilhado pelo app e pelos testes:

| Parâmetro | Valor |
|---|---|
| temperature | 1.0 |
| top_p | 0.95 |
| top_k | 64 |
| max_output_tokens | 8192 |
| thinking_level | low |
| candidate_count | 1 |
| seed | não definida (parâmetro não enviado) |
| safety_settings | padrão do serviço (parâmetro não enviado) |
| system_instruction | não utilizado: a instrução vai concatenada à mensagem do usuário |

---

## Testes do TCC

| Arquivo | Função |
|---|---|
| `testes/tarefas.json` | Textos das três tarefas padronizadas |
| `testes/executar_testes.py` | Bateria comparativa: 5 respostas válidas por tarefa com e sem a instrução de sistema, mesmos parâmetros, conversa nova a cada execução |
| `testes/avaliacao_cega.py` | Gera os arquivos da avaliação cega: respostas sem a condição e sem o bloco [ETAPAS] |
| `testes/retomar_bateria.py` | Retoma uma bateria pausada pela cota diária da API |
| `testes/verificacao_funcional_tabela5.csv` | Ficha da verificação funcional manual (CT01 a CT16) |

```bash
python testes/executar_testes.py --repeticoes 5 --pausa 10
python testes/executar_testes.py --continuar "testes/resultados/<data_hora>"
```

**PDF da Tarefa 2:** o arquivo `Modelo de TCC-Monografia.pdf` (modelo de TCC da UFAC, 20 páginas) não está no repositório, por ser material de terceiros. Para repetir a Tarefa 2, coloque o arquivo em `Referencia de documentos TCC/Modelo de TCC-Monografia.pdf`. O `configuracao.json` de cada bateria registra o tamanho e o SHA-256 do arquivo usado, para conferir se é o mesmo.

Os resultados ficam em `testes/resultados/<data_hora>/`. No plano gratuito da API, a cota diária de requisições pode exigir que a bateria seja concluída em mais de um dia.

---

## Limitações

- **Sem contexto entre mensagens:** cada envio vai ao modelo sem o histórico da conversa, então o modelo não lembra o que foi dito antes.
- **"Etapas verificadas" não é verificável:** a seção é texto gerado pelo modelo a pedido da instrução de sistema. Ela não mostra o raciocínio real e não garante que a resposta esteja correta.
- **Referências bibliográficas:** o modelo pode errar a formatação ABNT ou citar obras inexistentes. Confira sempre as fontes.
- **Anexos não são persistidos:** os arquivos enviados não são salvos com a conversa. Arquivos .docx não são suportados.
- **Pastas de conversa duplicadas:** a pasta da conversa é nomeada pelo título, e a mudança de "Nova conversa" para o título gerado cria uma segunda pasta.
- **Geração de imagem:** depende do serviço externo Pollinations. Nos testes, a imagem veio em 768 × 768 px, embora o app peça 1024 × 1024.
- **Sem criptografia em repouso:** conversas e imagens ficam em texto e arquivos comuns nas pastas `Conversas/` e `Downloads/`.
- **Limites da API:** no plano gratuito, as cotas por minuto e por dia geram erros 429.
- **O que os testes não medem:** os testes do TCC mostram diferenças entre as respostas, mas não medem aprendizagem, plágio nem produtividade.

---

## Licença

Distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE).
