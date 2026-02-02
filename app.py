import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import base64

# --- FUNÇÃO MÍDIA ---
def get_media_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Iluminar Conecta", page_icon="💡", layout="centered")

# --- 2. ESTILO VISUAL (CSS V25.0) ---
st.markdown("""
    <style>
    /* --- RESET E GERAL --- */
    .stApp { background-color: #ffffff; }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 5rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* --- GRADE DE ÍCONES (GRID) --- */
    div[data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 5px !important;
        width: 100% !important;
        justify-items: center !important;
    }
    
    div[data-testid="column"] {
        width: 100% !important;
        min-width: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        padding: 0 !important;
    }

    /* --- BOTÕES REDONDOS (CATEGORIAS) --- */
    button[kind="secondary"] {
        border-radius: 50% !important;
        background-color: white !important;
        border: 2px solid #FF8C00 !important;
        color: black !important;
        padding: 0 !important;
        margin: 0 auto !important;
        display: block !important;
        line-height: 1 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        width: 68px !important;
        height: 68px !important;
        font-size: 28px !important;
    }

    @media (min-width: 768px) {
        button[kind="secondary"] {
            width: 75px !important;
            height: 75px !important;
            font-size: 32px !important;
        }
    }

    button[kind="secondary"]:hover {
        transform: scale(0.95);
        background-color: #FFF3E0 !important;
    }

    /* Rótulo dos ícones */
    .rotulo-icone {
        display: block;
        width: 100%;
        text-align: center;
        font-size: 11px;
        font-weight: bold;
        color: #444;
        margin-top: 5px;
        line-height: 1.2;
    }

    /* --- BOTÕES PRIMÁRIOS (ENTRAR/SALVAR/LIMPAR) --- */
    button[kind="primary"] {
        border-radius: 10px !important;
        font-weight: bold !important;
        background-color: #FF8C00 !important;
        color: white !important;
        border: none !important;
        padding: 10px 10px !important; /* Padding ajustado */
        font-size: 14px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        width: 100% !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    button[kind="primary"]:hover { background-color: #e67e00 !important; }

    /* Sticky Aviso */
    .sticky-aviso { position: sticky; top: 0; z-index: 1000; background-color: #FF8C00; color: white; text-align: center; padding: 10px; font-weight: bold; font-size: 12px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px; }

    /* Social Icons */
    .social-container { display: flex; justify-content: center; gap: 40px; margin-top: 15px; margin-bottom: 15px; }
    .social-icon img { filter: contrast(1.2); }
    
    /* Carrossel */
    .ofertas-container { display: flex; overflow-x: auto; gap: 10px; padding-bottom: 10px; scrollbar-width: none; width: 100%; }
    .ofertas-container::-webkit-scrollbar { display: none; }
    
    .oferta-item { flex: 0 0 auto; width: 85%; max-width: 320px; border-radius: 10px; overflow: hidden; border: 1px solid #eee; }
    .oferta-item img, .oferta-item video { width: 100%; height: auto; display: block; }

    /* Cards */
    .card-profissional { background-color: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.08); margin-bottom: 15px; border-left: 5px solid #FF8C00; width: 100%; }
    
    /* Abas */
    div[data-baseweb="tab-list"] { display: flex; width: 100%; gap: 2px; }
    button[data-baseweb="tab"] { flex-grow: 1 !important; background-color: #f8f9fa !important; border-radius: 5px 5px 0 0 !important; font-size: 14px !important; padding: 10px 0 !important; }
    button[aria-selected="true"] { background-color: #FF8C00 !important; color: white !important; }
    
    /* Termos */
    .box-termos { height: 200px; overflow-y: scroll; background-color: #f9f9f9; border: 1px solid #ddd; padding: 15px; border-radius: 8px; font-size: 13px; color: #444; margin-bottom: 15px; text-align: justify; }

    [data-baseweb="checkbox"] div[data-testid="stCheckbox"] label span { border-color: #FF8C00 !important; }
    [aria-checked="true"] div:first-child { background-color: #FF8C00 !important; border-color: #FF8C00 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. DADOS ---
avatar_homem = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
avatar_mulher = "https://cdn-icons-png.flaticon.com/512/3135/3135789.png"

if 'prestadores' not in st.session_state:
    data = {
        'Nome': ['João Silva', 'Maria Gesso', 'Vidraçaria Luz', 'Pedro Fio', 'Ana Climatização', 'José Encanador'],
        'Categoria': ['Eletricista', 'Gesseiro', 'Vidraceiro', 'Eletricista', 'Ar-Condicionado', 'Encanador'],
        'Whatsapp': ['555599999999', '555588888888', '555577777777', '555566666666', '555544444444', '555533333333'],
        'Latitude': [-28.6592, -28.6600, -28.6550, -28.6580, -28.6570, -28.6610],
        'Longitude': [-56.0020, -56.0050, -56.0100, -56.0030, -56.0040, -56.0060],
        'Status': ['Disponível', 'Disponível', 'Ocupado', 'Disponível', 'Disponível', 'Disponível'],
        'Nota': [4.8, 5.0, 4.5, 4.2, 4.9, 4.7],
        'Foto': [avatar_homem, avatar_mulher, avatar_homem, avatar_homem, avatar_mulher, avatar_homem]
    }
    st.session_state['prestadores'] = pd.DataFrame(data)

# --- 4. FUNÇÕES ---
def mostrar_termos():
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    else: st.header("⚡ Iluminar Conecta")
    
    st.write("")
    st.markdown("##### 📜 Termos de Uso e Responsabilidade")
    st.markdown("""
    <div class="box-termos">
        <strong>1. SOBRE O APLICATIVO</strong><br>
        O "Iluminar Conecta" facilita a conexão entre clientes e prestadores.<br><br>
        <strong>2. ISENÇÃO</strong><br>
        Não garantimos a qualidade ou execução dos serviços.<br><br>
        <strong>3. ACEITE</strong><br>
        Ao clicar em "Entrar", você concorda com os termos.
    </div>
    """, unsafe_allow_html=True)
    
    aceite = st.checkbox("Li os termos de uso, concordo e aceito.")
    st.write("")
    if aceite:
        if st.button("ENTRAR NO APP", type="primary"):
            st.session_state['aceitou_termos'] = True
            st.rerun()

def crear_html_oferta(arquivo_nome, placeholder_text, color):
    if os.path.exists(arquivo_nome + ".mp4"):
        b64 = get_media_base64(arquivo_nome + ".mp4")
        return f'<div class="oferta-item"><video autoplay loop muted playsinline width="100%"><source src="data:video/mp4;base64,{b64}" type="video/mp4"></video></div>'
    elif os.path.exists(arquivo_nome + ".gif"):
        b64 = get_media_base64(arquivo_nome + ".gif")
        return f'<div class="oferta-item"><img src="data:image/gif;base64,{b64}"></div>'
    elif os.path.exists(arquivo_nome + ".jpg"):
        b64 = get_media_base64(arquivo_nome + ".jpg")
        return f'<div class="oferta-item"><img src="data:image/jpeg;base64,{b64}"></div>'
    return f'<div class="oferta-item"><img src="https://via.placeholder.com/300x200/{color}/FFFFFF?text={placeholder_text}"></div>'

def app_principal():
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True) 
    else: st.title("⚡ Iluminar Conecta")

    # SOCIAL
    insta_url = "https://www.instagram.com/iluminarsb?igsh=a3MycGtucXcxdWF1"
    whats_url = "https://wa.me/555534317561"
    icon_insta = "https://cdn-icons-png.flaticon.com/512/1384/1384031.png" 
    icon_whats = "https://cdn-icons-png.flaticon.com/512/5968/5968841.png"

    st.markdown(f"""
    <div class="social-container">
        <a href="{insta_url}" target="_blank" class="social-icon"><img src="{icon_insta}" width="35" height="35"></a>
        <a href="{whats_url}" target="_blank" class="social-icon"><img src="{icon_whats}" width="35" height="35"></a>
    </div>
    """, unsafe_allow_html=True)

    aba1, aba2, aba3, aba4 = st.tabs(["🏠 Início", "🗺️ Mapa", "⭐ Avaliar", "👤 Perfil"])
    
    with aba1:
        st.markdown("##### 🛠️ Categorias")
        if 'filtro' not in st.session_state: st.session_state['filtro'] = ""

        # CATEGORIAS GRID
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("⚡", key="btn_eletr", type="secondary"): st.session_state['filtro'] = "Eletricista"
            st.markdown('<div class="rotulo-icone">Eletricista</div>', unsafe_allow_html=True)
        with c2:
            if st.button("🏗️", key="btn_pedr", type="secondary"): st.session_state['filtro'] = "Pedreiro"
            st.markdown('<div class="rotulo-icone">Pedreiro</div>', unsafe_allow_html=True)
        with c3:
            if st.button("🚰", key="btn_enca", type="secondary"): st.session_state['filtro'] = "Encanador"
            st.markdown('<div class="rotulo-icone">Encanador</div>', unsafe_allow_html=True)
        with c4:
            if st.button("❄️", key="btn_ar", type="secondary"): st.session_state['filtro'] = "Ar-Cond."
            st.markdown('<div class="rotulo-icone">Ar-Cond.</div>', unsafe_allow_html=True)

        # BOTÃO LIMPAR FILTRO (AGORA COM MAIS ESPAÇO: 80% da tela)
        if st.session_state['filtro'] != "":
            st.write("") 
            # Damos 4 partes para o botão e 1 parte vazia. Muito espaço!
            cb1, cb2 = st.columns([4, 1]) 
            with cb1:
                if st.button(f"❌ Limpar Filtro", type="primary"):
                    st.session_state['filtro'] = ""
                    st.rerun()

        st.divider()

        # --- LÓGICA DE EXIBIÇÃO ---
        
        # HTML OFERTAS
        html1 = crear_html_oferta("oferta1", "Oferta+1", "FF8C00")
        html2 = crear_html_oferta("oferta2", "Oferta+2", "25D366")
        offers_html = f"""
        <div class="ofertas-container">
            {html1}
            {html2}
            <div class="oferta-item"><img src="https://via.placeholder.com/300x200/333333/FFFFFF?text=Novidades"></div>
        </div>
        """

        # SE TIVER FILTRO ATIVO
        if st.session_state['filtro'] != "":
            # 1. AVISO
            st.markdown("""<div class="sticky-aviso">Faça o seu orçamento de materiais conosco através do botão do Whatsapp acima.</div>""", unsafe_allow_html=True)
            
            # 2. LISTA
            df = st.session_state['prestadores']
            filtro = st.session_state['filtro']
            mapa_nomes = {"Ar-Cond.": "Ar-Condicionado"}
            nome_real = mapa_nomes.get(filtro, filtro)
            df = df[df['Categoria'] == nome_real]

            st.write(f"Mostrando: **{filtro}**")
            for i, row in df.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="card-profissional">
                        <div style="display: flex; align-items: center;">
                            <img src="{row['Foto']}" style="border-radius: 50%; width: 55px; height: 55px; margin-right: 15px; border: 2px solid #EEE;">
                            <div>
                                <div style="font-weight:bold; color:#333;">{row['Nome']}</div>
                                <div style="color:#666; font-size:13px;">{row['Categoria']}</div>
                                <div style="color:#FF8C00; font-size:12px;">⭐ {row['Nota']} • {row['Status']}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    link = f"https://wa.me/{row['Whatsapp']}"
                    st.link_button("📲 Chamar no WhatsApp", link)
            
            # 3. OFERTAS NO FINAL
            st.divider()
            st.markdown("##### 🔥 Aproveite também")
            st.markdown(offers_html, unsafe_allow_html=True)

        # SE NÃO TIVER FILTRO (HOME)
        else:
            # 1. OFERTAS PRIMEIRO
            st.markdown("##### 🔥 Ofertas da Semana")
            st.markdown(offers_html, unsafe_allow_html=True)
            st.write("")
            
            # 2. INSTRUÇÃO
            st.info("👆 Toque em uma categoria acima para ver os profissionais disponíveis.")

    # RESTANTE DAS ABAS...
    with aba2:
        st.write("")
        col_busca1, col_busca2 = st.columns([3, 1])
        with col_busca1: st.info("Região: São Borja")
        with col_busca2:
            if st.button("📍", type="primary"): st.toast("Buscando...")
        df_mapa = st.session_state['prestadores']
        m = folium.Map(location=[-28.6592, -56.0020], zoom_start=14)
        for i, row in df_mapa.iterrows():
            folium.Marker([row['Latitude'], row['Longitude']], popup=row['Nome'], icon=folium.Icon(color='orange', icon='bolt', prefix='fa')).add_to(m)
        st_folium(m, width=700, height=400)
    with aba3:
        st.write("Avalie o serviço:")
        st.selectbox("Profissional", st.session_state['prestadores']['Nome'])
        st.slider("Nota", 1, 5, 5)
        st.button("Enviar Avaliação", type="primary")
    with aba4:
        st.header("👤 Perfil")
        st.text_input("Nome Completo")
        genero = st.radio("Gênero", ["Masculino", "Feminino"])
        col_img, col_txt = st.columns([1,3])
        with col_img:
            if genero == "Masculino": st.image(avatar_homem, width=80)
            else: st.image(avatar_mulher, width=80)
        st.write("")
        st.button("Salvar Perfil", type="primary")

if 'aceitou_termos' not in st.session_state: st.session_state['aceitou_termos'] = False
if not st.session_state['aceitou_termos']: mostrar_termos()
else: app_principal()