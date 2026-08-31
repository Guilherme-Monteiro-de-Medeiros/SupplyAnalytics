import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="SupplyAnalytics - Dashboard Logístico",
    page_icon="🚚",
    layout="wide"
)

# Estilização CSS Avançada: auto-adaptação responsiva dos cards de métricas
st.markdown("""
    <style>
    /* Transforma os containers das métricas em contêineres de medição CSS */
    div[data-testid="stMetric"] {
        container-type: inline-size;
        background-color: #f8f9fa;
        padding: 12px 16px;
        border-radius: 8px;
        border: 1px solid #e9ecef;
    }
    
    /* Fonte do valor auto-ajustável usando clamp() e cqw (Container Query Width) */
    div[data-testid="stMetricValue"] {
        font-size: clamp(1.1rem, 11cqw, 1.8rem) !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: clip !important;
        font-weight: 700;
    }
    
    /* Auto-ajuste do rótulo da métrica */
    div[data-testid="stMetricLabel"] {
        font-size: clamp(0.75rem, 5cqw, 0.95rem) !important;
        white-space: nowrap !important;
        color: #495057;
    }
    </style>
""", unsafe_allow_html=True)

# Função para formatação no padrão brasileiro (pt-BR)
def formatar_moeda(valor):
    """Formata valores numéricos para o padrão de moeda brasileiro R$ X.XXX,XX"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_inteiro(valor):
    """Formata valores inteiros com separador de milhar em ponto"""
    return f"{valor:,}".replace(",", ".")

# Carregamento dos dados
@st.cache_data
def carregar_dados():
    df = pd.read_csv("dados_logistica_tratados.csv")
    df['data_compra'] = pd.to_datetime(df['data_compra'])
    return df

try:
    df = carregar_dados()
except Exception as e:
    st.error("Erro ao carregar o arquivo 'dados_logistica_tratados.csv'. Certifique-se de executar o 'pipeline_logistica.py' primeiro.")
    st.stop()

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.header("🔍 Filtros da Operação")

regioes = ['Todas'] + list(df['regiao_destino'].unique())
regiao_sel = st.sidebar.selectbox("Região de Destino:", regioes)

categorias = ['Todas'] + list(df['categoria'].unique())
categoria_sel = st.sidebar.selectbox("Categoria de Produto:", categorias)

status_lista = ['Todos'] + list(df['status_sla_detalhado'].unique())
status_sel = st.sidebar.selectbox("Status do Pedido:", status_lista)

# Aplicação dos Filtros
df_filtrado = df.copy()
if regiao_sel != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['regiao_destino'] == regiao_sel]
if categoria_sel != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_sel]
if status_sel != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['status_sla_detalhado'] == status_sel]

# --- TÍTULO E CABEÇALHO ---
st.title("🚚 SupplyAnalytics — Performance Logística & Vendas")
st.markdown("Painel de monitoramento de nível de serviço (SLA/OTIF), custos de frete e margem financeira da operação.")
st.markdown("---")

# --- MÉTRICAS CHAVE (KPIs) ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_pedidos = len(df_filtrado)
pedidos_entregues = df_filtrado[df_filtrado['status_pedido'] == 'Entregue']
taxa_otif = (df_filtrado['cumpriram_sla'].sum() / len(pedidos_entregues) * 100) if len(pedidos_entregues) > 0 else 0
faturamento_total = df_filtrado['valor_venda'].sum()
lucro_bruto_total = df_filtrado['lucro_bruto'].sum()

kpi1.metric("Total de Pedidos", formatar_inteiro(total_pedidos))
kpi2.metric("SLA / OTIF (% no Prazo)", f"{taxa_otif:.1f}%".replace(".", ","))
kpi3.metric("Faturamento Total", formatar_moeda(faturamento_total))
kpi4.metric("Lucro Bruto Operacional", formatar_moeda(lucro_bruto_total))

st.markdown("---")

# --- GRÁFICOS PRINCIPAIS ---
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("📦 Status das Entregas (SLA)")
    fig_status = px.pie(
        df_filtrado, 
        names='status_sla_detalhado', 
        hole=0.4,
        color='status_sla_detalhado',
        color_discrete_map={
            'Entregue no Prazo': '#2ecc71',
            'Entregue com Atraso': '#e74c3c',
            'Em Trânsito': '#f1c40f',
            'Cancelado': '#95a5a6'
        }
    )
    st.plotly_chart(fig_status, use_container_width=True)

with col_g2:
    st.subheader("💰 Lucro Bruto x Frete por Região")
    df_regiao = df_filtrado.groupby('regiao_destino')[['lucro_bruto', 'custo_frete']].sum().reset_index()
    fig_regiao = px.bar(
        df_regiao, 
        x='regiao_destino', 
        y=['lucro_bruto', 'custo_frete'], 
        barmode='group',
        labels={'value': 'R$', 'regiao_destino': 'Região', 'variable': 'Métrica'},
        color_discrete_map={'lucro_bruto': '#27ae60', 'custo_frete': '#e67e22'}
    )
    st.plotly_chart(fig_regiao, use_container_width=True)

# --- SEGUNDA LINHA DE GRÁFICOS ---
col_g3, col_g4 = st.columns(2)

with col_g3:
    st.subheader("⚖️ Custo Médio do Frete por Kg")
    df_frete_kg = df_filtrado.groupby('categoria')['custo_frete_por_kg'].mean().reset_index().sort_values(by='custo_frete_por_kg', ascending=True)
    fig_frete = px.bar(
        df_frete_kg, 
        x='custo_frete_por_kg', 
        y='categoria', 
        orientation='h',
        labels={'custo_frete_por_kg': 'R$ / Kg', 'categoria': 'Categoria'},
        color='custo_frete_por_kg',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_frete, use_container_width=True)

with col_g4:
    st.subheader("⏱️ Tempo Médio de Trânsito Real (Dias)")
    df_tempo = df_filtrado[df_filtrado['status_pedido'] == 'Entregue'].groupby('regiao_destino')['dias_transito_real'].mean().reset_index()
    fig_tempo = px.bar(
        df_tempo, 
        x='regiao_destino', 
        y='dias_transito_real',
        labels={'dias_transito_real': 'Dias', 'regiao_destino': 'Região'},
        color='dias_transito_real',
        color_continuous_scale='Oranges'
    )
    st.plotly_chart(fig_tempo, use_container_width=True)

# --- VISUALIZAÇÃO DOS DADOS TRATADOS ---
with st.expander("📄 Visualizar Tabela de Dados Filtrados"):
    df_exibicao = df_filtrado[['id_pedido', 'data_compra', 'regiao_destino', 'categoria', 'valor_venda', 'custo_frete', 'dias_transito_real', 'status_sla_detalhado']].copy()
    df_exibicao['valor_venda'] = df_exibicao['valor_venda'].apply(formatar_moeda)
    df_exibicao['custo_frete'] = df_exibicao['custo_frete'].apply(formatar_moeda)
    st.dataframe(df_exibicao, use_container_width=True)