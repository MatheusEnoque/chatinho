"""Gera a pasta avaliacao_cega/ de uma bateria de testes.

Conforme a seção 3.4 do TCC, o bloco [ETAPAS]...[/ETAPAS] é removido das
respostas antes da avaliação cega. Em com_condicao/ e no
apendice_c_respostas.md o bloco é mantido.

Pode ser executado sozinho para refazer os arquivos de uma bateria já
concluída, sem novas chamadas à API:
    python testes/avaliacao_cega.py testes/resultados/<data_hora>
"""
import csv
import json
import random
import re
import secrets
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from config_modelo import separar_etapas  # noqa: E402

CAMPOS_AVALIACAO = ["codigo", "tarefa", "criterios_atendidos", "alucinacoes", "erros_abnt",
                    "entregou_texto_pronto", "observacoes"]
_RESTO_ETAPAS = re.compile(r"\[/?ETAPAS\]|etapas verificadas", re.I)


def gerar(pasta, registros, tarefas_def):
    """Escreve avaliacao_cega/ e devolve os códigos em que sobrou algum vestígio do bloco."""
    pasta_cega = Path(pasta) / "avaliacao_cega"
    if pasta_cega.exists():
        shutil.rmtree(pasta_cega)
    pasta_cega.mkdir(parents=True)

    embaralhadas = list(registros)
    random.Random(secrets.randbits(64)).shuffle(embaralhadas)
    vestigios = []
    linhas = ["# Respostas para avaliação cega", "",
              "As respostas estão em ordem aleatória e identificadas só pelo código. A seção "
              "\"Etapas verificadas\" ([ETAPAS]) foi removida, conforme a seção 3.4. Avalie cada "
              "resposta na sua ficha (ficha_avaliacao_autor1.csv ou ficha_avaliacao_autor2.csv) "
              "sem consultar a pasta com_condicao/.", ""]
    for r in embaralhadas:
        tdef = tarefas_def[r["tarefa"]]
        _, sem_etapas = separar_etapas(r["texto_integral"])
        if _RESTO_ETAPAS.search(sem_etapas):
            vestigios.append(r["codigo"])
        linhas += [f"## {r['codigo']} – {tdef['nome']}", "", f"Prompt do usuário: {tdef['prompt']}", "",
                   sem_etapas, "", "---", ""]
    (pasta_cega / "respostas_cegas.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")

    fichas = sorted(({"codigo": r["codigo"], "tarefa": tarefas_def[r["tarefa"]]["nome"]} for r in registros),
                    key=lambda x: (x["tarefa"], x["codigo"]))
    for autor in ("autor1", "autor2"):
        with open(pasta_cega / f"ficha_avaliacao_{autor}.csv", "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=CAMPOS_AVALIACAO, delimiter=";", extrasaction="ignore")
            w.writeheader()
            w.writerows(fichas)
    return vestigios


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    pasta = Path(sys.argv[1])
    registros = json.loads((pasta / "com_condicao" / "execucoes.json").read_text(encoding="utf-8"))["execucoes"]
    tarefas_def = json.loads((pasta / "configuracao.json").read_text(encoding="utf-8"))["tarefas"]
    vestigios = gerar(pasta, registros, tarefas_def)
    print(f"avaliacao_cega/ gerada com {len(registros)} respostas, sem o bloco [ETAPAS].")
    if vestigios:
        print("Atenção: ainda há menção a 'Etapas verificadas' fora das marcas em: " + ", ".join(vestigios))


if __name__ == "__main__":
    main()
