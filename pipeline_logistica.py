import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def gerar_dados_brutos(n_registros=1000):
    """Gera uma base sintética de vendas e logística para simulação do pipeline."""
    np.random.seed(42)
    
    regioes = ['Nordeste', 'Sudeste', 'Sul', 'Norte', 'Centro-Oeste']
    status_possiveis = ['Entregue', 'Entregue', 'Entregue', 'Em Transito', 'Cancelado']
    categorias = ['Eletrônicos', 'Móveis', 'Vestuário', 'Alimentos', 'Ferramentas']
    
    data_inicio = datetime(2026, 1, 1)
    
    dados = []
    for i in range(1, n_registros + 1):
        id_pedido = f"PED-{10000 + i}"
        data_compra = data_inicio + timedelta(days=int(np.random.randint(0, 200)))
        regiao = np.random.choice(regioes)
        categoria = np.random.choice(categorias)
        
        # Valores financeiros e físicos
        valor_venda = round(float(np.random.uniform(50.0, 3500.0)), 2)
        custo_produto = round(valor_venda * np.random.uniform(0.4, 0.7), 2)
        peso_kg = round(float(np.random.uniform(0.5, 50.0)), 2)
        
        # Prazos e Logística
        prazo_estimado_dias = int(np.random.randint(2, 15))
        data_previsao = data_compra + timedelta(days=prazo_estimado_dias)
        
        status = np.random.choice(status_possiveis)
        
        if status == 'Entregue':
            # Simula atraso ou pontualidade no envio
            dias_reais = prazo_estimado_dias + int(np.random.choice([-2, -1, 0, 0, 0, 1, 2, 4, 6]))
            data_entrega = data_compra + timedelta(days=max(1, dias_reais))
        else:
            data_entrega = None
            
        custo_frete = round(peso_kg * np.random.uniform(1.5, 4.5) + np.random.uniform(10, 30), 2)
        
        dados.append({
            'id_pedido': id_pedido,
            'data_compra': data_compra.strftime('%Y-%m-%d'),
            'regiao_destino': regiao,
            'categoria': categoria,
            'valor_venda': valor_venda,
            'custo_produto': custo_produto,
            'custo_frete': custo_frete,
            'peso_kg': peso_kg,
            'data_previsao_entrega': data_previsao.strftime('%Y-%m-%d'),
            'data_entrega_real': data_entrega.strftime('%Y-%m-%d') if data_entrega else None,
            'status_pedido': status
        })
    
    df_raw = pd.DataFrame(dados)
    
    # Injeta alguns valores nulos/sujos para testar a etapa de limpeza do ETL
    df_raw.loc[df_raw.sample(frac=0.02, random_state=42).index, 'custo_frete'] = np.nan
    
    return df_raw


def executar_pipeline_etl():
    """Executa as etapas de Extração, Transformação e Carga (ETL)."""
    print("🚀 Iniciando Pipeline ETL Logístico...")
    
    # --- 1. EXTRAÇÃO ---
    print("📥 [1/3] Extraindo dados brutos...")
    df = gerar_dados_brutos(n_registros=1200)
    
    # --- 2. TRANSFORMAÇÃO ---
    print("🔄 [2/3] Transformando e limpando dados...")
    
    # Trata valores nulos de frete pela média da região
    df['custo_frete'] = df.groupby('regiao_destino')['custo_frete'].transform(lambda x: x.fillna(x.mean()))
    
    # Conversão de datas
    df['data_compra'] = pd.to_datetime(df['data_compra'])
    df['data_previsao_entrega'] = pd.to_datetime(df['data_previsao_entrega'])
    df['data_entrega_real'] = pd.to_datetime(df['data_entrega_real'])
    
    # Engenharia de Recursos / Métricas Financeiras
    df['receita_liquida'] = df['valor_venda'] - df['custo_produto']
    df['lucro_bruto'] = df['receita_liquida'] - df['custo_frete']
    df['margem_lucro_pct'] = round((df['lucro_bruto'] / df['valor_venda']) * 100, 2)
    df['custo_frete_por_kg'] = round(df['custo_frete'] / df['peso_kg'], 2)
    
    # Métricas de SLA e Logística
    df['dias_prazo_prometido'] = (df['data_previsao_entrega'] - df['data_compra']).dt.days
    
    # Tempo real de entrega (apenas para entregues)
    df['dias_transito_real'] = (df['data_entrega_real'] - df['data_compra']).dt.days
    
    # SLA de Entrega (1 = No prazo / 0 = Atrasado)
    df['cumpriram_sla'] = np.where(
        df['status_pedido'] == 'Entregue',
        np.where(df['data_entrega_real'] <= df['data_previsao_entrega'], 1, 0),
        0
    )
    
    # Classificação do status logístico
    conditions = [
        (df['status_pedido'] == 'Cancelado'),
        (df['status_pedido'] == 'Em Transito'),
        (df['status_pedido'] == 'Entregue') & (df['cumpriram_sla'] == 1),
        (df['status_pedido'] == 'Entregue') & (df['cumpriram_sla'] == 0)
    ]
    choices = ['Cancelado', 'Em Trânsito', 'Entregue no Prazo', 'Entregue com Atraso']
    df['status_sla_detalhado'] = np.select(conditions, choices, default='Indefinido')

    # --- 3. CARGA (CARREGAMENTO) ---
    print("💾 [3/3] Exportando dados tratados...")
    nome_arquivo_saida = "dados_logistica_tratados.csv"
    df.to_csv(nome_arquivo_saida, index=False, encoding='utf-8')
    
    print(f"✅ Pipeline concluído com sucesso! Base salva como '{nome_arquivo_saida}'.")
    
    # Resumo rápido no terminal
    tot_pedidos = len(df)
    pedidos_entregues = df[df['status_pedido'] == 'Entregue']
    taxa_otif = round((df['cumpriram_sla'].sum() / len(pedidos_entregues)) * 100, 2)
    lucro_total = round(df['lucro_bruto'].sum(), 2)
    
    print("\n--- RESUMO DA OPERAÇÃO ---")
    print(f"Total de Pedidos Processados: {tot_pedidos}")
    print(f"Taxa de Entregas no Prazo (OTIF): {taxa_otif}%")
    print(f"Lucro Bruto Total: R$ {lucro_total:,.2f}")


if __name__ == "__main__":
    executar_pipeline_etl()