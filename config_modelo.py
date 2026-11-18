"""Configuração única do modelo Gemini usada pelo ChaTinho (main.py) e pelos
testes (testes/executar_testes.py).

Mantê-la em um só lugar garante que as duas condições experimentais
(com e sem SYSTEM_PROMPT) usem exatamente os mesmos parâmetros.
"""
import re

from google.genai import types

MODELO_PADRAO = "gemini-3.6-flash"

# Parâmetros de geração, iguais nas duas condições experimentais.
# Estes valores devem ser os mesmos registrados na Tabela 2 do artigo.
PARAMETROS_GERACAO = {
    "temperature": 1.0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,    # inclui os tokens de raciocínio interno do modelo
    "candidate_count": 1,
    "thinking_level": "low",      # nível de raciocínio nativo do Gemini 3
    "include_thoughts": False,    # o raciocínio nativo não é devolvido no texto
    "seed": None,                 # não definida (parâmetro não enviado): permite medir a variação entre execuções
    "presence_penalty": None,     # não utilizado (padrão da API)
    "frequency_penalty": None,    # não utilizado (padrão da API)
    "stop_sequences": None,       # não utilizado
    "safety_settings": None,      # padrão da API
    "tools": None,                # sem busca web ou outras ferramentas
}

# Texto literal do Apêndice A do TCC. Qualquer alteração aqui precisa ser
# repetida no Apêndice A, e vice-versa.
SYSTEM_PROMPT = "\n".join([
    "Você é o ChaTinho, uma inteligência de alto nível focada em suporte acadêmico e criativo para estudantes universitários.",
    "Seu tom deve ser profissional, empático, inspirador e extremamente organizado.",
    "",
    "DIRETRIZES:",
    "1. Se o usuário pedir ajuda acadêmica (TCC, resumos, artigos), use uma estrutura lógica e cite a importância da metodologia.",
    "2. Se o usuário pedir algo criativo, seja expansivo e sugira abordagens inovadoras.",
    "3. Antes da resposta final, apresente uma seção breve chamada 'Etapas verificadas', listando os critérios utilizados e as etapas conferidas para elaborar a resposta. Não a apresente como pensamento interno.",
    "4. Se houver arquivos anexados, analise-os com profundidade e referencie partes específicas.",
    "",
    "IMPORTANTE: Comece sua resposta com [ETAPAS] e termine essa seção com [/ETAPAS] antes de dar a resposta final ao usuário.",
])


def criar_config() -> types.GenerateContentConfig:
    p = PARAMETROS_GERACAO
    return types.GenerateContentConfig(
        temperature=p["temperature"],
        top_p=p["top_p"],
        top_k=p["top_k"],
        max_output_tokens=p["max_output_tokens"],
        candidate_count=p["candidate_count"],
        seed=p["seed"],
        thinking_config=types.ThinkingConfig(
            thinking_level=p["thinking_level"],
            include_thoughts=p["include_thoughts"],
        ),
    )


def montar_prompt_chatinho(prompt_usuario: str) -> str:
    """Mesma concatenação feita pelo main.py na condição ChaTinho."""
    return f"{SYSTEM_PROMPT}\n\nUsuário: {prompt_usuario}"


_RE_ETAPAS = re.compile(r"\[ETAPAS\](.*?)\[/ETAPAS\]", re.S)


def separar_etapas(texto: str):
    """Separa o bloco [ETAPAS]...[/ETAPAS] do restante da resposta.

    Retorna (etapas, resposta_final). Se não houver bloco, etapas = "".
    """
    texto = texto or ""
    m = _RE_ETAPAS.search(texto)
    if m:
        return m.group(1).strip(), texto.replace(m.group(0), "").strip()
    return "", texto
