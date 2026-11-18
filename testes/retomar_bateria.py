"""Retomada automática da bateria (usada pelo Agendador de Tarefas do Windows).

Roda uma vez por dia. Se a bateria indicada ainda não tem todas as respostas
válidas, continua de onde parou com `executar_testes.py --continuar`. Quando
a bateria fica completa, remove a própria tarefa agendada.

Uso:
    python testes/retomar_bateria.py testes/resultados/<data_hora>
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

NOME_TAREFA = "ChaTinho_Bateria"
AQUI = Path(__file__).resolve().parent


def situacao(pasta):
    conf = json.loads((pasta / "configuracao.json").read_text(encoding="utf-8"))
    previstas = conf["respostas_validas_por_tarefa_e_condicao"] * len(conf["tarefas"]) * len(conf["condicoes"])
    arq = pasta / "com_condicao" / "execucoes.json"
    validas = len(json.loads(arq.read_text(encoding="utf-8"))["execucoes"]) if arq.exists() else 0
    return validas, previstas


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    pasta = Path(sys.argv[1]).resolve()
    log = pasta / "agendamento.log"

    def registrar(msg):
        with open(log, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now():%d/%m/%Y %H:%M:%S} {msg}\n")

    validas, previstas = situacao(pasta)
    if validas < previstas:
        registrar(f"retomando: {validas}/{previstas} respostas válidas")
        with open(log, "a", encoding="utf-8") as f:
            subprocess.run([sys.executable, "-X", "utf8", str(AQUI / "executar_testes.py"),
                            "--continuar", str(pasta)], stdout=f, stderr=subprocess.STDOUT,
                           env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
        validas, previstas = situacao(pasta)
        registrar(f"fim da sessão: {validas}/{previstas} respostas válidas")

    if validas >= previstas:
        registrar("bateria completa; removendo a tarefa agendada")
        subprocess.run(["schtasks", "/Delete", "/TN", NOME_TAREFA, "/F"], capture_output=True)


if __name__ == "__main__":
    main()
