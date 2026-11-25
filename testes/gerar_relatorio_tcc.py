"""Gera a pasta relatorio_tcc/ com os dados da bateria para o TCC.

Todos os valores são lidos dos arquivos do projeto (código, configuracao.json,
execucoes.json). Nada é estimado: o que não existe aparece como
"NÃO ENCONTRADO", com o local onde foi procurado.

Uso (na raiz do repositório):
    python testes/gerar_relatorio_tcc.py [testes/resultados/<data_hora>]

Os arquivos da pasta relatorio_tcc/APOS_AVALIACAO_CEGA/ ligam cada código à
condição: só devem ser abertos depois da avaliação cega.
"""
import csv
import json
import platform
import random
import statistics
import struct
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from importlib import metadata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from config_modelo import PARAMETROS_GERACAO, SYSTEM_PROMPT, criar_config  # noqa: E402

PASTA_PADRAO = RAIZ / "testes" / "resultados" / "2026-11-18_113300"
SAIDA = RAIZ / "relatorio_tcc"
CEGA = SAIDA / "APOS_AVALIACAO_CEGA"
COPIA_PRIVADA = RAIZ.parent / "my_chat_bot"   # onde o CT09 foi executado
NF = "NÃO ENCONTRADO"
COND = {"chatinho": "com prompt de direcionamento", "padrao": "sem prompt de direcionamento"}
TAREFA_CURTA = {"tarefa1": "Tarefa 1", "tarefa2": "Tarefa 2", "tarefa3": "Tarefa 3"}


# ---------------------------------------------------------------- utilidades
def br(v, casas=2):
    if v is None:
        return "—"
    if isinstance(v, int):
        return f"{v:,}".replace(",", ".")
    s = f"{v:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def linha(arquivo, trecho):
    """Número da linha (1-based) em que o trecho aparece pela primeira vez."""
    caminho = RAIZ / arquivo
    for i, l in enumerate(caminho.read_text(encoding="utf-8").splitlines(), 1):
        if trecho in l:
            return f"{arquivo}:{i}"
    return f"{arquivo} ({NF}: '{trecho}')"


def dims_jpeg(caminho):
    b = caminho.read_bytes()
    i = 2
    while i < len(b) - 9:
        if b[i] != 0xFF:
            return None
        marcador, tam = b[i + 1], struct.unpack(">H", b[i + 2:i + 4])[0]
        if marcador in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", b[i + 5:i + 9])
            return w, h
        i += 2 + tam
    return None


def media_dp(valores, casas=2):
    v = [x for x in valores if x is not None]
    if not v:
        return "—"
    if len(v) == 1:
        return f"{br(float(v[0]), casas)} (n = 1, sem desvio-padrão)"
    return f"{br(statistics.mean(v), casas)} ± {br(statistics.stdev(v), casas)}"


def escrever(caminho, texto):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto.rstrip() + "\n", encoding="utf-8")


# ---------------------------------------------------------------- leitura
def carregar(pasta):
    conf = json.loads((pasta / "configuracao.json").read_text(encoding="utf-8"))
    dados = json.loads((pasta / "com_condicao" / "execucoes.json").read_text(encoding="utf-8"))
    return conf, dados["execucoes"], dados["tentativas"]


def sessao_de(instante_iso, sessoes):
    t = datetime.fromisoformat(instante_iso)
    for n, s in enumerate(sessoes, 1):
        ini = datetime.fromisoformat(s["inicio"])
        fim = datetime.fromisoformat(s["fim"]) if s.get("fim") else datetime.max
        if ini <= t <= fim:
            return n
    return None


def sessoes_de(conf):
    return conf.get("sessoes") or [{"inicio": conf["data_inicio"], "fim": conf.get("data_fim"),
                                     "interrompida": conf.get("interrompida")}]


def id_exec(r):
    return f"{r['tarefa']}_{r['condicao']}_rep{r['repeticao']}"


# ---------------------------------------------------------------- 1
def gerar_configuracao(pasta, conf, rel):
    p = PARAMETROS_GERACAO
    enviado = conf.get("config_enviada_api", {})
    cfg_atual = criar_config().model_dump(exclude_none=True, mode="json")
    meta = conf.get("metadados_modelo_api", {})
    amb = conf.get("ambiente", {})
    sessoes = sessoes_de(conf)
    linhas_cfg = [
        ("temperature", enviado.get("temperature"), linha("config_modelo.py", '"temperature"')),
        ("top_p", enviado.get("top_p"), linha("config_modelo.py", '"top_p"')),
        ("top_k", enviado.get("top_k"), linha("config_modelo.py", '"top_k"')),
        ("max_output_tokens", enviado.get("max_output_tokens"), linha("config_modelo.py", '"max_output_tokens"')),
        ("thinking_level", (enviado.get("thinking_config") or {}).get("thinking_level"),
         linha("config_modelo.py", '"thinking_level"')),
        ("include_thoughts", (enviado.get("thinking_config") or {}).get("include_thoughts"),
         linha("config_modelo.py", '"include_thoughts"')),
        ("candidate_count", enviado.get("candidate_count"), linha("config_modelo.py", '"candidate_count"')),
    ]
    t = [f"# Configuração da bateria de testes", "",
         f"Gerado em {datetime.now():%d/%m/%Y %H:%M} por `testes/gerar_relatorio_tcc.py`. "
         f"Fonte principal: `{rel}/configuracao.json`, campo `config_enviada_api` (cópia exata do objeto "
         f"`GenerateContentConfig` enviado, produzida por `criar_config()` em {linha('config_modelo.py', 'def criar_config')}).", "",
         "## Parâmetros enviados no GenerateContentConfig", "",
         "| Parâmetro | Valor enviado | Fonte |", "|---|---|---|"]
    for nome, valor, fonte in linhas_cfg:
        if isinstance(valor, float) and valor.is_integer() and nome == "top_k":
            v = f"{int(valor)} (o SDK registra como {valor})"
        else:
            v = str(valor).replace(".", ",") if isinstance(valor, float) else str(valor)
        t.append(f"| {nome} | {v} | `configuracao.json` → config_enviada_api; definido em `{fonte}` |")
    for nome, chave in (("seed", "seed"), ("safety_settings", "safety_settings"),
                        ("system_instruction", "system_instruction")):
        presente = chave in enviado
        t.append(f"| {nome} | {'enviado: ' + str(enviado[chave]) if presente else 'não enviado (ausente do objeto enviado)'} | "
                 f"`configuracao.json` → config_enviada_api; `{linha('config_modelo.py', chr(34) + chave + chr(34)) if chave != 'system_instruction' else linha('config_modelo.py', 'def montar_prompt_chatinho')}` |")
    t += ["", f"- **safety_settings:** como o parâmetro não é enviado, vale o padrão do serviço (`configuracao.json` → `safety_settings`: “{conf.get('safety_settings', NF)}”).",
          f"- **system_instruction:** não usado. O prompt de direcionamento é concatenado à mensagem do usuário por `montar_prompt_chatinho()` ({linha('config_modelo.py', 'def montar_prompt_chatinho')}). "
          f"`configuracao.json` → `system_instruction_utilizado` = {conf.get('system_instruction_utilizado', NF)}.",
          f"- **Conferência:** a configuração gerada hoje pelo código atual é {'idêntica' if cfg_atual == enviado else 'DIFERENTE'} à registrada na bateria.", "",
          "## Modelo", "",
          "| Item | Valor | Fonte |", "|---|---|---|",
          f"| Identificador solicitado | `{conf.get('modelo_solicitado', NF)}` | `configuracao.json` → modelo_solicitado; `{linha('config_modelo.py', 'MODELO_PADRAO =')}` |",
          f"| Nome na API | `{meta.get('name', NF)}` | `configuracao.json` → metadados_modelo_api.name |",
          f"| Versão informada pela API | `{meta.get('version', NF)}` | `configuracao.json` → metadados_modelo_api.version |",
          f"| Versão que respondeu (model_version) | ver `execucoes.csv` após a avaliação cega | `com_condicao/execucoes.json` → model_version |", "",
          "## Versões do ambiente", "",
          "| Componente | Versão registrada na bateria | Versão instalada hoje | requirements.txt |", "|---|---|---|---|"]
    req = {}
    for l in (RAIZ / "requirements.txt").read_text(encoding="utf-8").splitlines():
        if "==" in l:
            a, b = l.split("==")
            req[a.strip()] = b.strip()
    def inst(pkg):
        try:
            return metadata.version(pkg)
        except metadata.PackageNotFoundError:
            return NF
    t.append(f"| Python | {amb.get('python', NF)} | {platform.python_version()} | — |")
    for pkg in ("google-genai", "streamlit", "python-dotenv", "requests"):
        t.append(f"| {pkg} | {amb.get(pkg, NF + ' (não registrado em configuracao.json → ambiente)')} | {inst(pkg)} | {req.get(pkg, NF)} |")
    t.append(f"| Sistema operacional | {amb.get('sistema', NF)} | {platform.platform()} | — |")
    t += ["", "O `configuracao.json` guarda o ambiente da sessão mais recente (é regravado a cada retomada). "
          "As sessões rodaram no mesmo computador. O `requests` não é usado pela bateria, só pelo comando /imagem do app.", "",
          "## Sessões de execução", "",
          "| Sessão | Data | Início | Fim | Como terminou | Fonte |", "|---|---|---|---|---|---|"]
    for n, s in enumerate(sessoes, 1):
        ini = datetime.fromisoformat(s["inicio"])
        fim = datetime.fromisoformat(s["fim"]) if s.get("fim") else None
        motivo = s.get("interrompida") or "concluída"
        t.append(f"| {n} | {ini:%d/%m/%Y} | {ini:%H:%M:%S} | {fim.strftime('%H:%M:%S') if fim else NF} | {motivo} | `configuracao.json` → sessoes[{n - 1}] |")
    datas = {datetime.fromisoformat(s["inicio"]).strftime("%d/%m/%Y") for s in sessoes}
    if "25/11/2026" not in datas:
        t += ["", f"- **25/11/2026:** {NF}. Nenhuma sessão nessa data em `configuracao.json` → sessoes (procurado em {datetime.now():%d/%m/%Y %H:%M})."]
    escrever(SAIDA / "configuracao.md", "\n".join(t))


# ---------------------------------------------------------------- 2
def gerar_protocolo(pasta, conf, execs, tentativas, rel):
    semente = conf.get("semente_sorteio_ordem")
    reps = conf["respostas_validas_por_tarefa_e_condicao"]
    tarefas = list(conf["tarefas"])
    rng = random.Random(semente)
    plano = []
    for rep in range(1, reps + 1):
        for tk in tarefas:
            conds = list(conf["condicoes"])
            rng.shuffle(conds)
            plano += [(tk, c, rep) for c in conds]
    validas = {(r["tarefa"], r["condicao"], r["repeticao"]): r for r in execs}
    confere = all(validas[k]["ordem_global"] == i for i, k in enumerate(plano, 1) if k in validas)
    ids_validos = {id_exec(r) for r in execs}
    pendentes = sorted({x["execucao"] for x in tentativas} - ids_validos)
    t = ["# Protocolo da bateria", "",
         "## Sorteio da ordem das execuções", "",
         f"- **Função:** `random.Random(semente)` ({linha('testes/executar_testes.py', 'rng = random.Random(semente_ordem)')}). "
         f"Para cada repetição (1 a {reps}) e cada tarefa, nessa ordem, a lista das duas condições é embaralhada com `rng.shuffle` "
         f"({linha('testes/executar_testes.py', 'rng.shuffle(conds)')}). Tarefas e repetições seguem ordem fixa; só a ordem das duas condições dentro de cada par é sorteada.",
         f"- **Semente:** {semente} (`{rel}/configuracao.json` → semente_sorteio_ordem). Foi sorteada com `random.randrange(1_000_000)` "
         f"({linha('testes/executar_testes.py', 'random.randrange(1_000_000)')}) no início da 1ª sessão e reaproveitada nas retomadas "
         f"({linha('testes/executar_testes.py', 'semente_ordem = anterior[')}).",
         f"- **Conferência:** a ordem reconstruída com essa semente {'coincide' if confere else 'NÃO coincide'} com o campo `ordem_global` das respostas válidas em `com_condicao/execucoes.json`.", "",
         "| Posição | Tarefa | Condição | Repetição | Situação |", "|---|---|---|---|---|"]
    for i, (tk, c, rep) in enumerate(plano, 1):
        k = (tk, c, rep)
        if k in validas:
            sit = f"válida ({validas[k]['data']})"
        elif f"{tk}_{c}_rep{rep}" in pendentes:
            sit = "pendente (iniciada, sem resposta válida)"
        else:
            sit = "ainda não executada"
        t.append(f"| {i} | {TAREFA_CURTA.get(tk, tk)} | {COND[c]} | {rep} | {sit} |")
    t += ["", "Os códigos aleatórios não aparecem aqui, para não revelar a condição de cada código antes da avaliação cega.", "",
          "## Recusas da API e retomada", "",
          f"- **Pausa entre execuções:** 10 s (`--pausa`, {linha('testes/executar_testes.py', 'add_argument("--pausa"')}; `configuracao.json` → pausa_entre_chamadas_s = {br(conf['pausa_entre_chamadas_s'], 0) if 'pausa_entre_chamadas_s' in conf else NF}).",
          f"- **Limite de tentativas por execução e por sessão:** 40 (`--max-tentativas`, {linha('testes/executar_testes.py', 'add_argument("--max-tentativas"')}).",
          f"- **Intervalo entre tentativas:** 30 s × número da tentativa na sessão, com máximo de 300 s (`--espera-max`, {linha('testes/executar_testes.py', 'espera = min(30')}; {linha('testes/executar_testes.py', 'add_argument("--espera-max"')}).",
          f"- **Erros repetidos:** códigos e mensagens temporários listados em `ERROS_TEMPORARIOS` ({linha('testes/executar_testes.py', 'ERROS_TEMPORARIOS =')}) e resposta vazia ({linha('testes/executar_testes.py', 'raise RuntimeError(\"resposta vazia\")')}). Outros erros interrompem a bateria.",
          f"- **Cota diária:** um 429 com a mensagem de limite diário (“per day”) pausa a bateria em vez de repetir ({linha('testes/executar_testes.py', 'cota_diaria =')}; classe `CotaDiariaEsgotada`, {linha('testes/executar_testes.py', 'class CotaDiariaEsgotada')}).",
          f"- **Retomada:** `--continuar <pasta>` relê as respostas válidas e as tentativas registradas, pula as execuções que já têm resposta válida ({linha('testes/executar_testes.py', 'if (t, cond, rep) in feitas')}) e continua a primeira sem resposta. "
          f"As tentativas recusadas de sessões anteriores são somadas às da execução retomada ({linha('testes/executar_testes.py', 'anteriores = [l for l in log_tentativas')}). "
          f"A retomada é recusada se parâmetros, prompt, tarefas ou PDF mudarem ({linha('testes/executar_testes.py', 'for chave in (\"parametros_geracao\"')}).",
          "- **Tempo de resposta:** mede só a tentativa que deu certo, sem as esperas (`time.perf_counter()` em `chamar_ate_valida`, "
          f"{linha('testes/executar_testes.py', 'def chamar_ate_valida')}).", "",
          "### Diferença entre as sessões", "",
          "A 1ª sessão (18/11/2026) rodou com uma versão anterior do script, que não estava versionada e não tinha a detecção de cota diária: "
          "erros 429 de cota diária eram tratados como temporários e repetidos. O comportamento está nos registros de `com_condicao/tentativas.csv`:"]
    for n, s in enumerate(sessoes_de(conf), 1):
        ts = [x for x in tentativas if sessao_de(x["inicio"], sessoes_de(conf)) == n]
        esperas = Counter(int(float(x.get("espera_depois_s") or 0)) for x in ts)
        t.append(f"- Sessão {n}: {len(ts)} tentativas; esperas registradas (s → quantidade): "
                 + ", ".join(f"{k} → {v}" for k, v in sorted(esperas.items())) + f"; motivo do fim: {s.get('interrompida') or 'concluída'}.")
    t += ["- Da 2ª sessão em diante vale a versão atual do script, descrita acima.", "",
          "### Execuções repetidas ou descartadas", "",
          "- Nenhuma resposta válida foi descartada nem refeita. Cada combinação tarefa × condição × repetição tem no máximo uma resposta válida "
          "(chave única em `com_condicao/execucoes.json`).",
          "- Execução retomada entre sessões: "
          + (", ".join(f"`{x}`" for x in sorted({x['execucao'] for x in tentativas if x['resultado'] != 'ok'
                                                    and any(id_exec(r) == x['execucao'] and r['data'] != datetime.fromisoformat(x['inicio']).strftime('%d/%m/%Y') for r in execs)}))
             or "nenhuma")
          + " (recusada em uma sessão e respondida em outra; as recusas entram na contagem).",
          f"- Execuções iniciadas e ainda sem resposta válida: {', '.join(f'`{x}`' for x in pendentes) or 'nenhuma'}.",
          f"- Respostas vazias registradas: {sum('vazia' in x['resultado'] for x in tentativas)}.", "",
          "## Avaliação cega", "",
          f"- **Códigos:** cada resposta válida recebe um código `R-` seguido de 5 caracteres sorteados com `secrets.choice` do alfabeto `ALFABETO_CODIGO` "
          f"({linha('testes/executar_testes.py', 'ALFABETO_CODIGO =')}), sem 0/O e 1/I e sem repetição (`gerar_codigo`, {linha('testes/executar_testes.py', 'def gerar_codigo')}).",
          f"- **Remoção de [ETAPAS]:** `avaliacao_cega.gerar()` ({linha('testes/avaliacao_cega.py', 'def gerar')}) aplica `separar_etapas()` "
          f"({linha('config_modelo.py', 'def separar_etapas')}), que remove o trecho entre `[ETAPAS]` e `[/ETAPAS]` com a expressão regular de {linha('config_modelo.py', '_RE_ETAPAS =')}. "
          f"O script avisa se sobrar menção a “Etapas verificadas” fora das marcas ({linha('testes/avaliacao_cega.py', '_RESTO_ETAPAS =')}).",
          f"- **Ordem:** as respostas são embaralhadas com uma semente aleatória nova a cada geração ({linha('testes/avaliacao_cega.py', 'shuffle(embaralhadas)')}).",
          "- **Arquivos:** `avaliacao_cega/respostas_cegas.md` (sem condição e sem [ETAPAS]) e uma ficha por autor. "
          "A chave código → condição fica em `com_condicao/chave_codigos.csv`.",
          "- O bloco [ETAPAS] é mantido em `com_condicao/` e no Apêndice C."]
    escrever(SAIDA / "protocolo.md", "\n".join(t))


# ---------------------------------------------------------------- 4
def gerar_falhas(conf, execs, tentativas, rel):
    sessoes = sessoes_de(conf)
    por = defaultdict(Counter)
    for x in tentativas:
        if x["resultado"] == "ok":
            continue
        cod = x["resultado"].split(":")[0].replace("erro ", "").strip()
        por[(sessao_de(x["inicio"], sessoes), x["execucao"])][cod] += 1
    t = ["# Tentativas recusadas pela API", "",
         f"Fonte: `{rel}/com_condicao/tentativas.csv` (uma linha por tentativa; resultado diferente de “ok” = recusa). "
         "Sessão atribuída pelo horário da tentativa em relação a `configuracao.json` → sessoes.", "",
         "A coluna “Execução” usa o identificador `tarefa_condição_repetição` registrado em tentativas.csv. "
         "O código aleatório da resposta (R-…) não aparece aqui para não revelar a condição antes da avaliação cega.", "",
         "| Sessão | Execução | Tarefa | Condição | Erros 503 | Erros 429 | Outros | Total |", "|---|---|---|---|---|---|---|---|"]
    tot = Counter()
    for n in range(1, len(sessoes) + 1):
        sub = Counter()
        for (s, ex), c in sorted(por.items()):
            if s != n:
                continue
            tk, cond, _ = ex.split("_")
            outros = sum(v for k, v in c.items() if k not in ("503", "429"))
            t.append(f"| {n} ({datetime.fromisoformat(sessoes[n - 1]['inicio']):%d/%m/%Y}) | `{ex}` | {TAREFA_CURTA.get(tk, tk)} | {COND.get(cond, cond)} | "
                     f"{c['503']} | {c['429']} | {outros} | {sum(c.values())} |")
            sub.update(c)
        t.append(f"| **Subtotal sessão {n}** | | | | **{sub['503']}** | **{sub['429']}** | **{sum(v for k, v in sub.items() if k not in ('503', '429'))}** | **{sum(sub.values())}** |")
        tot.update(sub)
    total = sum(tot.values())
    t.append(f"| **Total geral** | | | | **{tot['503']}** | **{tot['429']}** | **{sum(v for k, v in tot.items() if k not in ('503', '429'))}** | **{total}** |")
    confirma = total == 45 and tot["503"] == 16 and tot["429"] == 29
    t += ["", f"**Conferência do total 45 (16 × 503 e 29 × 429):** {'CONFIRMADO' if confirma else 'NÃO CONFERE'} — total {total} ({tot['503']} × 503, {tot['429']} × 429).", "",
          "- 503 (UNAVAILABLE): sobrecarga temporária do serviço (“This model is currently experiencing high demand”).",
          "- 429 (RESOURCE_EXHAUSTED): limite de requisições do plano gratuito (20 por dia para o gemini-3.6-flash).",
          f"- Tentativas registradas no total, incluindo as bem-sucedidas: {len(tentativas)}."]
    escrever(SAIDA / "falhas.md", "\n".join(t))


# ---------------------------------------------------------------- 5
def gerar_ct09():
    img = COPIA_PRIVADA / "Downloads" / "IA_113239.jpg"
    conv = sorted((COPIA_PRIVADA / "Conversas").glob("4ce4ed9b-b54e-402e-931d-3cfcf55c0762_*")) \
        if (COPIA_PRIVADA / "Conversas").exists() else []
    ficha = RAIZ / "testes" / "verificacao_funcional_tabela5.csv"
    reg = {}
    with open(ficha, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f, delimiter=";"):
            if r["ct"] == "CT09":
                reg = r
    dims = dims_jpeg(img) if img.exists() else None
    t = ["# CT09 – Comando /imagem", "",
         "| Item | Resultado | Fonte |", "|---|---|---|",
         f"| Data e hora | {reg.get('data_hora') or NF} | `testes/verificacao_funcional_tabela5.csv`, linha CT09 |",
         f"| Como foi executado | {reg.get('responsavel') or NF} | idem |",
         "| Prompt | /imagem arvore do conhecimento feita de livros luminosos em uma biblioteca | `testes/tarefas.json` → imagem |",
         f"| Tempo | 6,32 s (do envio do comando até o fim do processamento no app) | registrado em `verificacao_funcional_tabela5.csv` → resultado_obtido no momento do teste; não há outro log desse tempo |",
         f"| Resolução recebida | {f'{dims[0]} × {dims[1]} px' if dims else NF} | lida agora do cabeçalho JPEG de `{img}` |",
         f"| Tamanho do arquivo | {br(img.stat().st_size) + ' bytes' if img.exists() else NF} | `{img}` |",
         f"| Imagem gravada em | `Downloads/IA_113239.jpg` e `Conversas/<pasta da conversa>/Imagens/IA_113239.jpg` | `main.py` (`filename_dn`, {linha('main.py', 'filename_dn = ')}; `filename_cv`, {linha('main.py', 'filename_cv = ')}) |",
         f"| Pastas da conversa | " + ("; ".join(f"`Conversas/{p.name}`" for p in conv) if conv else NF + f" (procurado em {COPIA_PRIVADA / 'Conversas'})") + " | cópia local privada (pasta `Conversas/` não vai para o repositório) |",
         f"| Situação | {reg.get('situacao') or NF} | `verificacao_funcional_tabela5.csv` |", "",
         "O teste foi feito em 18/11/2026 na cópia local privada (`my_chat_bot`), antes da criação do repositório público. "
         "O trecho do comando /imagem é idêntico no `main.py` do repositório público.", "",
         "## Causa provável da resolução 768 × 768", "",
         f"- O app pede 1024 × 1024 na URL do serviço (`width=1024&height=1024`, {linha('main.py', 'width=1024')}).",
         f"- O app grava os bytes recebidos sem redimensionar (`requests.get(image_url).content` gravado direto em arquivo, {linha('main.py', 'img_data = requests.get')}).",
         "- Portanto a redução para 768 × 768 aconteceu no serviço Pollinations AI, e não no código do ChaTinho.",
         f"- A razão exata do serviço: {NF}. Não há registro da resposta HTTP (cabeçalhos) no projeto, e a documentação do serviço não foi consultada.", "",
         "## Causa da gravação da conversa em duas pastas", "",
         f"- A pasta da conversa é nomeada pelo identificador e pelo título: `f\"{{cid}}_{{titulo_limpo}}\"` (`salvar_historico`, {linha('main.py', 'pasta_path = os.path.join(CONVERSAS_DIR')}).",
         f"- A conversa nasce com o título “Nova conversa” e é salva imediatamente ({linha('main.py', 'def criar_nova_conversa')}; título em {linha('main.py', '\"titulo\": \"Nova conversa\"')}).",
         f"- Na primeira mensagem o título passa a ser o resumo do prompt ({linha('main.py', 'conv[\"titulo\"] = resumo')}) e a conversa é salva de novo ({linha('main.py', 'salvar_historico()')}), "
         "agora numa pasta com o novo nome. A pasta antiga não é apagada nem renomeada.",
         f"- Na reabertura, `carregar_historico` usa só o identificador (`pasta.split(\"_\")[0]`, {linha('main.py', 'cid = pasta.split')}), então as duas pastas disputam a mesma conversa e a última lida prevalece."]
    escrever(SAIDA / "ct09.md", "\n".join(t))


# ---------------------------------------------------------------- 6
def gerar_repositorio(rel):
    def git(*a):
        return subprocess.run(["git", *a], cwd=RAIZ, capture_output=True, text=True).stdout.strip()
    remoto = git("remote", "get-url", "origin") or NF
    head = git("rev-parse", "HEAD") or NF
    head_data = git("log", "-1", "--format=%cd", "--date=format:%d/%m/%Y %H:%M") or NF
    alterado = git("status", "--porcelain")
    publicados = git("ls-files").splitlines()
    t = ["# Repositório público", "",
         "| Item | Valor | Fonte |", "|---|---|---|",
         f"| URL | {remoto.removesuffix('.git')} | `git remote get-url origin` |",
         f"| Licença | MIT | arquivo `LICENSE` |",
         f"| Commit atual (HEAD) | `{head}` ({head_data}) | `git rev-parse HEAD` |",
         f"| Arquivos publicados | {len(publicados)} | `git ls-files` |", "",
         "**Versão do TCC:** o código do app e da bateria corresponde ao commit acima. "
         + ("Há alterações locais ainda não commitadas (resultados das sessões posteriores e este gerador); "
            "o hash definitivo da versão do TCC será o do commit feito depois da última sessão." if alterado else
            "Não há alterações locais pendentes."), "",
         "## Execução", "",
         "```bash", f"git clone {remoto}", "cd chatinho", "pip install -r requirements.txt",
         "copy .env.example .env      # colocar a chave em GEMINI_API_KEY", "streamlit run main.py", "```", "",
         "Bateria de testes:", "", "```bash", "python testes/executar_testes.py --repeticoes 5 --pausa 10",
         f"python testes/executar_testes.py --continuar \"{rel}\"", "```", "",
         "## O que ficou fora do repositório e por quê", "",
         "| Item | Motivo | Fonte |", "|---|---|---|",
         "| `.env` | contém a chave da API | `.gitignore` |",
         "| `.streamlit/secrets.toml` | segredos do Streamlit | `.gitignore` |",
         "| `Conversas/`, `historico_conversas.json` | conversas locais do usuário | `.gitignore` |",
         "| `Downloads/` | imagens geradas localmente | `.gitignore` |",
         "| `Referencia de documentos TCC/` (inclui o PDF da Tarefa 2) | material de terceiros; o README explica onde colocar o PDF e o `configuracao.json` registra o SHA-256 | `.gitignore`; `README.md` |",
         "| `Meu TCC/`, `TCC/` | documentos do TCC e dados pessoais | `.gitignore` |",
         "| `Apostila_ChatBot.pdf` | material de terceiros | `.gitignore` |",
         "| `.agents/` | atalho local com caminho de pasta do usuário | `.gitignore` |",
         "| `*.zip` | pacotes locais, repetem dados já versionados | `.gitignore` |",
         "| Histórico do repositório privado anterior | continha documentos de terceiros e pessoais | repositório criado do zero |", "",
         f"**Respostas brutas:** {'estão no repositório' if any('com_condicao/respostas/' in p for p in publicados) else NF}, "
         f"em `{rel}/com_condicao/respostas/` e no `apendice_c_respostas.md`, junto com as medidas e o registro de tentativas."]
    escrever(SAIDA / "repositorio.md", "\n".join(t))


# ---------------------------------------------------------------- 7
def gerar_pos_avaliacao(conf, execs, tarefas_def, rel):
    sessoes = sessoes_de(conf)
    campos = ["codigo", "tarefa", "condicao", "repeticao", "sessao", "data", "hora_inicio", "tempo_s",
              "etapas_chars", "resposta_chars", "finish_reason", "model_version", "tentativas_recusadas_antes"]
    ordenadas = sorted(execs, key=lambda r: (r["tarefa"], r["condicao"], r["repeticao"]))
    CEGA.mkdir(parents=True, exist_ok=True)
    with open(CEGA / "execucoes.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(campos)
        for r in ordenadas:
            n = sessao_de(f"{datetime.strptime(r['data'], '%d/%m/%Y'):%Y-%m-%d}T{r['hora_inicio']}", sessoes)
            w.writerow([r["codigo"], TAREFA_CURTA[r["tarefa"]], COND[r["condicao"]], r["repeticao"], n, r["data"],
                        r["hora_inicio"], br(r["tempo_s"]), r["etapas_chars"], r["resposta_chars"],
                        r["finish_reason"], r["model_version"], r["novas_tentativas"]])

    def tabela(grupo_filtro, titulo):
        out = [f"### {titulo}", "",
               "| Tarefa | Condição | n | Tempo (s) | [ETAPAS] (caracteres) | Resposta final (caracteres) | [ETAPAS] presente | finish_reason STOP |",
               "|---|---|---|---|---|---|---|---|"]
        for tk in conf["tarefas"]:
            for c in COND:
                g = [r for r in execs if r["tarefa"] == tk and r["condicao"] == c and grupo_filtro(r)]
                if not g:
                    out.append(f"| {TAREFA_CURTA[tk]} | {COND[c]} | 0 | — | — | — | — | — |")
                    continue
                et = [r["etapas_chars"] for r in g if r["etapas_presente"]]
                out.append(f"| {TAREFA_CURTA[tk]} | {COND[c]} | {len(g)} | {media_dp([r['tempo_s'] for r in g])} | "
                           f"{media_dp(et, 0) if et else '—'} | {media_dp([r['resposta_chars'] for r in g], 0)} | "
                           f"{sum(r['etapas_presente'] for r in g)}/{len(g)} | {sum(r['finish_reason'] == 'STOP' for r in g)}/{len(g)} |")
        return out
    previstas = conf["respostas_validas_por_tarefa_e_condicao"] * len(conf["tarefas"]) * len(conf["condicoes"])
    t = ["# Médias por tarefa e condição", "",
         f"Fonte: `{rel}/com_condicao/execucoes.json`. Desvio-padrão amostral (`statistics.stdev`). "
         f"Respostas válidas: {len(execs)} de {previstas}.", ""]
    if len(execs) < previstas:
        t += [f"**Resultados parciais:** faltam {previstas - len(execs)} respostas. Gere de novo depois da última sessão.", ""]
    t += tabela(lambda r: True, "Todas as sessões") + [""]
    t += tabela(lambda r: r["data"] != "18/11/2026", "Sem as execuções de 18/11/2026 (API sobrecarregada)") + [""]
    t += ["“[ETAPAS] (caracteres)” considera só as respostas em que o bloco apareceu."]
    escrever(CEGA / "medias.md", "\n".join(t))

    a = ["# Apêndice C – Respostas integrais", "",
         "Cada execução foi feita em conversa nova, sem histórico. Na condição com prompt de direcionamento, "
         "o texto do Apêndice A foi enviado na mesma mensagem que o prompt do usuário. Respostas transcritas sem alteração, incluindo o bloco [ETAPAS].", ""]
    for tk in conf["tarefas"]:
        td = tarefas_def[tk]
        a += [f"## {td['nome']}", "", f"**Prompt do usuário:** {td['prompt']}", ""]
        if td.get("anexo"):
            a += [f"**Anexo:** {Path(td['anexo']).name}", ""]
        for r in [x for x in ordenadas if x["tarefa"] == tk]:
            a += [f"### {r['codigo']} – {COND[r['condicao']]}, repetição {r['repeticao']}", "",
                  f"Data: {r['data']}, {r['hora_inicio']}–{r['hora_fim']} · tempo {br(r['tempo_s'])} s · finish_reason {r['finish_reason']} · modelo {r['model_version']}", "",
                  r["texto_integral"], ""]
    escrever(CEGA / "respostas_integrais.md", "\n".join(a))
    escrever(CEGA / "LEIA-ME.txt", "NÃO ABRIR ANTES DA AVALIAÇÃO CEGA.\nEstes arquivos ligam cada código à condição.")


def main():
    pasta = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else PASTA_PADRAO
    rel = pasta.relative_to(RAIZ).as_posix()
    conf, execs, tentativas = carregar(pasta)
    SAIDA.mkdir(parents=True, exist_ok=True)
    # Texto literal, byte a byte, sem quebra de linha acrescentada no final.
    (SAIDA / "prompt_direcionamento.txt").write_bytes(conf.get("system_prompt", NF).encode("utf-8"))
    if conf.get("system_prompt") != SYSTEM_PROMPT:
        print("ATENÇÃO: o prompt registrado na bateria difere do config_modelo.py atual.")
    gerar_configuracao(pasta, conf, rel)
    gerar_protocolo(pasta, conf, execs, tentativas, rel)
    gerar_falhas(conf, execs, tentativas, rel)
    gerar_ct09()
    gerar_repositorio(rel)
    gerar_pos_avaliacao(conf, execs, conf["tarefas"], rel)
    print(f"relatorio_tcc/ gerado com {len(execs)} respostas válidas.")


if __name__ == "__main__":
    main()
