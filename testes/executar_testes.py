"""Bateria de testes repetidos do ChaTinho (TCC).

Executa cada tarefa até obter N respostas válidas (padrão: 5) em cada condição:
  - chatinho : prompt do usuário concatenado ao SYSTEM_PROMPT na mesma mensagem,
               exatamente como no main.py (o campo system_instruction NÃO é usado)
  - padrao   : mesmo modelo, mesmo prompt do usuário, sem SYSTEM_PROMPT

As duas condições usam a mesma configuração de geração (config_modelo.py).
Cada chamada é uma conversa nova, sem histórico.

Falhas temporárias da API (429/500/503) são repetidas até a resposta válida.
O tempo de resposta mede só a tentativa que deu certo (sem as esperas), e
todas as tentativas ficam registradas em com_condicao/tentativas.csv.

Cada resposta recebe um código aleatório. A pasta avaliacao_cega/ traz as
respostas sem o nome da condição e sem o bloco [ETAPAS] (removido conforme a
seção 3.4 do TCC), em ordem embaralhada, para a avaliação independente pelos
autores. A chave código -> condição fica em com_condicao/.

Uso (na raiz do projeto):
    python testes/executar_testes.py
    python testes/executar_testes.py --repeticoes 5 --pausa 10
"""
import argparse
import csv
import hashlib
import json
import os
import platform
import random
import secrets
import statistics
import sys
import time
from datetime import datetime
from importlib import metadata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from dotenv import load_dotenv  # noqa: E402
from google import genai  # noqa: E402
from google.genai import types  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import avaliacao_cega  # noqa: E402
from config_modelo import (  # noqa: E402
    MODELO_PADRAO,
    PARAMETROS_GERACAO,
    SYSTEM_PROMPT,
    criar_config,
    montar_prompt_chatinho,
    separar_etapas,
)

CONDICOES = {
    "chatinho": "ChaTinho (com prompt de direcionamento)",
    "padrao": "Gemini padrão (sem prompt de direcionamento)",
}
MIME_MAP = {"pdf": "application/pdf", "txt": "text/plain", "png": "image/png",
            "jpg": "image/jpeg", "jpeg": "image/jpeg"}
ERROS_TEMPORARIOS = ("429", "500", "503", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "INTERNAL",
                     "DEADLINE_EXCEEDED", "timed out", "Timeout", "ConnectError", "RemoteProtocolError")
ALFABETO_CODIGO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # sem 0/O, 1/I

CAMPOS_EXECUCAO = [
    "codigo", "tarefa", "condicao", "repeticao", "ordem_global",
    "data", "hora_inicio", "hora_fim", "tempo_s",
    "tentativas", "novas_tentativas", "erros_nas_tentativas", "espera_total_s",
    "finish_reason", "cortada_max_tokens", "model_version",
    "tokens_entrada", "tokens_saida", "tokens_raciocinio", "tokens_total",
    "etapas_presente", "etapas_chars", "resposta_chars", "texto_integral_chars",
    "arquivo_resposta",
]


def versao(pacote):
    try:
        return metadata.version(pacote)
    except metadata.PackageNotFoundError:
        return None


def sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(65536), b""):
            h.update(bloco)
    return h.hexdigest()


def num_br(v, casas=2):
    """Número no formato brasileiro (vírgula decimal) para o CSV/Excel."""
    if v is None or v == "":
        return ""
    if isinstance(v, bool):
        return "sim" if v else "não"
    if isinstance(v, float):
        return f"{v:.{casas}f}".replace(".", ",")
    return str(v)


def gerar_codigo(usados):
    while True:
        c = "R-" + "".join(secrets.choice(ALFABETO_CODIGO) for _ in range(5))
        if c not in usados:
            usados.add(c)
            return c


def codigo_erro(msg):
    for c in ("429", "500", "503", "504", "400", "403", "404"):
        if c in msg:
            return c
    return msg.split(".")[0][:40]


class CotaDiariaEsgotada(RuntimeError):
    """Cota diária do plano gratuito esgotada: só volta no dia seguinte."""


def chamar_ate_valida(client, modelo, parts, log_tentativas, id_exec, max_tentativas, espera_max):
    """Repete a chamada até obter uma resposta válida.

    Retorna (resposta, tempo_s, inicio, fim, tentativas, erros, espera_total).
    O tempo mede só a tentativa bem-sucedida. As tentativas feitas em sessões
    anteriores (bateria retomada) entram na contagem. Erros não temporários
    (ex.: 400) e a cota diária esgotada interrompem a bateria.
    """
    anteriores = [l for l in log_tentativas if l["execucao"] == id_exec]
    erros = [l["resultado"].split(":")[0].replace("erro ", "") for l in anteriores]
    espera_total = float(sum(float(l.get("espera_depois_s") or 0) for l in anteriores))
    for tentativa in range(len(anteriores) + 1, len(anteriores) + max_tentativas + 1):
        inicio = datetime.now()
        t0 = time.perf_counter()
        try:
            res = client.models.generate_content(
                model=modelo,
                contents=[types.Content(role="user", parts=parts)],
                config=criar_config(),
            )
            dt, fim = time.perf_counter() - t0, datetime.now()
            if not (res.text or "").strip():
                raise RuntimeError("resposta vazia")
            log_tentativas.append({"execucao": id_exec, "tentativa": tentativa,
                                   "inicio": inicio.isoformat(timespec="seconds"),
                                   "fim": fim.isoformat(timespec="seconds"),
                                   "resultado": "ok", "espera_depois_s": 0})
            return res, dt, inicio, fim, tentativa, erros, espera_total
        except Exception as e:  # noqa: BLE001
            fim, msg = datetime.now(), str(e)
            cota_diaria = "per day" in msg.lower() or "perday" in msg.lower()
            temporario = not cota_diaria and (msg == "resposta vazia" or any(c in msg for c in ERROS_TEMPORARIOS))
            n_sessao = tentativa - len(anteriores)
            espera = min(30 * n_sessao, espera_max) if temporario else 0
            erros.append(codigo_erro(msg))
            log_tentativas.append({"execucao": id_exec, "tentativa": tentativa,
                                   "inicio": inicio.isoformat(timespec="seconds"),
                                   "fim": fim.isoformat(timespec="seconds"),
                                   "resultado": f"erro {codigo_erro(msg)}: {msg[:200]}",
                                   "espera_depois_s": espera})
            if cota_diaria:
                raise CotaDiariaEsgotada(f"cota diária da API esgotada em {id_exec}") from e
            if not temporario:
                raise RuntimeError(f"Erro não temporário em {id_exec}: {msg}") from e
            print(f"      tentativa {tentativa}: erro {codigo_erro(msg)}, nova tentativa em {espera}s")
            time.sleep(espera)
            espera_total += espera
    raise RuntimeError(f"{id_exec}: sem resposta válida após {max_tentativas} tentativas")


def resumir(valores):
    v = [x for x in valores if isinstance(x, (int, float)) and not isinstance(x, bool)]
    if not v:
        return {"media": None, "dp": None, "min": None, "max": None, "mediana": None}
    return {"media": statistics.mean(v), "dp": statistics.stdev(v) if len(v) > 1 else 0.0,
            "min": min(v), "max": max(v), "mediana": statistics.median(v)}


def escrever_csv(caminho, campos, linhas):
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=campos, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for l in linhas:
            w.writerow({k: num_br(l.get(k)) for k in campos})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repeticoes", type=int, default=5, help="respostas válidas por tarefa e condição")
    ap.add_argument("--tarefas", default="tarefa1,tarefa2,tarefa3")
    ap.add_argument("--pausa", type=float, default=10.0, help="segundos entre chamadas")
    ap.add_argument("--max-tentativas", type=int, default=40, help="limite de tentativas por execução")
    ap.add_argument("--espera-max", type=float, default=300.0, help="espera máxima entre tentativas (s)")
    ap.add_argument("--modelo", default=MODELO_PADRAO)
    ap.add_argument("--semente-ordem", type=int, default=None,
                    help="semente do sorteio da ordem das condições (registrada no resultado)")
    ap.add_argument("--continuar", metavar="PASTA", default=None,
                    help="retoma uma bateria interrompida (ex.: cota diária), na mesma pasta e ordem")
    args = ap.parse_args()

    load_dotenv(RAIZ / ".env")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        sys.exit("GEMINI_API_KEY não encontrada no arquivo .env")
    client = genai.Client(api_key=api_key)

    tarefas_def = json.loads((Path(__file__).parent / "tarefas.json").read_text(encoding="utf-8"))
    tarefas = [t.strip() for t in args.tarefas.split(",") if t.strip()]
    for t in tarefas:
        if t not in tarefas_def or not tarefas_def[t].get("prompt") or t == "imagem":
            sys.exit(f"Tarefa desconhecida: {t}")

    inicio_sessao = datetime.now()
    anterior = None
    if args.continuar:
        pasta = Path(args.continuar).resolve()
        anterior = json.loads((pasta / "configuracao.json").read_text(encoding="utf-8"))
        semente_ordem = anterior["semente_sorteio_ordem"]
        args.repeticoes = anterior["respostas_validas_por_tarefa_e_condicao"]
        tarefas = list(anterior["tarefas"])
        if args.modelo != anterior["modelo_solicitado"]:
            sys.exit("Modelo diferente do usado na bateria original.")
    else:
        semente_ordem = args.semente_ordem if args.semente_ordem is not None else random.randrange(1_000_000)
        pasta = Path(__file__).parent / "resultados" / inicio_sessao.strftime("%Y-%m-%d_%H%M%S")
    rng = random.Random(semente_ordem)
    inicio_bateria = datetime.fromisoformat(anterior["data_inicio"]) if anterior else inicio_sessao
    pasta_id = pasta / "com_condicao"
    (pasta_id / "respostas").mkdir(parents=True, exist_ok=True)

    # ---------- Registro das configurações ----------
    try:
        m = client.models.get(model=args.modelo)
        meta_modelo = {k: getattr(m, k, None) for k in (
            "name", "version", "display_name", "input_token_limit", "output_token_limit",
            "temperature", "max_temperature", "top_p", "top_k", "thinking")}
    except Exception as e:  # noqa: BLE001
        meta_modelo = {"erro": str(e)}

    anexos = {}
    for t in tarefas:
        a = tarefas_def[t].get("anexo")
        if a:
            caminho = RAIZ / a
            anexos[t] = {"arquivo": a, "bytes": caminho.stat().st_size, "sha256": sha256(caminho)}

    config_api = criar_config().model_dump(exclude_none=True, mode="json")
    configuracao = {
        "data_inicio": inicio_bateria.isoformat(timespec="seconds"),
        "respostas_validas_por_tarefa_e_condicao": args.repeticoes,
        "condicoes": CONDICOES,
        "diferenca_entre_condicoes": "Somente o texto enviado: na condição 'chatinho' o SYSTEM_PROMPT é "
                                     "concatenado ao prompt do usuário na mesma mensagem (como no main.py); "
                                     "na condição 'padrao' é enviado apenas o prompt do usuário. O campo "
                                     "system_instruction não é utilizado. Modelo e parâmetros são idênticos.",
        "system_instruction_utilizado": "system_instruction" in config_api,
        "conversa": "nova a cada execução, sem histórico",
        "ordem_das_condicoes": "sorteada a cada repetição/tarefa",
        "semente_sorteio_ordem": semente_ordem,
        "pausa_entre_chamadas_s": args.pausa,
        "politica_de_falhas": f"erros temporários (429/500/503) repetidos até a resposta válida, "
                              f"espera de 30 s × nº da tentativa (máx. {args.espera_max:.0f} s), "
                              f"até {args.max_tentativas} tentativas; o tempo mede só a tentativa válida",
        "modelo_solicitado": args.modelo,
        "metadados_modelo_api": meta_modelo,
        "parametros_geracao": PARAMETROS_GERACAO,
        "config_enviada_api": config_api,
        "safety_settings": "não enviado: vale o padrão do serviço",
        "system_prompt": SYSTEM_PROMPT,
        "tarefas": {t: tarefas_def[t] for t in tarefas},
        "anexos": anexos,
        "ambiente": {
            "python": platform.python_version(),
            "sistema": platform.platform(),
            "google-genai": versao("google-genai"),
            "streamlit": versao("streamlit"),
            "python-dotenv": versao("python-dotenv"),
        },
    }
    assert not configuracao["system_instruction_utilizado"], "system_instruction não deve ser usado"

    registros, log_tentativas, sessoes = [], [], []
    if anterior:
        # A retomada só é válida se nada que afete as respostas mudou.
        for chave in ("parametros_geracao", "config_enviada_api", "system_prompt", "tarefas", "anexos"):
            if json.dumps(anterior.get(chave), sort_keys=True, default=str) != \
                    json.dumps(configuracao[chave], sort_keys=True, default=str):
                sys.exit(f"Não é possível continuar: '{chave}' mudou desde o início da bateria.")
        configuracao["data_inicio"] = anterior["data_inicio"]
        configuracao["metadados_modelo_api"] = anterior.get("metadados_modelo_api", meta_modelo)
        sessoes = anterior.get("sessoes") or [{"inicio": anterior["data_inicio"], "fim": anterior.get("data_fim"),
                                               "interrompida": anterior.get("interrompida")}]
        salvo = json.loads((pasta_id / "execucoes.json").read_text(encoding="utf-8"))
        registros, log_tentativas = salvo["execucoes"], salvo["tentativas"]
    sessoes.append({"inicio": inicio_sessao.isoformat(timespec="seconds"), "fim": None, "interrompida": None})
    configuracao["sessoes"] = sessoes

    def salvar_estado():
        (pasta_id / "execucoes.json").write_text(
            json.dumps({"execucoes": registros, "tentativas": log_tentativas}, ensure_ascii=False, indent=2),
            encoding="utf-8")
        (pasta / "configuracao.json").write_text(
            json.dumps(configuracao, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    # ---------- Execução ----------
    plano = []
    for rep in range(1, args.repeticoes + 1):
        for t in tarefas:
            conds = list(CONDICOES)
            rng.shuffle(conds)
            plano += [(t, c, rep) for c in conds]

    total = len(plano)
    feitas = {(r["tarefa"], r["condicao"], r["repeticao"]) for r in registros}
    codigos = {r["codigo"] for r in registros}
    print(f"Modelo: {args.modelo} | {total} respostas válidas a obter ({len(feitas)} já obtidas) | "
          f"resultados em {pasta}")
    salvar_estado()
    interrompida = None
    for i, (t, cond, rep) in enumerate(plano, 1):
        if (t, cond, rep) in feitas:
            continue
        tdef = tarefas_def[t]
        texto = montar_prompt_chatinho(tdef["prompt"]) if cond == "chatinho" else tdef["prompt"]
        parts = []
        if tdef.get("anexo"):
            caminho = RAIZ / tdef["anexo"]
            mime = MIME_MAP.get(caminho.suffix.lower().lstrip("."), "application/octet-stream")
            parts.append(types.Part(inline_data=types.Blob(mime_type=mime, data=caminho.read_bytes())))
        parts.append(types.Part(text=texto))

        id_exec = f"{t}_{cond}_rep{rep}"
        print(f"[{i}/{total}] {t} | {cond} | repetição {rep}")
        try:
            res, tempo, dh_ini, dh_fim, tentativas, erros, espera = chamar_ate_valida(
                client, args.modelo, parts, log_tentativas, id_exec, args.max_tentativas, args.espera_max)
        except CotaDiariaEsgotada as e:
            interrompida = str(e)
            print(f"      BATERIA PAUSADA: {e}. Continue amanhã com:\n"
                  f"      python testes/executar_testes.py --continuar \"{pasta}\"")
            break
        except RuntimeError as e:
            interrompida = str(e)
            print(f"      BATERIA INTERROMPIDA: {e}")
            break

        bruto = res.text
        etapas, final = separar_etapas(bruto)
        u = res.usage_metadata
        fr = res.candidates[0].finish_reason if res.candidates else None
        fr = getattr(fr, "value", fr)
        codigo = gerar_codigo(codigos)
        reg = {
            "codigo": codigo, "tarefa": t, "condicao": cond, "repeticao": rep, "ordem_global": i,
            "data": dh_ini.strftime("%d/%m/%Y"), "hora_inicio": dh_ini.strftime("%H:%M:%S"),
            "hora_fim": dh_fim.strftime("%H:%M:%S"), "tempo_s": tempo,
            "tentativas": tentativas, "novas_tentativas": tentativas - 1,
            "erros_nas_tentativas": ", ".join(erros), "espera_total_s": espera,
            "finish_reason": fr, "cortada_max_tokens": fr == "MAX_TOKENS",
            "model_version": res.model_version,
            "tokens_entrada": u.prompt_token_count if u else None,
            "tokens_saida": u.candidates_token_count if u else None,
            "tokens_raciocinio": u.thoughts_token_count if u else None,
            "tokens_total": u.total_token_count if u else None,
            "etapas_presente": bool(etapas), "etapas_chars": len(etapas),
            "resposta_chars": len(final), "texto_integral_chars": len(bruto),
            "arquivo_resposta": f"respostas/{codigo}.md", "texto_integral": bruto,
        }
        (pasta_id / "respostas" / f"{codigo}.md").write_text(
            f"# {codigo} | {tdef['nome']} | {CONDICOES[cond]} | repetição {rep}\n\n"
            f"- Data: {reg['data']} · início {reg['hora_inicio']} · fim {reg['hora_fim']}\n"
            f"- Tempo de resposta: {tempo:.2f} s · tentativas: {tentativas}\n"
            f"- finish_reason: {fr} · modelo: {res.model_version}\n"
            f"- Conversa nova, sem histórico. Prompt do usuário: {tdef['prompt']}\n\n"
            f"## Resposta integral\n\n{bruto}\n", encoding="utf-8")
        registros.append(reg)
        salvar_estado()
        aviso ="  ** CORTADA POR MAX_TOKENS **" if reg["cortada_max_tokens"] else ""
        print(f"      {codigo} | {tempo:.2f}s | [ETAPAS] {len(etapas)} car. | resposta {len(final)} car. | "
              f"{fr} | {res.model_version} | novas tentativas: {tentativas - 1}{aviso}")
        if i < total:
            time.sleep(args.pausa)

    fim_bateria = datetime.now()
    configuracao["data_fim"] = fim_bateria.isoformat(timespec="seconds")
    configuracao["interrompida"] = interrompida
    sessoes[-1].update({"fim": configuracao["data_fim"], "interrompida": interrompida})
    salvar_estado()
    registros.sort(key=lambda r: r["ordem_global"])

    # ---------- Arquivos com a condição (não abrir antes da avaliação cega) ----------
    escrever_csv(pasta_id / "execucoes.csv", CAMPOS_EXECUCAO, registros)
    escrever_csv(pasta_id / "tentativas.csv",
                 ["execucao", "tentativa", "inicio", "fim", "resultado", "espera_depois_s"], log_tentativas)
    escrever_csv(pasta_id / "chave_codigos.csv", ["codigo", "tarefa", "condicao", "repeticao"],
                 [{**r, "condicao": CONDICOES[r["condicao"]]} for r in registros])

    ap_c = ["# Apêndice C – Respostas integrais dos testes", "",
            f"Modelo `{args.modelo}`. Cada execução foi feita em conversa nova, sem histórico. "
            "Na condição ChaTinho, o prompt do usuário foi enviado na mesma mensagem que a instrução "
            "de sistema do Apêndice A.", ""]
    for t in tarefas:
        ap_c += [f"## {tarefas_def[t]['nome']}", "", f"Prompt do usuário: {tarefas_def[t]['prompt']}", ""]
        if tarefas_def[t].get("anexo"):
            ap_c += [f"Anexo: {tarefas_def[t]['anexo']}", ""]
        for cond in CONDICOES:
            for r in sorted((x for x in registros if x["tarefa"] == t and x["condicao"] == cond),
                            key=lambda x: x["repeticao"]):
                ap_c += [f"### {CONDICOES[cond]} – execução {r['repeticao']} ({r['codigo']})", "",
                         f"Data: {r['data']} · início {r['hora_inicio']} · fim {r['hora_fim']} · "
                         f"tempo {num_br(r['tempo_s'])} s · finish_reason {r['finish_reason']}", "",
                         r["texto_integral"], ""]
    (pasta_id / "apendice_c_respostas.md").write_text("\n".join(ap_c) + "\n", encoding="utf-8")

    # ---------- Avaliação cega (sem o nome da condição e sem o bloco [ETAPAS]) ----------
    vestigios = avaliacao_cega.gerar(pasta, registros, tarefas_def)
    if vestigios:
        print("Atenção: menção a 'Etapas verificadas' fora das marcas em: " + ", ".join(vestigios))

    # ---------- Resumo ----------
    metricas = [("tempo_s", "Tempo de resposta (s)"), ("etapas_chars", "Bloco [ETAPAS] (caracteres)"),
                ("resposta_chars", "Resposta final (caracteres)"), ("tokens_saida", "Tokens de saída"),
                ("tokens_raciocinio", "Tokens de raciocínio nativo")]
    linhas = []
    for t in tarefas:
        for cond in CONDICOES:
            g = [r for r in registros if r["tarefa"] == t and r["condicao"] == cond]
            l = {"tarefa": tarefas_def[t]["nome"], "condicao": CONDICOES[cond], "respostas_validas": len(g),
                 "etapas_presente_pct": (100.0 * sum(r["etapas_presente"] for r in g) / len(g)) if g else None,
                 "cortadas_max_tokens": sum(r["cortada_max_tokens"] for r in g),
                 "novas_tentativas": sum(r["novas_tentativas"] for r in g)}
            for chave, _ in metricas:
                for est, val in resumir([r.get(chave) for r in g]).items():
                    l[f"{chave}_{est}"] = val
            linhas.append(l)
    if linhas:
        escrever_csv(pasta_id / "resumo.csv", list(linhas[0]), linhas)

    def fmt(l, chave):
        if l[f"{chave}_media"] is None:
            return "-"
        c = 2 if chave == "tempo_s" else 0
        return (f"{num_br(float(l[f'{chave}_media']), c)} ± {num_br(float(l[f'{chave}_dp']), c)} "
                f"({num_br(float(l[f'{chave}_min']), c)}–{num_br(float(l[f'{chave}_max']), c)})")

    versoes = sorted({r["model_version"] for r in registros if r["model_version"]})
    novas = sum(r["novas_tentativas"] for r in registros)
    erros_cont = {}
    for r in registros:
        for e in filter(None, r["erros_nas_tentativas"].split(", ")):
            erros_cont[e] = erros_cont.get(e, 0) + 1
    p = PARAMETROS_GERACAO
    md = [f"# Resumo dos testes – {inicio_bateria.strftime('%d/%m/%Y %H:%M')} a {fim_bateria.strftime('%d/%m/%Y %H:%M')}", "",
          f"Modelo solicitado: `{args.modelo}` · versões retornadas: {', '.join(versoes) or '-'}",
          "Sessões de execução: " + "; ".join(
              f"{datetime.fromisoformat(s['inicio']).strftime('%d/%m/%Y %H:%M')}–"
              f"{datetime.fromisoformat(s['fim']).strftime('%H:%M') if s.get('fim') else '?'}"
              + (" (pausada: cota diária)" if s.get("interrompida") and "cota" in s["interrompida"] else "")
              for s in sessoes),
          "Datas das respostas válidas: " + ", ".join(sorted({r["data"] for r in registros})),
          f"Respostas válidas: {len(registros)} de {total} previstas"
          + (f" · **bateria interrompida:** {interrompida}" if interrompida else ""),
          f"Novas tentativas por falha da API: {novas}"
          + (f" ({', '.join(f'{k}: {v}' for k, v in sorted(erros_cont.items()))})" if erros_cont else ""),
          f"Respostas cortadas por MAX_TOKENS: {sum(r['cortada_max_tokens'] for r in registros)}"
          + "".join(f" · {r['codigo']}" for r in registros if r["cortada_max_tokens"]),
          "", "Valores: média ± desvio-padrão (mínimo–máximo).", "",
          "| Tarefa | Condição | n | " + " | ".join(n for _, n in metricas)
          + " | [ETAPAS] presente | MAX_TOKENS | Novas tentativas |",
          "|---|---|---|" + "---|" * len(metricas) + "---|---|---|"]
    for l in linhas:
        pct = "-" if l["etapas_presente_pct"] is None else f"{l['etapas_presente_pct']:.0f}%"
        md.append(f"| {l['tarefa']} | {l['condicao']} | {l['respostas_validas']} | "
                  + " | ".join(fmt(l, c) for c, _ in metricas)
                  + f" | {pct} | {l['cortadas_max_tokens']} | {l['novas_tentativas']} |")
    md += ["", "## Configuração (idêntica nas duas condições)", "",
           f"- temperature: {p['temperature']} · top_p: {p['top_p']} · top_k: {p['top_k']}",
           f"- max_output_tokens: {p['max_output_tokens']} · thinking_level: {p['thinking_level']} · "
           f"candidate_count: {p['candidate_count']}",
           "- seed: não definida · safety_settings: padrão do serviço · system_instruction: não utilizado",
           "- prompt do ChaTinho concatenado à mensagem do usuário · conversa nova a cada execução",
           f"- Python {platform.python_version()} · google-genai {versao('google-genai')}"]
    (pasta / "resumo.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    (pasta / "LEIA-ME.txt").write_text(
        "avaliacao_cega/  -> respostas sem a condição e sem o bloco [ETAPAS], em ordem aleatória, e uma ficha para cada autor.\n"
        "                    Avaliar ANTES de abrir com_condicao/.\n"
        "com_condicao/    -> medidas (execucoes.csv), tentativas.csv, chave_codigos.csv,\n"
        "                    apendice_c_respostas.md e respostas/ identificadas.\n"
        "resumo.md        -> tabela com média ± desvio-padrão (contém a condição, mas não as respostas).\n"
        "configuracao.json-> parâmetros, versões, prompts e anexos.\n", encoding="utf-8")

    print(f"\nConcluído: {len(registros)}/{total} respostas válidas, {novas} novas tentativas. Resultados em: {pasta}")
    if interrompida:
        sys.exit(1)


if __name__ == "__main__":
    main()
