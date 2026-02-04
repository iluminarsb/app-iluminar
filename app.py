import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import base64
from datetime import date

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Iluminar Conecta", page_icon="💡", layout="centered")

# ==============================================================================
# 👇👇👇 LINK DA PLANILHA 👇👇👇
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQebfRxbrTKHczD0zyzThfru67dqKpCbREHoDjZUPAQYY9OQdzEmxCewcxAdtuLc4Upef5UYdMRE2OD/pub?output=csv"
# ==============================================================================

# --- 2. FUNÇÕES AUXILIARES ---
def get_media_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def criar_link_download(texto, filename):
    b64 = base64.b64encode(texto.encode()).decode()
    return f'<a href="data:text/plain;base64,{b64}" download="{filename}" style="color: #666; font-size: 12px; text-decoration: underline;">📥 Baixar Termos de Uso (PDF/Txt)</a>'

def gerar_estrelas_html(nota):
    try:
        nota_float = float(nota)
    except:
        nota_float = 5.0
    n_cheias = int(round(nota_float))
    n_vazias = 5 - n_cheias
    estrelas = "★" * n_cheias + "☆" * n_vazias
    return f'<span style="color: #FF8C00; font-size: 15px; letter-spacing: 1px;">{estrelas}</span> <span style="font-size: 11px; color: #666; font-weight: bold;">{nota}</span>'

def carregar_dados_planilha():
    df = pd.DataFrame()
    try:
        df = pd.read_csv(SHEET_URL)
        
        if len(df) == 0: raise Exception("Planilha Vazia")

        if 'Agenda' not in df.columns: df['Agenda'] = ""
        df['Agenda'] = df['Agenda'].fillna("").astype(str)
        df['Agenda_Lista'] = df['Agenda'].apply(lambda x: [d.strip() for d in x.split(',')] if x.strip() != "" else [])
        df['Nota'] = pd.to_numeric(df['Nota'], errors='coerce').fillna(5.0)
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        
        def corrigir_foto(f):
            if pd.isna(f) or str(f).strip().lower() == 'avatar' or str(f).strip() == '':
                return "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
            return f 
        
        df = df.loc[:,~df.columns.duplicated()]
        if 'Foto' in df.columns: df['Foto'] = df['Foto'].apply(corrigir_foto)
        else: df['Foto'] = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

        df['Medalhas'] = df['Nota'].apply(lambda x: ['🥇', '⚡'] if x >= 4.8 else [])
        
    except Exception:
        # BACKUP COMPLETO (27 PROFISSIONAIS)
        data = {
            'Nome': [
                'Carlos Eletro', 'João da Luz', 'Roberto Fios', 
                'Paulo Pedreiro', 'Marcos Construção', 'Antônio Obras', 
                'José Encanador', 'Luiz Vazamentos', 'Fernando Tubos', 
                'Ana Clima', 'Geladao Refri', 'Frio Max', 
                'Maria Gesso', 'Decora Gesso', 'Arte em Gesso', 
                'Vidraçaria Luz', 'Pedro Vidros', 'Transparente Vidros', 
                'Carlos Jardim', 'Verde Vida', 'Jardins & Cia', 
                'Roberto Mármores', 'Pedra Fina', 'Granitos Sul',
                'Severino Faz Tudo', 'Help Casa', 'SOS Reparos'
            ],
            'Categoria': [
                'Eletricista', 'Eletricista', 'Eletricista',
                'Pedreiro', 'Pedreiro', 'Pedreiro',
                'Encanador', 'Encanador', 'Encanador',
                'Ar-Condicionado', 'Ar-Condicionado', 'Ar-Condicionado',
                'Gesseiro', 'Gesseiro', 'Gesseiro',
                'Vidraceiro', 'Vidraceiro', 'Vidraceiro',
                'Jardineiro', 'Jardineiro', 'Jardineiro',
                'Marmorista', 'Marmorista', 'Marmorista',
                'Serviços Gerais', 'Serviços Gerais', 'Serviços Gerais'
            ],
            'Whatsapp': ['555599999999'] * 27,
            'Latitude': [-28.6583, -28.6605, -28.6550, -28.6620, -28.6575, -28.6650, -28.6590, -28.6540, -28.6610, -28.6560, -28.6630, -28.6580, -28.6600, -28.6530, -28.6640, -28.6550, -28.6615, -28.6570, -28.6560, -28.6625, -28.6545, -28.6540, -28.6600, -28.6585, -28.6595, -28.6612, -28.6578],
            'Longitude': [-56.0041, -56.0010, -56.0080, -56.0030, -55.9990, -56.0055, -56.0100, -56.0020, -56.0070, -56.0040, -56.0000, -56.0120, -56.0050, -55.9980, -56.0090, -56.0100, -56.0025, -56.0060, -56.0010, -56.0085, -56.0035, -56.0080, -55.9995, -56.0110, -56.0045, -56.0022, -56.0066],
            'Status': ['Disponível'] * 27,
            'Nota': [5.0] * 27,
            'Foto': ["https://cdn-icons-png.flaticon.com/512/3135/3135715.png"] * 27,
            'Agenda_Lista': [[] for _ in range(27)],
            'Medalhas': [['🥇', '⚡']] * 27
        }
        df = pd.DataFrame(data)
    return df

def inicializar_session_state():
    if 'usuario' not in st.session_state: st.session_state['usuario'] = None
    if 'aceitou_termos' not in st.session_state: st.session_state['aceitou_termos'] = False
    
    # --- MURAL COM MENSAGENS E FOTOS FICTÍCIAS (AVATARES) ---
    if 'mural_posts' not in st.session_state:
        st.session_state['mural_posts'] = [
            {"id": 1, "autor": "Ana Silva", "avatar": "https://cdn-icons-png.flaticon.com/512/4128/4128244.png", "texto": "Alguém indica um eletricista urgente para o bairro Centro? Minha luz caiu.", "respostas": [], "denuncias": 0},
            {"id": 2, "autor": "Marcos Oliveira", "avatar": "https://cdn-icons-png.flaticon.com/512/4128/4128176.png", "texto": "Sobraram 2 sacos de cimento da minha obra. Vendo barato. Whatsapp: 55 99...", "respostas": [], "denuncias": 0},
            {"id": 3, "autor": "Clara Souza", "avatar": "https://cdn-icons-png.flaticon.com/512/4128/4128359.png", "texto": "Preciso de indicação de frete pequeno para levar uma geladeira até o Pirahy.", "respostas": [], "denuncias": 0},
            {"id": 4, "autor": "Roberto Santos", "avatar": "https://cdn-icons-png.flaticon.com/512/4128/4128262.png", "texto": "Procuro pedreiro para pequena reforma no banheiro. Orçamento sem compromisso.", "respostas": [], "denuncias": 0},
            {"id": 5, "autor": "Luciana Ferreira", "avatar": "https://cdn-icons-png.flaticon.com/512/4128/4128409.png", "texto": "Alguém conhece um bom jardineiro para poda de árvore grande?", "respostas": [], "denuncias": 0}
        ]
    
    if 'prestadores' not in st.session_state:
        st.session_state['prestadores'] = carregar_dados_planilha()

inicializar_session_state()

# --- 3. ESTILO VISUAL (CSS V51.0 - ÍCONES RETANGULARES ARREDONDADOS) ---
st.markdown("""
    <style>
    :root { color-scheme: light; }
    .stApp { background-color: #ffffff; color: #000000; }
    .block-container { padding: 1rem; padding-bottom: 5rem; }

    .btn-whatsapp {
        display: block; width: 100%; background-color: #25D366; color: white !important;
        text-align: center; padding: 8px; border-radius: 20px; text-decoration: none;
        font-weight: bold; font-size: 14px; margin-top: 5px; border: none; box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .btn-whatsapp:hover { background-color: #128C7E; color: white !important; }

    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #f8f9fa !important; color: #000000 !important;
        -webkit-text-fill-color: #000000 !important; border: 1px solid #ced4da !important;
    }
    label, .stMarkdown p { color: #000000 !important; }
    
    .stRadio label p { color: #FF8C00 !important; font-weight: bold !important; font-size: 18px !important; }
    div[role="radiogroup"] [aria-checked="true"] > div:first-child { background-color: #FF8C00 !important; border-color: #FF8C00 !important; }

    /* BOTÕES DOS ÍCONES (RETANGULARES ARREDONDADOS - ESTILO IMAGEM 1) */
    button[kind="primary"] {
        background-color: #FF8C00 !important; border: 1px solid #FF8C00 !important;
        color: white !important; 
        border-radius: 15px !important; /* Retângulo Arredondado */
        font-weight: bold !important; box-shadow: none !important;
        width: auto !important; height: auto !important; padding: 10px 15px !important;
        font-size: 28px !important; line-height: 1.1 !important;
    }
    
    button[kind="secondary"] {
        border-radius: 15px !important; /* Retângulo Arredondado */
        background-color: white !important; 
        border: 2px solid #FF8C00 !important; 
        color: black !important;
        padding: 10px 15px !important; margin: 0 auto !important; display: block !important;
        line-height: 1.1 !important; box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        width: auto !important; height: auto !important; font-size: 28px !important;
    }

    /* GRID DE 3 COLUNAS */
    div[data-testid="stHorizontalBlock"] {
        display: grid !important; grid-template-columns: repeat(3, 1fr) !important;
        gap: 10px !important; width: 100% !important; justify-items: center !important;
    }
    div[data-testid="column"] {
        width: 100% !important; min-width: 0 !important; display: flex !important; flex-direction: column !important; align-items: center !important; padding: 0 !important;
    }
    .rotulo-icone { display: block; width: 100%; text-align: center; font-size: 12px; font-weight: bold; color: #444 !important; margin-top: 5px; line-height: 1.2; }

    .social-container { display: flex; justify-content: center; gap: 40px; margin-top: 15px; margin-bottom: 15px; }
    .insta-original img { filter: grayscale(100%) brightness(0) !important; }
    .card-profissional { background-color: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.08); margin-bottom: 15px; border-left: 5px solid #FF8C00; width: 100%; }
    .sticky-aviso { position: sticky; top: 0; z-index: 1000; background-color: #FF8C00; color: white !important; text-align: center; padding: 10px; font-weight: bold; font-size: 12px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px; }
    
    .ofertas-container { display: flex; overflow-x: auto; gap: 10px; padding-bottom: 10px; scrollbar-width: none; width: 100%; }
    .oferta-item { flex: 0 0 auto; width: 85%; max-width: 320px; border-radius: 10px; overflow: hidden; border: 1px solid #eee; }
    .oferta-item img, .oferta-item video { width: 100%; height: auto; display: block; }
    div[data-baseweb="tab-list"] { display: flex; width: 100%; gap: 2px; }
    button[data-baseweb="tab"] { flex-grow: 1 !important; background-color: #f8f9fa !important; border-radius: 5px 5px 0 0 !important; font-size: 12px !important; padding: 10px 0 !important; }
    button[aria-selected="true"] { background-color: #FF8C00 !important; color: white !important; }
    
    .box-termos { height: 150px; overflow-y: scroll; background-color: #f8f9fa; border: 1px solid #ced4da; padding: 10px; border-radius: 8px; font-size: 12px; color: #000 !important; margin-bottom: 15px; text-align: justify; }
    [data-baseweb="checkbox"] div[data-testid="stCheckbox"] label span { border-color: #FF8C00 !important; background-color: white !important; }
    [aria-checked="true"] div:first-child { background-color: #FF8C00 !important; border-color: #FF8C00 !important; }
    div[data-baseweb="select"] > div { background-color: #f8f9fa !important; color: #000000 !important; border-color: #ced4da !important; }
    div[data-baseweb="select"] span { color: #000000 !important; }
    div[data-baseweb="menu"] { background-color: #ffffff !important; }
    div[data-baseweb="option"] { color: #000000 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. TELAS DO SISTEMA ---

def tela_termos():
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    else: st.header("⚡ Iluminar Conecta")
    st.markdown("##### 📜 Termos de Uso")
    texto_termos = """1. AVISO IMPORTANTE: Este é um aplicativo de teste da Iluminar.\n2. RESPONSABILIDADE: A empresa não se responsabiliza pelos serviços contratados.\n3. DADOS: Seus dados serão usados apenas para contato dentro do app.\n4. SEGURANÇA: Não compartilhe senhas financeiras."""
    st.markdown(f"""<div class="box-termos">{texto_termos.replace(chr(10), "<br>")}</div>""", unsafe_allow_html=True)
    st.markdown(criar_link_download(texto_termos, "termos_uso.txt"), unsafe_allow_html=True)
    st.write("")
    aceite = st.checkbox("Li os termos de uso, concordo e aceito.")
    if aceite:
        st.write("")
        if st.button("AVANÇAR", type="secondary"):
            st.session_state['aceitou_termos'] = True
            st.rerun()

def formulario_cadastro_prestador():
    st.markdown("### 📝 Cadastro de Prestador")
    st.info("Preencha todos os campos para ganhar destaque Ouro! 🥇")
    
    # 1. Dados Pessoais
    nome_completo = st.text_input("Nome Completo (Obrigatório)")
    cpf = st.text_input("CPF (Somente números)", max_chars=11)
    
    # 2. Dados Públicos
    nome_exibicao = st.text_input("Nome que aparecerá no App (Ex: João Eletricista)")
    categoria = st.selectbox("Sua Categoria", ["Eletricista", "Pedreiro", "Encanador", "Ar-Condicionado", "Gesseiro", "Vidraceiro", "Jardineiro", "Marmorista", "Serviços Gerais"])
    whats = st.text_input("WhatsApp de Trabalho (Com DDD)", placeholder="555599999999")
    
    # 3. Avatar
    st.markdown("**Escolha sua Foto/Avatar:**")
    avatares = {
        "Homem Capacete": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
        "Mulher Capacete": "https://cdn-icons-png.flaticon.com/512/3135/3135768.png",
        "Homem Formal": "https://cdn-icons-png.flaticon.com/512/4128/4128176.png",
        "Mulher Formal": "https://cdn-icons-png.flaticon.com/512/4128/4128244.png"
    }
    opcao_avatar = st.radio("Selecione:", list(avatares.keys()), horizontal=True)
    foto_final = avatares[opcao_avatar]
    
    # 4. Detalhes
    nota_fiscal = st.checkbox("Emito Nota Fiscal")
    descricao = st.text_area("Descreva seu trabalho e experiência (Máx 300 letras)", max_chars=300)
    
    st.markdown("**Fotos de Trabalhos:**")
    st.file_uploader("Envie fotos (Apenas simulação visual)", accept_multiple_files=True)
    st.caption("⚠️ Responsabilidade: Declaro ter autorização para divulgar as imagens dos serviços.")
    
    termos_resp = st.checkbox("Declaro que as informações são verdadeiras.")
    
    if st.button("CONCLUIR CADASTRO", type="primary"):
        if nome_completo and whats and nome_exibicao and termos_resp:
            medalhas = []
            if descricao and nota_fiscal:
                medalhas = ['🥇', '⚡']
            
            novo_prestador = {
                'Nome': nome_exibicao,
                'Categoria': categoria,
                'Whatsapp': whats,
                'Latitude': -28.6592,
                'Longitude': -56.0020,
                'Status': 'Disponível',
                'Nota': 5.0,
                'Foto': foto_final,
                'Agenda_Lista': [],
                'Medalhas': medalhas
            }
            
            novo_df = pd.DataFrame([novo_prestador])
            st.session_state['prestadores'] = pd.concat([novo_df, st.session_state['prestadores']], ignore_index=True)
            
            st.session_state['usuario'] = {
                "nome": nome_exibicao,
                "tipo": "Prestador de Serviços",
                "whats": whats,
                "medalhas": medalhas
            }
            st.success("Cadastro realizado com Sucesso! Bem-vindo.")
            st.rerun()
        else:
            st.error("Preencha os campos obrigatórios e aceite o termo.")
            
    if st.button("Voltar"):
        st.session_state['tela_cadastro'] = False
        st.rerun()

def tela_identificacao():
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    
    if 'tela_cadastro' in st.session_state and st.session_state['tela_cadastro']:
        formulario_cadastro_prestador()
        return

    st.markdown("### 👤 Quem é você?")
    
    st.markdown("**Escolha seu Avatar (Cliente):**")
    st.markdown("👨🏿 👩🏼 👴🏽 👱🏻‍♀️ 🧔🏻 👩🏾")
    
    nome = st.text_input("Seu Nome")
    
    if st.button("Sou Cliente", type="primary"):
        st.session_state['usuario'] = {"nome": nome if nome else "Visitante", "tipo": "Cliente"}
        st.rerun()
            
    st.divider()
    st.markdown("##### Para Profissionais")
    if st.button("Quero me cadastrar como Prestador de Serviços no app ILUMINAR CONECTA"):
        st.session_state['tela_cadastro'] = True
        st.rerun()
    
    if st.button("Já tenho cadastro (Entrar)", type="secondary"):
        st.session_state['usuario'] = {"nome": nome if nome else "Prestador", "tipo": "Prestador de Serviços"}
        st.rerun()

def html_ofertas():
    html_content = ""
    for i in range(1, 6):
        if os.path.exists(f"oferta{i}.mp4"):
            b64 = get_media_base64(f"oferta{i}.mp4")
            html_content += f'<div class="oferta-item"><video autoplay loop muted playsinline width="100%"><source src="data:video/mp4;base64,{b64}" type="video/mp4"></video></div>'
        elif os.path.exists(f"oferta{i}.jpg"):
            b64 = get_media_base64(f"oferta{i}.jpg")
            html_content += f'<div class="oferta-item"><img src="data:image/jpeg;base64,{b64}"></div>'
    
    if not html_content:
        html_content = f'<div class="oferta-item"><img src="https://via.placeholder.com/300x200/FF8C00/FFFFFF?text=Ofertas"></div>'
    return f"""<div class="ofertas-container">{html_content}</div>"""

def html_parceiros_dinamico():
    html_content = ""
    for i in range(1, 6):
        nome_base = f"parceiro{i}"
        if os.path.exists(f"{nome_base}.mp4"):
            b64 = get_media_base64(f"{nome_base}.mp4")
            html_content += f'<div class="oferta-item" style="width: 150px;"><video autoplay loop muted playsinline width="100%"><source src="data:video/mp4;base64,{b64}" type="video/mp4"></video></div>'
        elif os.path.exists(f"{nome_base}.gif"):
            b64 = get_media_base64(f"{nome_base}.gif")
            html_content += f'<div class="oferta-item" style="width: 150px;"><img src="data:image/gif;base64,{b64}"></div>'
        elif os.path.exists(f"{nome_base}.jpg"):
            b64 = get_media_base64(f"{nome_base}.jpg")
            html_content += f'<div class="oferta-item" style="width: 150px;"><img src="data:image/jpeg;base64,{b64}"></div>'
    
    if not html_content:
        html_content = '<div style="text-align:center; color:#999; width:100%;">Em breve</div>'
        
    return f"""<div class="ofertas-container" style="justify-content: center;">{html_content}</div>"""

def app_principal():
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True) 
    else: st.title("⚡ Iluminar Conecta")

    insta_url = "https://www.instagram.com/iluminarsb"
    whats_url = "https://wa.me/5555999900048"
    icon_insta = "https://cdn-icons-png.flaticon.com/512/1384/1384031.png"
    icon_whats_vasado = "https://cdn-icons-png.flaticon.com/512/220/220236.png"

    st.markdown(f"""
    <div class="social-container">
        <a href="{insta_url}" target="_blank" class="social-icon insta-original"><img src="{icon_insta}" width="35" height="35"></a>
        <a href="{whats_url}" target="_blank" class="social-icon"><img src="{icon_whats_vasado}" width="35" height="35"></a>
    </div>
    """, unsafe_allow_html=True)

    aba1, aba2, aba3, aba4, aba5 = st.tabs(["🏠 Início", "🗺️ Mapa", "💬 Mural", "🤝 Parceiros", "👤 Perfil"])
    
    with aba1:
        st.markdown("##### 🛠️ Categorias")
        if 'filtro' not in st.session_state: st.session_state['filtro'] = ""

        # GRID 3 COLUNAS
        c1, c2, c3 = st.columns(3)
        def btn_cat(col, icone, nome, chave):
            tipo_botao = "primary" if st.session_state['filtro'] == chave else "secondary"
            with col:
                if st.button(icone, key=f"btn_{chave}", type=tipo_botao): 
                    st.session_state['filtro'] = chave
                    st.rerun()
                st.markdown(f'<div class="rotulo-icone">{nome}</div>', unsafe_allow_html=True)

        btn_cat(c1, "⚡", "Eletricista", "Eletricista")
        btn_cat(c2, "🏗️", "Pedreiro", "Pedreiro")
        btn_cat(c3, "🚰", "Encanador", "Encanador")
        st.write("")
        c4, c5, c6 = st.columns(3)
        btn_cat(c4, "❄️", "Ar-Cond.", "Ar-Condicionado")
        btn_cat(c5, "🧱", "Gesseiro", "Gesseiro")
        btn_cat(c6, "🪟", "Vidraceiro", "Vidraceiro")
        st.write("")
        c7, c8, c9 = st.columns(3)
        btn_cat(c7, "🌱", "Jardineiro", "Jardineiro")
        btn_cat(c8, "🪨", "Marmorista", "Marmorista")
        btn_cat(c9, "🛠️", "Serv. Gerais", "Serviços Gerais")

        ofertas_html = html_ofertas()

        if st.session_state['filtro'] != "":
            st.write("")
            st.markdown("""<div class="sticky-aviso">Faça o seu orçamento de materiais conosco através do botão do Whatsapp acima.</div>""", unsafe_allow_html=True)
            
            df = st.session_state['prestadores']
            filtro = st.session_state['filtro']
            if 'Categoria' in df.columns:
                df_filtrado = df[df['Categoria'].astype(str).str.contains(filtro, case=False, na=False)]
            else:
                df_filtrado = pd.DataFrame() 

            st.write(f"Encontrados: **{len(df_filtrado)} profissionais**")
            
            for i, row in df_filtrado.iterrows():
                lista_medalhas = row['Medalhas'] if 'Medalhas' in row else []
                if not isinstance(lista_medalhas, list): lista_medalhas = []
                medalhas = " ".join(lista_medalhas)
                estrelas_html = gerar_estrelas_html(row['Nota'])
                
                agenda_html = ""
                if len(row['Agenda_Lista']) > 0:
                    dias_texto = ", ".join(row['Agenda_Lista'])
                    agenda_html = f'<div style="color: #D32F2F; font-size: 11px; margin-top: 5px; font-weight: bold;">📅 Ocupado em: {dias_texto}</div>'

                with st.container():
                    card_html = "".join([
                        f'<div class="card-profissional">',
                        f'<div style="display: flex; align-items: center;">',
                        f'<img src="{row["Foto"]}" style="border-radius: 50%; width: 55px; height: 55px; margin-right: 15px; border: 2px solid #EEE; object-fit: cover;">',
                        f'<div>',
                        f'<div style="font-weight:bold; color:#333;">{row["Nome"]} {medalhas}</div>',
                        f'<div style="color:#666; font-size:12px; margin-bottom: 2px;">{row["Categoria"]}</div>',
                        f'<div>{estrelas_html} <span style="color:#888; font-size:10px;">• {row["Status"]}</span></div>',
                        f'{agenda_html}',
                        f'</div></div>',
                        f'<a href="https://wa.me/{row["Whatsapp"]}" target="_blank" class="btn-whatsapp">📲 Chamar no WhatsApp</a>',
                        f'</div>'
                    ])
                    st.markdown(card_html, unsafe_allow_html=True)

            st.divider()
            st.markdown("##### 🔥 Aproveite também")
            st.markdown(ofertas_html, unsafe_allow_html=True)

        else:
            st.divider()
            st.markdown("##### 🔥 Ofertas da Semana")
            st.markdown(ofertas_html, unsafe_allow_html=True)
            st.write("")
            st.info("👆 Toque em uma categoria acima para ver os profissionais disponíveis.")
            st.divider()
            st.markdown("###### 📢 Parceiros em Destaque")
            st.markdown(html_parceiros_dinamico(), unsafe_allow_html=True)

    with aba2:
        st.write("")
        st.info("📍 Prestadores na região")
        m = folium.Map(location=[-28.6592, -56.0020], zoom_start=14)
        df_mapa = st.session_state['prestadores']
        if 'Latitude' in df_mapa.columns and 'Longitude' in df_mapa.columns:
            df_mapa = df_mapa.dropna(subset=['Latitude', 'Longitude'])
            for i, row in df_mapa.iterrows():
                folium.Marker([row['Latitude'], row['Longitude']], popup=row['Nome'], icon=folium.Icon(color='orange', icon='bolt', prefix='fa')).add_to(m)
        st_folium(m, width=700, height=400)

    with aba3:
        st.markdown("### 💬 Mural")
        with st.form("novo_post"):
            texto_post = st.text_area("O que você precisa?", max_chars=300)
            if st.form_submit_button("Publicar", type="secondary"):
                st.success("Publicado!")
        st.divider()
        # MURAL COM AVATARES (FOTOS)
        for post in st.session_state['mural_posts']:
            st.markdown(f"""
            <div class="post-mural" style="margin-bottom: 15px; padding: 10px; background-color: #f8f9fa; border-radius: 10px; border: 1px solid #eee;">
                <div class="post-header" style="display: flex; align-items: center; margin-bottom: 5px; font-weight: bold; color: #FF8C00;">
                    <img src="{post['avatar']}" style="width: 35px; height: 35px; border-radius: 50%; margin-right: 10px; border: 1px solid #ccc;">
                    {post['autor']}
                </div>
                <div class="post-texto" style="font-size: 14px; color: #333; padding-left: 45px;">{post['texto']}</div>
            </div>
            """, unsafe_allow_html=True)

    with aba4:
        st.markdown("### 🤝 Parceiros")
        st.markdown(html_parceiros_dinamico(), unsafe_allow_html=True)
        st.info("Quer ser um parceiro? Entre em contato!")

    with aba5:
        usuario = st.session_state['usuario']
        st.header(f"Olá, {usuario['nome']}")
        st.caption(f"Perfil: {usuario['tipo']}")
        
        if usuario['tipo'] == 'Prestador de Serviços':
            st.divider()
            ativo = st.toggle("Ativo para Trabalho", value=True)
            if not ativo: st.warning("Você está invisível nas buscas.")
            else: st.success("Você está visível para clientes.")
            
        opcoes = st.selectbox("Gerenciar", ["Meus Dados", "Sair"])
        if opcoes == "Meus Dados":
            st.text_input("WhatsApp", value=usuario.get('whats', ''))
            st.button("Salvar", type="secondary")
        elif opcoes == "Sair":
            if st.button("Sair da Conta"):
                st.session_state['usuario'] = None
                st.session_state['aceitou_termos'] = False
                st.rerun()

if not st.session_state['aceitou_termos']: tela_termos()
elif st.session_state['usuario'] is None: tela_identificacao()
else: app_principal()