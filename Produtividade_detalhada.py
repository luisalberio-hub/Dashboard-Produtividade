import streamlit as st
import pandas as pd
plotly
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

# --------------------------------
#LOGO DA PAGINA
#--------------------------------
import streamlit as st

st.set_page_config(layout="wide")

st.markdown("""
<style>

/* Remove padding padrão */
.block-container {
    padding-top: 0rem;
    padding-left: 0rem;
    padding-right: 0rem;
}

/* Remove margem externa */
.main {
    padding: 0rem;
}

/* Header full width */
.header-full {
    background-color: #FFC400;
    width: 100vw;
    margin-left: calc(-50vw + 50%);
    padding: 60px 10px;
    display: flex;
    align-items: center;
}

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-full">', unsafe_allow_html=True)

st.image("Logo Millena.png", width=300)

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------
st.set_page_config(page_title="Dashboard Produtividade", layout="wide")

st.markdown("""
<h1 style='text-align: center; 
           color: #191970;
           font-size: 62px;
           margin-bottom: 30px;'>
📊 Dashboard de Produtividade
</h1>
""", unsafe_allow_html=True)

# -----------------------------
# CARREGAR DADOS
# -----------------------------

@st.cache_data
def carregar_dados():
    return pd.read_excel("produtividade_detalhada.xlsx")

df = carregar_dados()
df["Data Inicio"] = pd.to_datetime(df["Data Inicio"])

# -----------------------------
# FILTROS
# -----------------------------

st.sidebar.markdown("## 🔎 Filtros")
st.sidebar.markdown("### ⚡ Período")

periodo_rapido = st.sidebar.radio(
    "Selecione",
    ["Personalizado", "Hoje", "Últimos 7 dias", "Mês Atual"]
)

# -----------------------------
# DEFINIÇÃO AUTOMÁTICA DE DATAS
# -----------------------------

hoje = pd.Timestamp.today().normalize()

if periodo_rapido == "Hoje":
    data_inicio = hoje
    data_fim = hoje

elif periodo_rapido == "Últimos 7 dias":
    data_inicio = hoje - pd.Timedelta(days=7)
    data_fim = hoje

elif periodo_rapido == "Mês Atual":
    data_inicio = hoje.replace(day=1)
    data_fim = hoje

else:
    col1, col2 = st.sidebar.columns(2)

with col1:
    data_inicio = st.date_input(
        "Data Início",
        value=None,
        format="DD/MM/YYYY"
    )

with col2:
    data_fim = st.date_input(
        "Data Fim",
        value=None,
        format="DD/MM/YYYY"
    )
# -----------------------------
# OUTROS FILTROS
# -----------------------------

usuario_pesquisa = st.sidebar.selectbox(
    "Usuário",
    options=["Todos"] + sorted(df["Usuario"].dropna().unique()),
)

atividades = st.sidebar.multiselect(
    "Atividade",
    options=sorted(df["Atividade"].dropna().unique())
)

# -----------------------------
# APLICAÇÃO DO FILTRO
# -----------------------------

df_filtrado = df.copy()

# 🔹 Filtro por data (usando Data Inicio como base principal)
if data_inicio:
    df_filtrado = df_filtrado[
        df_filtrado["Data Inicio"] >= pd.to_datetime(data_inicio)
    ]

# 🔹 Usuário
if usuario_pesquisa != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["Usuario"] == usuario_pesquisa
    ]

# 🔹 Atividade
if atividades:
    df_filtrado = df_filtrado[
        df_filtrado["Atividade"].isin(atividades)
    ]
# -----------------------------
#Variáveis para cards e gráficos
#-----------------------------
# 🎨 CONFIGURAÇÕES VISUAIS
cor_fundo_card = "#191970"      # Fundo do card
cor_titulo = "#FFFAFA"          # Cor do título
cor_valor = "#FFFAFA"           # Cor do valor
tamanho_titulo = 22             # Fonte do título
tamanho_valor = 42              # Fonte do número
cor_barra_lateral = "#FFFF00"   # Barra lateral estilo Power BI

st.markdown(f"""
<style>
.card-pbi {{
    background-color: {cor_fundo_card};
    padding: 22px;
    border-radius: 14px;
    border-left: 6px solid {cor_barra_lateral};
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transition: 0.3s;
}}

.card-pbi:hover {{
    transform: translateY(-4px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.15);
}}

.card-title {{
    font-size: {tamanho_titulo}px;
    font-weight: 600;
    color: {cor_titulo};
    margin-bottom: 8px;
}}

.card-value {{
    font-size: {tamanho_valor}px;
    font-weight: 700;
    color: {cor_valor};
}}
</style>
""", unsafe_allow_html=True)

#-----------------------------
#Cards
#-----------------------------

peso_total = df_filtrado["Peso"].sum()
volume_total = df_filtrado["Volumes"].sum()
prod_total = df_filtrado["Qtd. Produtos"].sum()
palete_total = df_filtrado["Qtd. Palete"].sum()

st.markdown("## 📊 Resultado Geral")
col1, col2, col3, col4 = st.columns(4)

def criar_card(titulo, valor):
    return f"""
    <div class="card-pbi">
        <div class="card-title">{titulo}</div>
        <div class="card-value">{valor}</div>
    </div>
    """

with col1:
    st.markdown(criar_card("⚖️ Peso Total", f"{peso_total:,.0f} Kg"), unsafe_allow_html=True)

with col2:
    st.markdown(criar_card("📦 Volumes", f"{volume_total:,.0f}"), unsafe_allow_html=True)

with col3:
    st.markdown(criar_card("🛒 Produtos", f"{prod_total:,.0f}"), unsafe_allow_html=True)

with col4:
    st.markdown(criar_card("🧱 Paletes", f"{palete_total:,.0f}"), unsafe_allow_html=True)

# -----------------------------
# AGRUPAMENTO MENSAL
# -----------------------------
df_mensal = df_filtrado.groupby("Data Inicio").agg({
    "Peso": "sum",
    "Volumes": "sum",
    "Qtd. Produtos": "sum",
    "Qtd. Cubagem": "sum",
    "Qtd. Palete": "sum"
}).reset_index()

# -----------------------------
# GRÁFICOS COLUNA X MÊS
# -----------------------------
# 1️⃣ Radio
metrica_label = st.radio(
    "Escolha a métrica:",
    ["Peso", "Volume", "Produtos", "Paletes"],
    horizontal=True,
    key="radio_grafico_mensal"
)

# 2️⃣ Definir coluna + cor
if metrica_label == "Peso":
    coluna = "Peso"
    titulo = "Peso por Mês"
    cor = "#1f77b4"

elif metrica_label == "Volume":
    coluna = "Volumes"
    titulo = "Volume por Mês"
    cor = "#ff7f0e"

elif metrica_label == "Produtos":
    coluna = "Qtd. Produtos"
    titulo = "Qtd Produtos por Mês"
    cor = "#2ca02c"

else:
    coluna = "Qtd. Palete"
    titulo = "Qtd Palete por Mês"
    cor = "#9467bd"


# 3️⃣ Garantir datetime
df_mensal["Data Inicio"] = pd.to_datetime(df_mensal["Data Inicio"])

# 4️⃣ Criar coluna AnoMes
df_mensal["AnoMes"] = df_mensal["Data Inicio"].dt.to_period("M")

# 5️⃣ AGRUPAR (AQUI nasce o df_agrupado 👇)
df_agrupado = (
    df_mensal
    .groupby("AnoMes")[coluna]
    .sum()
    .reset_index()
)

# 6️⃣ Converter para string
df_agrupado["AnoMes"] = df_agrupado["AnoMes"].astype(str)


# 7️⃣ Criar gráfico
fig = px.bar(
    df_agrupado,
    x="AnoMes",
    y=coluna,
    title=titulo,
    color_discrete_sequence=[cor],
    text=df_agrupado[coluna].apply(lambda x: f"{x:,.0f}")
)
max_valor = df_agrupado[coluna].max()

fig.update_traces(
    textposition='outside',
    textfont=dict(size=18, color='black')
)

fig.update_layout(
    title=dict(
        text=titulo,
        x=0.5,
        font=dict(size=26, family="Segoe UI")
    ),

    font=dict(
        family="Segoe UI",
        size=16,
        color="#323130"
    ),

    plot_bgcolor="white",
    paper_bgcolor="white",

    margin=dict(t=90),

    xaxis=dict(
        title="",
        tickfont=dict(size=16, color="#323130"),
        showgrid=False
    ),

    yaxis=dict(
        title="",
        range=[0, max_valor * 1.15],
        tickfont=dict(size=16, color="#323130"),
        gridcolor="#E1E1E1",
        zeroline=False
    ),

    bargap=0.3
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# RANKING DE USUÁRIOS
# -----------------------------
st.markdown("## 🏆 Ranking de Produtividade")
metrica_label = st.radio(
    "Escolha a métrica:",
    ["Peso", "Volume", "Produtos", "Paletes"],
    horizontal=True,
    key="filtro_metrica_principal"
)

mapa_sufixos = {
    "Peso": " Kg",
    "Volume": "m³",
    "Produtos": "un",
    "Paletes": "un"
}

sufixo = mapa_sufixos[metrica_label]
mapa_metricas = {
    "Peso": "Peso", 
    "Volume": "Volumes",
    "Produtos": "Qtd. Produtos",
    "Paletes": "Qtd. Palete"
}
coluna_metrica = mapa_metricas[metrica_label]

ranking = (
    df_filtrado
    .groupby("Usuario")[coluna_metrica]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
import plotly.express as px


ranking_top5 = (
    df_filtrado
    .groupby("Usuario")[coluna_metrica]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

def medalha(pos):
    if pos == 1:
        return "🥇"
    elif pos == 2:
        return "🥈"
    elif pos == 3:
        return "🥉"
    else:
        return ""
    
ranking_top5["Posicao"] = list(range(1, 6))

ranking_top5["Usuario_Label"] = (
    ranking_top5["Posicao"].apply(medalha)
    + " " +
    ranking_top5["Usuario"]
)

ranking_top5["Posicao"] = ranking_top5["Posicao"].astype(str)

cores = {
    "1": "#FFD700",  # ouro
    "2": "#C0C0C0",  # prata
    "3": "#CD7F32",  # bronze
    "4": "#1f77b4",
    "5": "#6c757d"
}

fig_rank = px.bar(
    ranking_top5,
    x=coluna_metrica,
    y="Usuario_Label",
    orientation="h",
    text=ranking_top5[coluna_metrica].apply(lambda x: f"{x:,.0f}{sufixo}"),
    color="Posicao",
    color_discrete_map=cores,
    category_orders={"Posicao": ["5","4","3","2","1"]},
    title=f"Top 5 Usuários por {metrica_label}"
)

fig_rank.update_traces(
    textposition="outside",
    textfont=dict(size=20)
)

fig_rank.update_layout(
    showlegend=False,
    xaxis=dict(showticklabels=False),
    yaxis=dict(tickfont=dict(size=18)),
    title=dict(
        x=0.5,
        font=dict(size=28)
    ),
    yaxis_title=None  # remove o nome Usuario_Label
)

st.plotly_chart(fig_rank, use_container_width=True)

st.markdown("## 🏆 Ranking Geral de Produtividade")

ranking = (
    df_filtrado
    .groupby("Usuario")[["Peso", "Volumes", "Qtd. Produtos", "Qtd. Palete"]]
    .sum()
    .reset_index()
)

# 🔥 Criar coluna Total Geral
ranking["Total_Geral"] = (
    ranking["Peso"] +
    ranking["Volumes"] +
    ranking["Qtd. Produtos"] +
    ranking["Qtd. Palete"]
)

# Ordenar pelo Total
ranking = ranking.sort_values(by="Total_Geral", ascending=False).reset_index(drop=True)

def medalha(posicao):
    if posicao == 0:
        return "🥇"
    elif posicao == 1:
        return "🥈"
    elif posicao == 2:
        return "🥉"
    else:
        return ""

ranking["Posição"] = ranking.index
ranking["Medalha"] = ranking["Posição"].apply(medalha)
ranking["Usuario_Label"] = ranking["Medalha"] + " " + ranking["Usuario"]

ranking["Total_Formatado"] = ranking["Total_Geral"].apply(lambda x: f"{x:,.0f}")

fig_rank = px.bar(
    ranking.head(10),
    x="Total_Geral",
    y="Usuario_Label",
    orientation="h",
    text="Total_Formatado",
    title="Top 20 Usuários - Índice Geral"
)
fig_rank.update_traces(
    textposition="outside",
    textfont=dict(size=18)  # 🔥 tamanho dos valores nas barras
)

fig_rank.update_traces(
    textposition="outside",
    textfont=dict(size=18)
)

fig_rank.update_layout(
    yaxis=dict(
        categoryorder='total ascending',
        tickfont=dict(size=16)
    ),
    xaxis=dict(
        tickfont=dict(size=14)
    ),
    title=dict(
        text="Top 20 Usuários - Índice Geral",
        x=0.5,
        font=dict(size=28)
    ),
    yaxis_title=None,  # 🔥 remove nome da coluna
    transition_duration=500
)

st.plotly_chart(fig_rank, use_container_width=True)
