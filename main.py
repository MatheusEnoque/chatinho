#BIBLIOTECAS
import streamlit as st
from google import genai
from google.genai import types
import uuid
from datetime import datetime
import requests
import urllib.parse
import os
import json
import shutil
from dotenv import load_dotenv
from config_modelo import MODELO_PADRAO, criar_config, montar_prompt_chatinho, separar_etapas

# Carrega variáveis do arquivo .env
load_dotenv()

#CONFIGURACOES INICIAIS
st.set_page_config(
    page_title="ChaTinho | Consultor Inteligente",
    page_icon="🤖",
    layout="wide"
)


CONVERSAS_DIR = "Conversas"
DOWNLOADS_DIR = "Downloads"
for d in [CONVERSAS_DIR, DOWNLOADS_DIR]:
    if not os.path.exists(d):
        os.makedirs(d)

def pasta_conversa(cid):
    # A pasta é nomeada só pelo identificador; o título fica no dados.json
    return os.path.join(CONVERSAS_DIR, cid)

def pastas_do_id(cid):
    # Todas as pastas da conversa: a atual (<id>) e as antigas (<id>_<título>)
    if not os.path.exists(CONVERSAS_DIR): return []
    return [p for p in os.listdir(CONVERSAS_DIR) if p == cid or p.startswith(cid + "_")]

def salvar_historico(cid_especifico=None):

    cids = [cid_especifico] if cid_especifico else st.session_state["conversas"].keys()

    for cid in cids:
        data = st.session_state["conversas"][cid]

        pasta_path = pasta_conversa(cid)
        os.makedirs(pasta_path, exist_ok=True)


        msgs_para_salvar = []
        for m in data["mensagens"]:
            m_copy = m.copy()
            if "attachments" in m_copy:
                m_copy["attachments"] = [{k: v for k, v in a.items() if k != "data"} for a in m_copy["attachments"]]
            msgs_para_salvar.append(m_copy)
            
        with open(os.path.join(pasta_path, "dados.json"), "w", encoding="utf-8") as f:
            json.dump({**data, "id": cid, "mensagens": msgs_para_salvar}, f, ensure_ascii=False, indent=4)

def ler_dados(pasta):
    with open(os.path.join(CONVERSAS_DIR, pasta, "dados.json"), "r", encoding="utf-8") as f:
        return json.load(f)

def migrar_pastas(cid, pastas, data):
    # Formato antigo: <id>_<título>, com uma pasta a mais a cada troca de título.
    # Grava o conteúdo escolhido em <id>/dados.json, junta as imagens e apaga as pastas antigas.
    destino = pasta_conversa(cid)
    os.makedirs(destino, exist_ok=True)
    with open(os.path.join(destino, "dados.json"), "w", encoding="utf-8") as f:
        json.dump({**data, "id": cid}, f, ensure_ascii=False, indent=4)
    for p in pastas:
        if p == cid: continue
        origem_img = os.path.join(CONVERSAS_DIR, p, "Imagens")
        if os.path.isdir(origem_img):
            os.makedirs(os.path.join(destino, "Imagens"), exist_ok=True)
            for img in os.listdir(origem_img):
                alvo = os.path.join(destino, "Imagens", img)
                if not os.path.exists(alvo): shutil.copy2(os.path.join(origem_img, img), alvo)
        shutil.rmtree(os.path.join(CONVERSAS_DIR, p))

def carregar_historico():
    todas_conversas = {}
    if os.path.exists(CONVERSAS_DIR):
        grupos = {}
        for pasta in os.listdir(CONVERSAS_DIR):
            caminho_dados = os.path.join(CONVERSAS_DIR, pasta, "dados.json")
            if os.path.exists(caminho_dados):
                grupos.setdefault(pasta.split("_")[0], []).append(pasta)
        for cid, pastas in grupos.items():
            candidatos = []
            for p in pastas:
                try: candidatos.append((ler_dados(p), p))
                except Exception: continue
            if not candidatos: continue
            # Conteúdo mais recente: as mensagens só são acrescentadas e o título só muda
            # de "Nova conversa" para o título gerado; então vale a cópia com mais mensagens,
            # depois a que já tem título, e por fim a de modificação mais recente
            candidatos.sort(key=lambda c: (len(c[0].get("mensagens", [])),
                                           c[0].get("titulo") != "Nova conversa",
                                           os.path.getmtime(os.path.join(CONVERSAS_DIR, c[1], "dados.json"))), reverse=True)
            conversa_data = candidatos[0][0]
            if len(pastas) > 1 or pastas[0] != cid:
                migrar_pastas(cid, pastas, conversa_data)
            todas_conversas[cid] = {**conversa_data, "id": cid}
    return todas_conversas

#INICIALIZAÇÃO DO ESTADO
if "conversas"          not in st.session_state: 
    st.session_state["conversas"] = carregar_historico()

if "conversa_active"     not in st.session_state: st.session_state["conversa_active"]     = None
if "api_key"            not in st.session_state: st.session_state["api_key"]            = os.getenv("GEMINI_API_KEY", "")
if "modelo"             not in st.session_state: st.session_state["modelo"]             = MODELO_PADRAO
if "tema"               not in st.session_state: st.session_state["tema"]               = "gradiente"
if "arquivos_pendentes" not in st.session_state: st.session_state["arquivos_pendentes"] = []
if "modo_upload"        not in st.session_state: st.session_state["modo_upload"]        = None
if "view"               not in st.session_state: st.session_state["view"]               = "chat"
if "avisos_anexo"       not in st.session_state: st.session_state["avisos_anexo"]       = []

@st.cache_resource
def get_genai_client(api_key):
    if not api_key: return None
    return genai.Client(api_key=api_key)

#TEMAS
TEMAS = {
    "gradiente": {
        "app_bg": "linear-gradient(135deg, #020617 0%, #0f172a 100%)",
        "app_color": "#f8fafc",
        "sidebar_bg": "#020617",
        "msg_bg": "rgba(30, 41, 59, 0.7)",
        "panel_bg": "rgba(255,255,255,0.03)",
        "accent": "#38bdf8",
        "secondary": "#818cf8"
    },
    "dark": {
        "app_bg": "#0f172a",
        "app_color": "#e2e8f0",
        "sidebar_bg": "#020617",
        "msg_bg": "#1e293b",
        "panel_bg": "#1e293b",
        "accent": "#38bdf8",
        "secondary": "#a78bfa"
    },
    "light": {
        "app_bg": "#f8fafc",
        "app_color": "#0f172a",
        "sidebar_bg": "#f1f5f9",
        "msg_bg": "#ffffff",
        "panel_bg": "#f1f5f9",
        "accent": "#0ea5e9",
        "secondary": "#6366f1"
    },
}
t = TEMAS.get(st.session_state["tema"], TEMAS["gradiente"])

MIME_MAP = {
    "jpg":"image/jpeg","jpeg":"image/jpeg","png":"image/png","gif":"image/gif","webp":"image/webp",
    "pdf":"application/pdf","txt":"text/plain","md":"text/plain","csv":"text/csv",
    "mp3":"audio/mp3","wav":"audio/wav","mp4":"video/mp4"
}

#CSS
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
* {{ font-family: 'Outfit', sans-serif; }}
.stApp {{ background: {t['app_bg']} !important; color: {t['app_color']} !important; }}
[data-testid="stSidebar"] {{ background: {t['sidebar_bg']} !important; border-right: 1px solid rgba(255,255,255,0.1); }}
.main-title {{ font-weight: 800; background: linear-gradient(90deg, {t['accent']}, {t['secondary']}); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3rem; text-align: center; margin-bottom: 0.5rem; letter-spacing: -1px; }}
.subtitle {{ text-align: center; color: #94a3b8; font-size: 1.1rem; margin-bottom: 2rem; font-weight: 300; }}
.stChatMessage {{ background-color: {t['msg_bg']} !important; border-radius: 20px; border: 1px solid rgba(255,255,255,0.05); padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
.file-badge {{ display: inline-flex; align-items: center; gap: 8px; background: rgba(56,189,248,0.1); border: 1px solid rgba(56,189,248,0.2); border-radius: 10px; padding: 6px 14px; font-size: 0.85rem; color: {t['accent']}; margin: 5px 5px 0 0; }}
.upload-panel {{ background: {t['panel_bg']}; border-radius: 20px; padding: 25px; margin-bottom: 30px; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px); }}
.ai-generated-img {{ border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); width: 100%; margin: 15px 0; }}
.ai-generated-img:hover {{ transform: translateY(-5px); box-shadow: 0 25px 30px -5px rgba(0, 0, 0, 0.2); }}
.thought-box {{ background: rgba(0,0,0,0.2); border-left: 3px solid {t['secondary']}; padding: 10px 15px; border-radius: 5px; font-style: italic; color: #94a3b8; font-size: 0.9rem; margin-bottom: 10px; }}
</style>
""", unsafe_allow_html=True)

#FUNCOES
def criar_nova_conversa():
    nid = str(uuid.uuid4())
    st.session_state["conversas"][nid] = {
        "titulo": "Nova conversa",
        "mensagens": [{"role":"assistant","content":"Olá! Eu sou o **ChaTinho**, sua inteligência acadêmica e criativa. \n\nPosso te ajudar a:\n- 📝 Estruturar seu TCC ou trabalhos acadêmicos.\n- 🔍 Analisar documentos e PDFs complexos.\n- 🎨 Gerar imagens conceituais com `/imagem`.\n- 💡 Brainstorm de ideias inovadoras.\n\nComo posso colaborar com você hoje?","attachments":[]}],
        "criada_em": datetime.now().strftime("%d/%m %H:%M"),
    }
    st.session_state["conversa_active"] = nid
    salvar_historico(nid)

def icone(mime):
    if "image" in mime: return "🖼️"
    if "pdf" in mime: return "📄"
    return "📎"

def extensao(nome):
    return os.path.splitext(nome)[1].lower().lstrip(".")

def aviso_formato(nome):
    ext = extensao(nome)
    return f"Formato de arquivo não suportado: {'.' + ext if ext else nome}. Envie PDF, imagem ou texto."

def adicionar_arquivo(f):
    if f is None: return
    if extensao(f.name) not in MIME_MAP:
        # Extensão não mapeada: recusa antes de entrar na lista de pendentes
        st.session_state["avisos_anexo"].append(aviso_formato(f.name))
        return
    st.session_state["arquivos_pendentes"].append({
        "name": f.name, "mime_type": MIME_MAP[extensao(f.name)], "data": f.read()
    })

def remover_nao_suportados():
    # Garante, antes do envio, que nenhum anexo de extensão não mapeada vá para a API
    validos, recusados = [], []
    for a in st.session_state["arquivos_pendentes"]:
        (validos if extensao(a["name"]) in MIME_MAP else recusados).append(a)
    st.session_state["arquivos_pendentes"] = validos
    st.session_state["avisos_anexo"].extend(aviso_formato(a["name"]) for a in recusados)
    return recusados

# Histórico enviado ao modelo: últimas N mensagens da conversa atual (sem a de boas-vindas)
HISTORICO_MAX_MENSAGENS = 10

def montar_historico(mensagens):
    # Só texto (anexos antigos não são reenviados); o prompt de direcionamento
    # não é repetido aqui porque as mensagens guardadas não o contêm.
    historico = [types.Content(role="user" if m["role"] == "user" else "model",
                               parts=[types.Part(text=m["content"])])
                 for m in mensagens[1:] if m.get("content")]
    historico = historico[-HISTORICO_MAX_MENSAGENS:]
    while historico and historico[0].role != "user":
        historico.pop(0)
    return historico

def excluir_conversa(cid):
    if cid in st.session_state["conversas"]:
        # Remover todas as pastas com esse identificador (atual e antigas)
        for pasta in pastas_do_id(cid):
            shutil.rmtree(os.path.join(CONVERSAS_DIR, pasta))
        
        # Remover do estado
        del st.session_state["conversas"][cid]
        
        # Resetar ativa se for a excluída
        if st.session_state["conversa_active"] == cid:
            st.session_state["conversa_active"] = None
        st.rerun()

#SIDEBAR
with st.sidebar:
    st.markdown('<h2 style="text-align: center; margin-bottom: 20px;">🤖 ChaTinho</h2>', unsafe_allow_html=True)
    
    if st.button("➕ Nova Conversa", use_container_width=True):
        st.session_state["view"] = "chat"
        criar_nova_conversa()
        st.rerun()

    if st.button("🖼️ Biblioteca de Imagens", use_container_width=True):
        st.session_state["view"] = "biblioteca"
        st.rerun()

    st.markdown("---")
    st.markdown("### 📎 Anexar Arquivos")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📄 Docs", use_container_width=True): st.session_state["modo_upload"] = "documentos"; st.rerun()
    with c2:
        if st.button("🖼️ Fotos", use_container_width=True): st.session_state["modo_upload"] = "fotos"; st.rerun()
    
    st.markdown("---")
    st.markdown("### 🗨️ Conversas")
    for cid, cv in reversed(list(st.session_state["conversas"].items())):
        col_t, col_d = st.columns([0.8, 0.2])
        with col_t:
            if st.button(cv["titulo"], key=f"btn_{cid}", use_container_width=True):
                st.session_state["view"] = "chat"
                st.session_state["conversa_active"] = cid
                st.rerun()
        with col_d:
            if st.button("🗑️", key=f"del_{cid}", help="Excluir conversa"):
                excluir_conversa(cid)

    st.markdown("---")
    st.markdown("### 🎨 Aparência")
    cl, cd, cg = st.columns(3)
    with cl:
        if st.button("☀️", help="Tema Claro", use_container_width=True):
            st.session_state["tema"] = "light"; st.rerun()
    with cd:
        if st.button("🌙", help="Tema Escuro", use_container_width=True):
            st.session_state["tema"] = "dark"; st.rerun()
    with cg:
        if st.button("✨", help="Tema Azul", use_container_width=True):
            st.session_state["tema"] = "gradiente"; st.rerun()
    
    st.markdown("---")
    with st.expander("⚙️ Configurações"):
        st.session_state["modelo"] = st.selectbox("Modelo", ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.8-flash"])
        st.session_state["api_key"] = st.text_input("API Key", value=st.session_state["api_key"], type="password")

#PRRINCIPAL
if not st.session_state["conversas"]: criar_nova_conversa()

# Busca o ID ativo
cid_ativo = st.session_state.get("conversa_active")
if cid_ativo is None or cid_ativo not in st.session_state["conversas"]:
    cid_ativo = list(st.session_state["conversas"].keys())[-1]
    st.session_state["conversa_active"] = cid_ativo

conv = st.session_state["conversas"][cid_ativo]

if st.session_state["view"] == "biblioteca":
    st.markdown('<h1 class="main-title">Biblioteca de Artes</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Galeria de todas as imagens geradas pela IA</p>', unsafe_allow_html=True)
    
    # Buscar na pasta Downloads central
    todas_imagens = []
    if os.path.exists(DOWNLOADS_DIR):
        for img_file in os.listdir(DOWNLOADS_DIR):
            if img_file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                path_completo = os.path.join(DOWNLOADS_DIR, img_file)
                c_time = os.path.getctime(path_completo)
                todas_imagens.append({
                    "path": path_completo,
                    "name": img_file,
                    "time": c_time,
                    "conversa": "Central de Downloads"
                })
    
    if not todas_imagens:
        st.info("Você ainda não gerou nenhuma imagem. Use o comando `/imagem` no chat!")
    else:
        # Ordenar por data (mais recente primeiro)
        todas_imagens.sort(key=lambda x: x["time"], reverse=True)
        
        # Grid de imagens
        cols = st.columns(3)
        for idx, img in enumerate(todas_imagens):
            with cols[idx % 3]:
                st.image(img["path"], use_container_width=True)
                st.caption(f"📅 {datetime.fromtimestamp(img['time']).strftime('%d/%m %H:%M')}")
                st.markdown(f"**Origem:** {img['conversa']}")
                with open(img["path"], "rb") as f:
                    st.download_button("Baixar", f, file_name=img["name"], key=f"dl_{idx}")
    
    if st.button("← Voltar para o Chat"):
        st.session_state["view"] = "chat"
        st.rerun()
    
    st.stop() # Interrompe a execução para não mostrar o chat abaixo

st.markdown('<h1 class="main-title">ChaTinho</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Sua Inteligência Acadêmica & Criativa</p>', unsafe_allow_html=True)

# Aviso de privacidade (exibido no topo do chat e na área de anexos)
AVISO_PRIVACIDADE = ("Aviso: suas mensagens e anexos são enviados a serviços externos (Google Gemini e "
                     "Pollinations). Não envie dados pessoais, informações sigilosas ou trabalhos ainda não publicados.")
st.info(AVISO_PRIVACIDADE)

# Painel de upload
if st.session_state["modo_upload"]:
    st.markdown('<div class="upload-panel">', unsafe_allow_html=True)
    st.info(AVISO_PRIVACIDADE)
    f = st.file_uploader("Escolha os arquivos", accept_multiple_files=True)
    if f:
        for file in f: adicionar_arquivo(file)
        st.session_state["modo_upload"] = None
        st.rerun()
    if st.button("Cancelar"): st.session_state["modo_upload"] = None; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Mensagens
for msg in conv["mensagens"]:
    with st.chat_message(msg["role"]):
        # Exibe anexos (se houver)
        for att in msg.get("attachments", []):
            if "image" in att["mime_type"]: st.image(att["data"], width=300)
            else: st.markdown(f'<span class="file-badge">{icone(att["mime_type"])} {att["name"]}</span>', unsafe_allow_html=True)
        
        if msg.get("image_url"):
            st.markdown(f"""
                <div style="display: flex; flex-direction: column; align-items: center; margin: 10px 0;">
                    <img src="{msg['image_url']}" 
                         style="width: 100%; max-width: 500px; border-radius: 10px; 
                                border: 2px solid #08DFDC; box-shadow: 0 4px 15px rgba(0,0,0,0.2);"
                         alt="Imagem Gerada">
                    <p style="color: #08DFDC; font-size: 0.75rem; margin-top: 5px; opacity: 0.8;">
                        ✨ Imagem salva em Downloads
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
        # Exibe as etapas se houver ("thought" = conversas salvas antes da troca para [ETAPAS])
        etapas_msg = msg.get("etapas") or msg.get("thought")
        if etapas_msg:
            with st.expander("Etapas verificadas e critérios utilizados"):
                st.markdown(etapas_msg)

        # Exibe o texto da mensagem
        st.markdown(msg["content"])

# Avisos de anexos recusados (exibidos uma vez)
for aviso in st.session_state["avisos_anexo"]:
    st.error(aviso)
st.session_state["avisos_anexo"] = []

# Arquivos pendentes
if st.session_state["arquivos_pendentes"]:
    for a in st.session_state["arquivos_pendentes"]:
        st.markdown(f'<span class="file-badge">⏳ {a["name"]}</span>', unsafe_allow_html=True)
    if st.button("Limpar anexos"): st.session_state["arquivos_pendentes"] = []; st.rerun()

# Input
prompt = st.chat_input("Digite sua mensagem...")

if prompt and remover_nao_suportados():
    # Anexo de formato não suportado: não envia; o aviso aparece após o rerun
    st.rerun()

if prompt:
    # 1. Atualizar o título da conversa se for a primeira mensagem
    if conv["titulo"] == "Nova conversa":
        # Pega um resumo da mensagem para o título
        if prompt.lower().startswith(("/imagem", "\\imagem")):
             resumo = "🖼️ " + prompt.replace("/imagem", "").replace("\\imagem", "").strip()[:20]
        else:
             resumo = prompt[:25].strip()
        
        conv["titulo"] = resumo + ("..." if len(prompt) > 25 else "")
        salvar_historico()

    # 2. Adicionar mensagem do usuário
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. Comando Especial: /imagem ou \imagem (aceita plural /imagens)
    if prompt.lower().startswith(("/imagem", "\\imagem", "/imagens", "\\imagens")):
        # Remove o comando e pega apenas o texto (independente de ser plural ou singular)
        prompt_desc = prompt.lower().replace("/imagens", "").replace("\\imagens", "").replace("/imagem", "").replace("\\imagem", "").strip()
        with st.chat_message("assistant"):
            # Usando o link oficial da API do Pollinations e modelo Flux
            with st.spinner("🎨 Criando sua obra de arte..."):
                import random
                seed = random.randint(1, 999999)
                prompt_encoded = urllib.parse.quote(prompt_desc)
                image_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&nologo=true&seed={seed}&model=flux"
                
                # --- SALVAR A IMAGEM EM DOWNLOADS E NA CONVERSA ---
                try:
                    img_data = requests.get(image_url).content
                    timestamp = datetime.now().strftime('%H%M%S')
                    
                    # 1. Salvar na pasta Downloads (Central)
                    filename_dn = os.path.join(DOWNLOADS_DIR, f"IA_{timestamp}.jpg")
                    with open(filename_dn, "wb") as f:
                        f.write(img_data)
                    
                    # 2. Salvar na pasta da conversa (Histórico)
                    pasta_imagens = os.path.join(pasta_conversa(cid_ativo), "Imagens")
                    os.makedirs(pasta_imagens, exist_ok=True)
                    
                    filename_cv = os.path.join(pasta_imagens, f"IA_{timestamp}.jpg")
                    with open(filename_cv, "wb") as f:
                        f.write(img_data)
                        
                    info_download = f"✅ Salva em: `{filename_dn}`"
                except Exception as e:
                    info_download = f"⚠️ Erro ao salvar arquivo: {e}"
                
                conv["mensagens"].append({"role": "user", "content": prompt, "attachments": []})
                conv["mensagens"].append({
                    "role": "assistant", 
                    "content": f"Aqui está a imagem que você pediu: *{prompt_desc}*\n\n{info_download}",
                    "image_url": image_url,
                    "attachments": []
                })
                salvar_historico(cid_ativo)
                st.rerun()

    # 3. Fluxo Normal com Gemini
    client = get_genai_client(st.session_state["api_key"])
    if client:
        with st.chat_message("assistant"):
            # Instrução de sistema e parâmetros vêm de config_modelo.py
            # (os mesmos usados nos testes em testes/executar_testes.py)
            # O prompt de direcionamento vai só na mensagem atual, como na bateria de testes
            full_prompt = montar_prompt_chatinho(prompt)

            parts = [types.Part(inline_data=types.Blob(mime_type=a["mime_type"], data=a["data"])) for a in st.session_state["arquivos_pendentes"]]
            parts.append(types.Part(text=full_prompt))

            # Histórico da conversa (últimas HISTORICO_MAX_MENSAGENS) + mensagem atual
            contents = montar_historico(conv["mensagens"]) + [types.Content(role="user", parts=parts)]

            try:
                with st.spinner("✨ ChaTinho está processando..."):
                    res = client.models.generate_content(
                        model=st.session_state["modelo"],
                        contents=contents,
                        config=criar_config()
                    )

                # Separa o bloco [ETAPAS] do restante da resposta
                etapas, final_content = separar_etapas(res.text)

                if etapas:
                    with st.expander("Etapas verificadas e critérios utilizados"):
                        st.markdown(etapas)

                st.markdown(final_content)

                conv["mensagens"].append({"role":"user", "content":prompt, "attachments": st.session_state["arquivos_pendentes"]})
                conv["mensagens"].append({
                    "role":"assistant",
                    "content":final_content,
                    "etapas": etapas,
                    "attachments": []
                })
                st.session_state["arquivos_pendentes"] = []
                salvar_historico(cid_ativo)
                st.rerun()
            except Exception as e:
                erro = str(e)
                if "429" in erro and ("per day" in erro.lower() or "perday" in erro.lower()):
                    st.error("🚀 Cota diária da API esgotada. A cota renova no dia seguinte; tente novamente amanhã.")
                elif "429" in erro:
                    st.error("🚀 Limite de mensagens por minuto atingido! Aguarde 1 minuto e tente novamente.")
                elif "API_KEY_INVALID" in str(e):
                    st.error("🔑 Sua chave de API parece inválida. Verifique nas configurações.")
                else:
                    st.error(f"😕 Ops! Tive um pequeno erro de conexão: {e}")
