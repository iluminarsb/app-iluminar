import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import base64
import random

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
    try: nota_float = float(nota)
    except: nota_float = 5.0
    n_cheias = int(round(nota_float))
    estrelas = "★" * n_cheias + "☆" * (5 - n_cheias)
    return f'<span style="color: #FF8C00; font-size: 15px;">{estrelas}</span> <span style="font-size: 11px; color: #666; font-weight: bold;">{nota}</span>'

def definir_medalhas(row):
    foto = str(row['Foto']).lower()
    if "flaticon" in foto or "avatar" in foto or foto == "" or "3135715" in foto:
        return ['🥈']
    else:
        return ['🥇', '⚡']

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

def gerar_dados_ficticios_massivos():
    """Gera 10 profissionais por categoria com CORREÇÃO DE GÊNERO NA FOTO"""
    categorias = [
        "Eletricista", "Pedreiro(a)", "Encanador(a)", "Ar-Condicionado", 
        "Gesseiro(a)", "Vidraceiro(a)", "Jardineiro(a)", "Marmorista", "Serviços Gerais"
    ]
    
    nomes_homens = ["Carlos", "João", "Roberto", "Paulo", "Marcos", "José", "Luiz", "Pedro", "Lucas", "Rafael", "Bruno", "Diego", "Felipe", "Anderson"]
    nomes_mulheres = ["Ana", "Maria", "Fernanda", "Juliana", "Carla", "Amanda", "Sonia", "Patrícia", "Camila", "Larissa", "Beatriz", "Mariana"]
    sobrenomes = ["Silva", "Santos", "Oliveira", "Souza", "Lima", "Ferreira", "Costa", "Pereira", "Almeida", "Nascimento", "Rodrigues", "Gomes"]
    
    data = []
    
    for cat in categorias:
        for i in range(10): # 10 por categoria
            # Decide gênero aleatoriamente (70% homem, 30% mulher para construção civil, ex)
            genero = 'men' if random.random() < 0.8 else 'women'
            
            if genero == 'men':
                nome_proprio = random.choice(nomes_homens)
            else:
                nome_proprio = random.choice(nomes_mulheres)
                
            nome_completo = f"{nome_proprio} {random.choice(sobrenomes)}"
            
            # Alterna entre Foto Real (Ouro) e Avatar (Prata)
            if i % 2 == 0:
                # Foto real correspondente ao gênero
                foto = f"https://randomuser.me/api/portraits/{genero}/{random.randint(1,99)}.jpg"
                nf = True
            else:
                foto = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
                nf = False
            
            item = {
                'Nome': nome_completo, 'Categoria': cat, 'Whatsapp': '555599999999',
                'Latitude': -28.6590 + (random.uniform(-0.015, 0.015)), # Espalha um pouco mais
                'Longitude': -56.0020 + (random.uniform(-0.015, 0.015)),
                'Status': 'Disponível', 'Nota': round(random.uniform(4.5, 5.0), 1),
                'Foto': foto, 'Agenda_Lista': [], 'NF': nf
            }
            data.append(item)
            
    df = pd.DataFrame(data)
    df['Medalhas'] = df.apply(definir_medalhas, axis=1)
    return df

def carregar_dados_planilha():
    df = pd.DataFrame()
    try:
        df = pd.read_csv(SHEET_URL)
        if len(df) == 0: raise Exception("Vazia")
        
        df = df.loc[:,~df.columns.duplicated()]
        if 'Agenda' not in df.columns: df['Agenda'] = ""
        df['Agenda'] = df['Agenda'].fillna("").astype(str)
        df['Agenda_Lista'] = df['Agenda'].apply(lambda x: [d.strip() for d in x.split(',')] if x.strip() != "" else [])
        df['Nota'] = pd.to_numeric(df['Nota'], errors='coerce').fillna(5.0)
        
        def corrigir_lat_long(valor):
            try:
                v = float(valor)
                if abs(v) > 90: return v / 10 
                return v
            except:
                return -28.6592 
        
        df['Latitude'] = df['Latitude'].apply(corrigir_lat_long)
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        
        if 'NF' not in df.columns: df['NF'] = False
        else: df['NF'] = df['NF'].astype(bool)
        
        def corrigir_foto(f):
            if pd.isna(f) or str(f).strip() == '' or str(f).lower() == 'avatar': return "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
            return f 
        df['Foto'] = df['Foto'].apply(corrigir_foto)
        df['Medalhas'] = df.apply(definir_medalhas, axis=1)
    except Exception:
        df = gerar_dados_ficticios_massivos()
    return df

def inicializar_session_state():
    if 'usuario' not in st.session_state: st.session_state['usuario'] = None
    if 'aceitou_termos' not in st.session_state: st.session_state['aceitou_termos'] = False
    if 'mural_posts' not in st.session_state:
        comentarios = [
            ("Ana Silva", "women/44.jpg", "Alguém indica um eletricista urgente para o bairro Centro?"),
            ("Marcos Oliveira", "men/32.jpg", "Sobraram 2 sacos de cimento. Vendo barato. Whatsapp: 55 99..."),
            ("Clara Souza", "women/68.jpg", "Preciso de frete para geladeira. Entre em contato comigo!"),
            ("Roberto Santos", "men/85.jpg", "Procuro pedreiro(a) para reforma. Orçamento sem compromisso."),
            ("Luciana Ferreira", "women/12.jpg", "Alguém conhece jardineiro(a) para poda? Entre em contato."),
            ("Ricardo Gomes", "men/11.jpg", "Instalador de ar condicionado para sábado?"),
            ("Fernanda Lima", "women/90.jpg", "Quem faz limpeza de caixa d'água? Preciso urgente."),
            ("Paulo Ricardo", "men/45.jpg", "Preciso de vidraceiro(a). Entre em contato comigo no privado."),
            ("Juliana Costa", "women/22.jpg", "Procuro diarista para pós-obra. Pago bem."),
            ("Bruno Alves", "men/55.jpg", "Vendo restos de piso porcelanato. Entre em contato."),
            ("Carla Dias", "women/33.jpg", "Indicação de encanador(a) para vazamento oculto?"),
            ("Felipe Neto", "men/66.jpg", "Preciso de eletricista para instalar chuveiro."),
            ("Amanda Luz", "women/15.jpg", "Alguém sabe quem faz frete de sofá? Entre em contato comigo."),
            ("Diego Show", "men/10.jpg", "Marmorista disponível para balcão de cozinha?"),
            ("Sonia Abrão", "women/70.jpg", "Preciso de marido de aluguel para pendurar quadros.")
        ]
        posts = []
        for i, (nome, img, texto) in enumerate(comentarios):
            posts.append({"id": i, "autor": nome, "avatar": f"https://randomuser.me/api/portraits/{img}", "texto": texto, "respostas": [], "denuncias": 0})
        st.session_state['mural_posts'] = posts
    if 'prestadores' not in st.session_state:
        st.session_state['prestadores'] = carregar_dados_planilha()

inicializar_session_state()

# --- 3. ESTILO VISUAL (CSS V63.0) ---
st.markdown("""
    <style>
    :root { color-scheme: light; }
    .stApp { background-color: #ffffff; color: #000000; }
    .block-container { padding: 1rem; padding-bottom: 5rem; }

    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #f8f9fa !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border: 1px solid #ced4da !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="input"] { background-color: #f8f9fa !important; }

    div[data-baseweb="tab-list"] { display: flex; width: 100%; gap: 2px; }
    button[data-baseweb="tab"] {
        flex-grow: 1 !important; 
        border-radius: 10px 10px 0 0 !important; 
        background-color: #f1f1f1 !important;
        border: none !important;
        color: #555 !important;
        font-size: 13px !important;
        padding: 10px 0 !important;
    }
    button[aria-selected="true"] { background-color: #FF8C00 !important; color: white !important; }

    .social-container { display: flex; justify-content: center; gap: 40px; margin-top: 15px; margin-bottom: 25px; width: 100%; }
    .insta-original img { filter: grayscale(100%) brightness(0) !important; }

    div[data-testid="column"] > div > div > div > div > button {
        border-radius: 12px !important; width: 100% !important; border: 1px solid #FF8C00 !important;
        font-size: 16px !important; padding: 12px !important; height: auto !important;
    }

    div[data-testid="stHorizontalBlock"] button {
        border-radius: 50% !important; width: 75px !important; height: 75px !important;
        padding: 0 !important; font-size: 35px !important; line-height: 1 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important; margin: 0 auto !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
    }
    div[data-testid="stHorizontalBlock"] button[kind="primary"] {
        background-color: #FF8C00 !important; border: 2px solid #FF8C00 !important;
        color: #FFFF00 !important; text-shadow: 1px 1px 1px #333;
    }
    div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
        background-color: white !important; border: 2px solid #FF8C00 !important; color: black !important;
    }

    .btn-whatsapp { display: block; width: 100%; background-color: #25D366; color: white !important; text-align: center; padding: 10px; border-radius: 20px; text-decoration: none; font-weight: bold; font-size: 14px; margin-top: 5px; border: none; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
    .card-profissional { background-color: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 15px; border-left: 5px solid #FF8C00; width: 100%; }
    .sticky-aviso { position: sticky; top: 0; z-index: 1000; background-color: #FF8C00; color: white !important; text-align: center; padding: 10px; font-weight: bold; font-size: 12px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px; }
    .ofertas-container { display: flex; overflow-x: auto; gap: 10px; padding-bottom: 10px; scrollbar-width: none; width: 100%; }
    .oferta-item { flex: 0 0 auto; width: 85%; max-width: 320px; border-radius: 10px; overflow: hidden; border: 1px solid #eee; }
    .oferta-item img, .oferta-item video { width: 100%; height: auto; display: block; }
    .rotulo-icone { display: block; width: 100%; text-align: center; font-size: 11px; font-weight: bold; color: #444 !important; margin-top: 5px; line-height: 1.2; }
    .box-termos { height: 150px; overflow-y: scroll; background-color: #f8f9fa; border: 1px solid #ced4da; padding: 10px; border-radius: 8px; font-size: 12px; color: #000 !important; margin-bottom: 15px; text-align: justify; }
    div[data-testid="stHorizontalBlock"] { display: grid !important; grid-template-columns: repeat(3, 1fr) !important; gap: 10px !important; }
    div[data-testid="column"] { min-width: 0 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. TELAS DO SISTEMA ---

def tela_termos():
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    else: st.header("⚡ Iluminar Conecta")
    st.markdown("##### 📜 Termos de Uso")
    texto_termos = """1. AVISO IMPORTANTE: Este é um aplicativo de teste da Iluminar.\n2. RESPONSABILIDADE: A empresa não se responsabiliza pelos serviços contratados diretamente com os prestadores.\n3. DADOS: Seus dados serão usados apenas para contato dentro do app.\n4. SEGURANÇA: Não compartilhe senhas financeiras."""
    st.markdown(f"""<div class="box-termos">{texto_termos.replace(chr(10), "<br>")}</div>""", unsafe_allow_html=True)
    st.markdown(criar_link_download(texto_termos, "termos_uso.txt"), unsafe_allow_html=True)
    st.write("")
    aceite = st.checkbox("Li os termos de uso, concordo e aceito.")
    if aceite:
        if st.button("AVANÇAR", type="primary"): 
            st.session_state['aceitou_termos'] = True
            st.rerun()

def formulario_cadastro_prestador():
    st.markdown("### 📝 Cadastro de Prestador")
    st.info("Preencha todos os campos.")
    nome_completo = st.text_input("Nome Completo (Obrigatório)")
    cpf = st.text_input("CPF (Somente números)")
    nome_exibicao = st.text_input("Nome no App (Ex: João Eletricista)")
    categoria = st.selectbox("Sua Categoria", ["Eletricista", "Pedreiro(a)", "Encanador(a)", "Ar-Condicionado", "Gesseiro(a)", "Vidraceiro(a)", "Jardineiro(a)", "Marmorista", "Serviços Gerais"])
    whats = st.text_input("WhatsApp (Com DDD)")
    
    st.markdown("**Foto de Perfil:**")
    tipo_foto = st.radio("Foto:", ["Enviar Foto Real (Ganha Ouro 🥇)", "Usar Avatar (Ganha Prata 🥈)"])
    foto_final = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    medalhas_temp = []
    
    if "Enviar Foto Real" in tipo_foto:
        uploaded = st.file_uploader("Sua foto", type=['jpg', 'png'])
        if uploaded:
            foto_final = "https://randomuser.me/api/portraits/men/99.jpg"
            medalhas_temp = ['🥇', '⚡']
            st.success("Foto OK! Medalha de Ouro.")
    else:
        st.warning("Avatar selecionado (Medalha de Prata).")
        medalhas_temp = ['🥈']
        
    nf = st.checkbox("Emito NF")
    if st.button("CONCLUIR CADASTRO", type="primary"):
        if nome_completo and whats:
            novo = {'Nome': nome_exibicao, 'Categoria': categoria, 'Whatsapp': whats, 'Latitude': -28.6592, 'Longitude': -56.0020, 'Status': 'Disponível', 'Nota': 5.0, 'Foto': foto_final, 'Agenda_Lista': [], 'Medalhas': medalhas_temp, 'NF': nf}
            df_novo = pd.DataFrame([novo])
            st.session_state['prestadores'] = pd.concat([df_novo, st.session_state['prestadores']], ignore_index=True)
            st.session_state['usuario'] = {"nome": nome_exibicao, "tipo": "Prestador de Serviços", "whats": whats, "medalhas": medalhas_temp}
            st.rerun()
    if st.button("Voltar"):
        st.session_state['tela_cadastro'] = False
        st.rerun()

def tela_identificacao():
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    if 'tela_cadastro' in st.session_state and st.session_state['tela_cadastro']:
        formulario_cadastro_prestador()
        return

    st.markdown("### 👤 Quem é você?")
    st.markdown("##### Para Clientes")
    nome = st.text_input("Seu Nome")
    up = st.file_uploader("Foto (Opcional)", type=['jpg', 'png'])
    if up: st.caption("Nota: Foto simulada para teste.")
    avatar = "https://randomuser.me/api/portraits/women/88.jpg" if up else "https://cdn-icons-png.flaticon.com/512/1077/1077114.png"

    if st.button("Sou Cliente (Entrar)", type="primary"):
        st.session_state['usuario'] = {"nome": nome if nome else "Visitante", "tipo": "Cliente", "foto": avatar}
        st.rerun()
    st.divider()
    st.markdown("##### Para Profissionais")
    if st.button("Quero me cadastrar como Prestador"):
        st.session_state['tela_cadastro'] = True
        st.rerun()
    if st.button("Já tenho cadastro (Entrar)", type="secondary"):
        st.session_state['usuario'] = {"nome": "Prestador", "tipo": "Prestador de Serviços"}
        st.rerun()

def app_principal():
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True) 
    else: st.title("⚡ Iluminar Conecta")

    insta_url = "https://www.instagram.com/iluminarsb"
    whats_url = "https://wa.me/5555999900048"
    st.markdown(f"""<div class="social-container"><a href="{insta_url}" target="_blank"><img src="https://cdn-icons-png.flaticon.com/512/1384/1384031.png" width="35" class="insta-original"></a><a href="{whats_url}" target="_blank"><img src="https://cdn-icons-png.flaticon.com/512/220/220236.png" width="35"></a></div>""", unsafe_allow_html=True)

    aba1, aba2, aba3, aba4, aba5 = st.tabs(["🏠 Início", "🗺️ Mapa", "💬 Mural", "🤝 Parceiros", "👤 Perfil"])
    
    with aba1:
        st.markdown("##### 🛠️ Categorias")
        if 'filtro' not in st.session_state: st.session_state['filtro'] = ""

        c1, c2, c3 = st.columns(3)
        def btn_cat(col, icone, nome, chave):
            tipo = "primary" if st.session_state['filtro'] == chave else "secondary"
            with col:
                if st.button(icone, key=f"btn_{chave}", type=tipo): 
                    st.session_state['filtro'] = chave
                    st.rerun()
                st.markdown(f'<div class="rotulo-icone">{nome}</div>', unsafe_allow_html=True)

        btn_cat(c1, "⚡", "Eletricista", "Eletricista")
        btn_cat(c2, "🏗️", "Pedreiro(a)", "Pedreiro(a)")
        btn_cat(c3, "🚰", "Encanador(a)", "Encanador(a)")
        st.write("")
        c4, c5, c6 = st.columns(3)
        btn_cat(c4, "❄️", "Ar-Cond.", "Ar-Condicionado")
        btn_cat(c5, "🧱", "Gesseiro(a)", "Gesseiro(a)")
        btn_cat(c6, "🪟", "Vidraceiro(a)", "Vidraceiro(a)")
        st.write("")
        c7, c8, c9 = st.columns(3)
        btn_cat(c7, "🌱", "Jardineiro(a)", "Jardineiro(a)")
        btn_cat(c8, "🪨", "Marmorista", "Marmorista")
        btn_cat(c9, "🛠️", "Serv. Gerais", "Serviços Gerais")

        ofertas_html = ""
        for i in range(1,6):
            if os.path.exists(f"oferta{i}.mp4"):
                b64 = get_media_base64(f"oferta{i}.mp4")
                ofertas_html += f'<div class="oferta-item"><video autoplay loop muted playsinline width="100%"><source src="data:video/mp4;base64,{b64}" type="video/mp4"></video></div>'
            elif os.path.exists(f"oferta{i}.jpg"):
                b64 = get_media_base64(f"oferta{i}.jpg")
                ofertas_html += f'<div class="oferta-item"><img src="data:image/jpeg;base64,{b64}"></div>'
        if not ofertas_html: ofertas_html = '<div class="oferta-item"><img src="https://via.placeholder.com/300x200/FF8C00/FFFFFF?text=Ofertas"></div>'
        
        if st.session_state['filtro'] == "":
            st.divider()
            st.markdown("##### 🔥 Ofertas da Semana")
            st.markdown(f"""<div class="ofertas-container">{ofertas_html}</div>""", unsafe_allow_html=True)
            st.info("👆 Toque em uma categoria acima.")
            st.divider()
            st.markdown("###### 📢 Parceiros em Destaque")
            st.markdown(html_parceiros_dinamico(), unsafe_allow_html=True)

        else:
            st.write("")
            st.markdown("""<div class="sticky-aviso">Faça o seu orçamento de materiais conosco através do botão do Whatsapp acima.</div>""", unsafe_allow_html=True)
            
            df = st.session_state['prestadores']
            filtro = st.session_state['filtro']
            if 'Categoria' in df.columns:
                df_filtrado = df[df['Categoria'].astype(str).str.contains(filtro, case=False, na=False)]
            else: df_filtrado = pd.DataFrame()

            st.write(f"Encontrados: **{len(df_filtrado)} profissionais**")
            
            df_filtrado['Ordem_Medalha'] = df_filtrado['Medalhas'].apply(lambda x: 0 if '🥇' in x else 1)
            df_filtrado = df_filtrado.sort_values(by=['Ordem_Medalha', 'Nota'], ascending=[True, False])
            
            for i, row in df_filtrado.iterrows():
                meds = " ".join(row['Medalhas'])
                nf_html = '<span style="background-color:#E3F2FD; color:#1565C0; padding:2px 6px; border-radius:4px; font-size:10px; margin-left:5px;">📄 NF</span>' if row.get('NF') else ''
                card = "".join([
                    f'<div class="card-profissional"><div style="display:flex; align-items:center;">',
                    f'<img src="{row["Foto"]}" style="border-radius:50%; width:55px; height:55px; margin-right:15px; border:2px solid #EEE; object-fit:cover;">',
                    f'<div><div style="font-weight:bold; color:#333;">{row["Nome"]} {meds}</div>',
                    f'<div style="color:#666; font-size:12px;">{row["Categoria"]}</div>',
                    f'<div>{gerar_estrelas_html(row["Nota"])} {nf_html}</div>',
                    f'</div></div><a href="https://wa.me/{row["Whatsapp"]}" target="_blank" class="btn-whatsapp">📲 Chamar no WhatsApp</a></div>'
                ])
                st.markdown(card, unsafe_allow_html=True)
            
            st.divider()
            st.markdown("##### 🔥 Aproveite também")
            st.markdown(f"""<div class="ofertas-container">{ofertas_html}</div>""", unsafe_allow_html=True)

    with aba2:
        st.info("📍 Mapa - Prestadores")
        
        # --- FILTRO DENTRO DO MAPA ---
        # Se veio com filtro da home, usa ele. Se não, permite escolher.
        opcoes_filtro = ["Todos", "Eletricista", "Pedreiro(a)", "Encanador(a)", "Ar-Condicionado", "Gesseiro(a)", "Vidraceiro(a)", "Jardineiro(a)", "Marmorista", "Serviços Gerais"]
        
        # Lógica para definir o índice padrão do selectbox
        index_padrao = 0
        if st.session_state.get('filtro'):
            # Tenta achar o filtro atual na lista
            for idx, op in enumerate(opcoes_filtro):
                if st.session_state['filtro'] in op:
                    index_padrao = idx
                    break
        
        filtro_mapa = st.selectbox("O que você quer buscar?", opcoes_filtro, index=index_padrao)
        
        m = folium.Map(location=[-28.6592, -56.0020], zoom_start=13)
        df_mapa = st.session_state['prestadores']
        df_mapa = df_mapa[pd.to_numeric(df_mapa['Latitude'], errors='coerce').notnull()]
        
        # Aplica o filtro selecionado NO MAPA
        if filtro_mapa != "Todos":
            df_mapa = df_mapa[df_mapa['Categoria'].astype(str).str.contains(filtro_mapa, case=False, na=False)]

        icones_mapa = {
            "Eletricista": "bolt", "Pedreiro(a)": "gavel", "Encanador(a)": "tint",
            "Ar-Condicionado": "snowflake-o", "Gesseiro(a)": "paint-brush", "Vidraceiro(a)": "square",
            "Jardineiro(a)": "leaf", "Marmorista": "cube", "Serviços Gerais": "wrench"
        }

        for i, row in df_mapa.iterrows():
            icone_nome = "user"
            for chave, valor in icones_mapa.items():
                if chave in row['Categoria']:
                    icone_nome = valor
                    break
            folium.Marker(
                [row['Latitude'], row['Longitude']], 
                popup=row['Nome'], 
                icon=folium.Icon(color='orange', icon=icone_nome, prefix='fa')
            ).add_to(m)
        st_folium(m, width=700, height=400)

    with aba3:
        st.markdown("### 💬 Mural")
        for post in st.session_state['mural_posts']:
            st.markdown(f"""
            <div class="post-mural" style="margin-bottom: 15px; padding: 10px; background-color: #f8f9fa; border-radius: 10px; border: 1px solid #eee;">
                <div class="post-header" style="display: flex; align-items: center; margin-bottom: 5px; font-weight: bold; color: #FF8C00;">
                    <img src="{post['avatar']}" style="width: 35px; height: 35px; border-radius: 50%; margin-right: 10px; border: 1px solid #ccc; object-fit: cover;">
                    {post['autor']}
                </div>
                <div class="post-texto" style="font-size: 14px; color: #333; padding-left: 45px;">{post['texto']}</div>
            </div>
            """, unsafe_allow_html=True)
        st.divider()
        st.markdown("##### ✏️ Nova Mensagem")
        with st.form("novo_post"):
            st.text_area("Mensagem")
            st.form_submit_button("Publicar")

    with aba4:
        st.markdown("### 🤝 Parceiros")
        st.markdown(html_parceiros_dinamico(), unsafe_allow_html=True)
        st.info("Quer ser um parceiro? Entre em contato!")

    with aba5:
        usuario = st.session_state['usuario']
        st.header(f"Olá, {usuario['nome']}")
        if usuario.get('foto'):
            st.image(usuario['foto'], width=100)
        if st.button("Sair"):
            st.session_state['usuario'] = None
            st.rerun()

if not st.session_state['aceitou_termos']: tela_termos()
elif st.session_state['usuario'] is None: tela_identificacao()
else: app_principal()