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
    """Lê os dados do Google Sheets ou usa Backup Completo se falhar"""
    df = pd.DataFrame()
    
    try:
        # Tenta ler do Google Sheets
        df = pd.read_csv(SHEET_URL)
        
        # Tratamento de dados da Planilha
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
        df['Foto'] = df['Foto'].apply(corrigir_foto)
        
    except Exception:
        # ==========================================================
        # 🚨 BACKUP DE EMERGÊNCIA (DADOS FICTÍCIOS NO CÓDIGO) 🚨
        # ==========================================================
        st.warning("Usando banco de dados offline (Backup)")
        data = {
            'Nome': [
                'Carlos Eletro', 'João da Luz', 'Roberto Fios', # Eletricistas
                'Paulo Pedreiro', 'Marcos Construção', 'Antônio Obras', # Pedreiros
                'José Encanador', 'Luiz Vazamentos', 'Fernando Tubos', # Encanadores
                'Ana Clima', 'Geladao Refri', 'Frio Max', # Ar Condicionado
                'Maria Gesso', 'Decora Gesso', 'Arte em Gesso', # Gesseiros
                'Vidraçaria Luz', 'Pedro Vidros', 'Transparente Vidros', # Vidraceiros
                'Carlos Jardim', 'Verde Vida', 'Jardins & Cia', # Jardineiros
                'Roberto Mármores', 'Pedra Fina', 'Granitos Sul' # Marmoristas
            ],
            'Categoria': [
                'Eletricista', 'Eletricista', 'Eletricista',
                'Pedreiro', 'Pedreiro', 'Pedreiro',
                'Encanador', 'Encanador', 'Encanador',
                'Ar-Condicionado', 'Ar-Condicionado', 'Ar-Condicionado',
                'Gesseiro', 'Gesseiro', 'Gesseiro',
                'Vidraceiro', 'Vidraceiro', 'Vidraceiro',
                'Jardineiro', 'Jardineiro', 'Jardineiro',
                'Marmorista', 'Marmorista', 'Marmorista'
            ],
            'Whatsapp': ['555599999999'] * 24, # Whats genérico
            'Latitude': [-28.6583, -28.6605, -28.6550, -28.6620, -28.6575, -28.6650, -28.6590, -28.6540, -28.6610, -28.6560, -28.6630, -28.6580, -28.6600, -28.6530, -28.6640, -28.6550, -28.6615, -28.6570, -28.6560, -28.6625, -28.6545, -28.6540, -28.6600, -28.6585],
            'Longitude': [-56.0041, -56.0010, -56.0080, -56.0030, -55.9990, -56.0055, -56.0100, -56.0020, -56.0070, -56.0040, -56.0000, -56.0120, -56.0050, -55.9980, -56.0090, -56.0100, -56.0025, -56.0060, -56.0010, -56.0085, -56.0035, -56.0080, -55.9995, -56.0110],
            'Status': ['Disponível'] * 24,
            'Nota': [5.0, 4.8, 4.9, 5.0, 4.7, 4.5, 5.0, 4.9, 4.8, 5.0, 4.9, 4.6, 5.0, 4.8, 4.9, 4.8, 5.0, 4.7, 5.0, 4.9, 4.8, 4.9, 5.0, 4.7],
            'Foto': ["https://cdn-icons-png.flaticon.com/512/3135/3135715.png"] * 24,
            'Agenda_Lista': [[] for _ in range(24)]
        }
        df = pd.DataFrame(data)
    
    # --- GARANTIAS FINAIS ---
    if 'Nota' in df.columns:
        df['Medalhas'] = df['Nota'].apply(lambda x: ['🥇', '⚡'] if x >= 4.8 else [])
    else:
        df['Medalhas'] = [[] for _ in range(len(df))]
        
    return df

def inicializar_session_state():
    if 'usuario' not in st.session_state:
        st.session_state['usuario'] = None
    if 'aceitou_termos' not in st.session_state:
        st.session_state['aceitou_termos'] = False
    if 'mural_posts' not in st.session_state:
        st.session_state['mural_posts'] = [
            {"id": 1, "autor": "Maria Gesso", "texto": "Sobra de material gesso. Contato inbox.", "respostas": [], "denuncias": 0}
        ]
    st.session_state['prestadores'] = carregar_dados_planilha()

inicializar_session_state()

# --- 3. ESTILO VISUAL (CSS V48.0 - ÍCONES RETANGULARES) ---
st.markdown("""
    <style>
    :root { color-scheme: light; }
    .stApp { background-color: #ffffff; color: #000000; }
    .block-container { padding: 1rem; padding-bottom: 5rem; }

    /* BOTÃO WHATSAPP VERDE */
    .btn-whatsapp {
        display: block; width: 100%; background-color: #25D366; color: white !important;
        text-align: center; padding: 8px; border-radius: 20px; text-decoration: none;
        font-weight: bold; font-size: 14px; margin-top: 5px; border: none; box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .btn-whatsapp:hover { background-color: #128C7E; color: white !important; }

    /* Inputs e Textos */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #f8f9fa !important; color: #000000 !important;
        -webkit-text-fill-color: #000000 !important; border: 1px solid #ced4da !important;
    }
    label, .stMarkdown p { color: #000000 !important; }
    
    .stRadio label p { color: #FF8C00 !important; font-weight: bold !important; font-size: 18px !important; }
    div[role="radiogroup"] [aria-checked="true"] > div:first-child { background-color: #FF8C00 !important; border-color: #FF8C00 !important; }

    /* --- ÍCONES DE CATEGORIA (RETANGULARES) --- */
    
    /* Botão SELECIONADO (Laranja Preenchido) */
    button[kind="primary"] {
        background-color: #FF8C00 !important; border: 1px solid #FF8C00 !important;
        color: white !important; 
        border-radius: 15px !important; /* RETANGULAR ARREDONDADO */
        font-weight: bold !important; box-shadow: none !important;
        width: auto !important; height: auto !important; padding: 10px 15px !important;
        font-size: 28px !important; line-height: 1 !important;
    }
    button[kind="primary"]:hover { background-color: #e67e00 !important; }

    /* Botão NÃO SELECIONADO (Branco com Borda) */
    button[kind="secondary"] {
        border-radius: 15px !important; /* RETANGULAR ARREDONDADO */
        background-color: white !important; 
        border: 2px solid #FF8C00 !important; 
        color: black !important;
        padding: 10px 15px !important; margin: 0 auto !important; display: block !important;
        line-height: 1 !important; box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        width: auto !important; height: auto !important; font-size: 28px !important;
    }

    div[data-testid="stHorizontalBlock"] {
        display: grid !important; grid-template-columns: repeat(4, 1fr) !important;
        gap: 5px !important; width: 100% !important; justify-items: center !important;
    }
    div[data-testid="column"] {
        width: 100% !important; min-width: 0 !important; display: flex !important; flex-direction: column !important; align-items: center !important; padding: 0 !important;
    }
    .rotulo-icone { display: block; width: 100%; text-align: center; font-size: 11px; font-weight: bold; color: #444 !important; margin-top: 5px; line-height: 1.2; }

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
        # Botão normal retangular para avançar
        if st.button("AVANÇAR", type="secondary"):
            st.session_state['aceitou_termos'] = True
            st.rerun()

def tela_cadastro_simples():
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    st.markdown("### 👤 Identificação")
    nome = st.text_input("Seu Nome (Opcional)")
    st.markdown("**Eu sou:**")
    tipo = st.radio("Selecione:", ["Cliente", "Prestador de Serviços"], label_visibility="collapsed")
    st.write("")
    # Botão normal retangular para entrar
    if st.button("ENTRAR NO APP", type="secondary"):
        st.session_state['usuario'] = {
            "nome": nome if nome else "Visitante",
            "tipo": tipo,
            "whats": "", "endereco": "", "medalhas": [], "calendario_ocupado": []
        }
        st.rerun()

def html_ofertas():
    html_content = ""
    encontrou_alguma = False
    for i in range(1, 6):
        video_name = f"oferta{i}.mp4"
        img_name = f"oferta{i}.jpg"
        if os.path.exists(video_name):
            b64 = get_media_base64(video_name)
            html_content += f'<div class="oferta-item"><video autoplay loop muted playsinline width="100%"><source src="data:video/mp4;base64,{b64}" type="video/mp4"></video></div>'
            encontrou_alguma = True
        elif os.path.exists(img_name):
            b64 = get_media_base64(img_name)
            html_content += f'<div class="oferta-item"><img src="data:image/jpeg;base64,{b64}"></div>'
            encontrou_alguma = True
    if not encontrou_alguma:
        html_content = f'<div class="oferta-item"><img src="https://via.placeholder.com/300x200/FF8C00/FFFFFF?text=Adicione+oferta1.jpg"></div>'
    html_content += f'<div class="oferta-item"><img src="https://via.placeholder.com/300x200/333/FFF?text=Novidades"></div>'
    return f"""<div class="ofertas-container">{html_content}</div>"""

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

        c1, c2, c3, c4 = st.columns(4)
        def btn_cat(col, icone, nome, chave):
            # Se selecionado = Primary (Laranja Redondo), Se não = Secondary (Branco Redondo)
            tipo_botao = "primary" if st.session_state['filtro'] == chave else "secondary"
            with col:
                if st.button(icone, key=f"btn_{chave}", type=tipo_botao): 
                    st.session_state['filtro'] = chave
                    st.rerun()
                st.markdown(f'<div class="rotulo-icone">{nome}</div>', unsafe_allow_html=True)

        btn_cat(c1, "⚡", "Eletricista", "Eletricista")
        btn_cat(c2, "🏗️", "Pedreiro", "Pedreiro")
        btn_cat(c3, "🚰", "Encanador", "Encanador")
        btn_cat(c4, "❄️", "Ar-Cond.", "Ar-Condicionado")
        st.write("") 
        c5, c6, c7, c8 = st.columns(4)
        btn_cat(c5, "🧱", "Gesseiro", "Gesseiro")
        btn_cat(c6, "🪟", "Vidraceiro", "Vidraceiro")
        btn_cat(c7, "🌱", "Jardineiro", "Jardineiro")
        btn_cat(c8, "🪨", "Marmorista", "Marmorista")

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

                # --- CORREÇÃO DEFINITIVA DO CARD HTML (USANDO JOIN PARA EVITAR ESPAÇOS) ---
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
            st.markdown("""<div class="ofertas-container"><div class="oferta-item"><img src="https://via.placeholder.com/300x100/333/FFF?text=Anuncie+Aqui"></div></div>""", unsafe_allow_html=True)

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
        for post in st.session_state['mural_posts']:
            st.markdown(f"""<div class="post-mural"><div class="post-header">👤 {post['autor']}</div><div class="post-texto">{post['texto']}</div></div>""", unsafe_allow_html=True)

    with aba4:
        st.markdown("### 🤝 Parceiros")
        p1_img = "https://via.placeholder.com/150?text=Parceiro+1"
        if os.path.exists("parceiro1.jpg"):
            b64 = get_media_base64("parceiro1.jpg")
            p1_img = f"data:image/jpeg;base64,{b64}"
        p2_img = "https://via.placeholder.com/150?text=Parceiro+2"
        if os.path.exists("parceiro2.jpg"):
            b64 = get_media_base64("parceiro2.jpg")
            p2_img = f"data:image/jpeg;base64,{b64}"

        pc1, pc2 = st.columns(2)
        with pc1:
            st.markdown(f'<img src="{p1_img}" style="width:100%; border-radius:10px;">', unsafe_allow_html=True)
            st.markdown('<a href="https://google.com" target="_blank" style="color: #666; font-size: 12px; text-decoration: none; display:block; text-align:center; margin-top:5px;">🔗 Visitar Site</a>', unsafe_allow_html=True)
        with pc2:
            st.markdown(f'<img src="{p2_img}" style="width:100%; border-radius:10px;">', unsafe_allow_html=True)
            st.markdown('<a href="https://google.com" target="_blank" style="color: #666; font-size: 12px; text-decoration: none; display:block; text-align:center; margin-top:5px;">🔗 Visitar Site</a>', unsafe_allow_html=True)

    with aba5:
        usuario = st.session_state['usuario']
        st.header(f"Olá, {usuario['nome']}")
        st.caption(f"Perfil: {usuario['tipo']}")
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
elif st.session_state['usuario'] is None: tela_cadastro_simples()
else: app_principal()