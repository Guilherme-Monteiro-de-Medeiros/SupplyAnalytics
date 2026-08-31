# 🚚 SupplyAnalytics — Performance Logística & SLA Dashboard

O **SupplyAnalytics** é um painel interativo focado no monitoramento de níveis de serviço (SLA/OTIF), eficiência de frete e margem financeira operacional. A solução conecta o tratamento automatizado de dados (ETL em Python/Pandas) à exibição visual de KPIs estratégicos via Streamlit.

---

## 📌 Funcionalidades Principais

* **Pipeline ETL Automatizado:** Extração, limpeza, engenharia de atributos (cálculo de OTIF/SLA e margem operacional) e exportação tratada.
* **Indicadores em Tempo Real (KPIs):**
  * Total de Pedidos Processados
  * Taxa de SLA / OTIF (% de entregas no prazo)
  * Faturamento Total (R$)
  * Lucro Bruto Operacional (R$)
* **Filtros Dinâmicos:** Filtragem por Região de Destino, Categoria de Produto e Status do Pedido.
* **Análises Gráficas Interativas:**
  * Distribuição dos Status das Entregas (Prazo/Atraso/Cancelado).
  * Comparativo de Lucro Bruto vs. Custo de Frete por Região.
  * Custo Médio do Frete por Kg por Categoria.
  * Tempo Médio de Trânsito Real (Lead Time) por Região.

---

## 🛠️ Tecnologias Utilizadas

* **Python 3.10+** — Linguagem base da aplicação.
* **Pandas** — Processamento, transformação e limpeza de dados (ETL).
* **Streamlit** — Construção da interface do Dashboard web.
* **Plotly Express** — Gráficos interativos e responsivos.

---

## 📁 Estrutura do Projeto

```text
SupplyAnalytics/
│
├── pipeline_logistica.py        # Script de ETL (Extração, Tratamento e Exportação)
├── app.py                      # Aplicação web Streamlit e visualizações
├── dados_logistica_tratados.csv # Base de dados processada pelo pipeline
├── requirements.txt            # Dependências do projeto
└── README.md                   # Documentação do repositório
```

1. Clonar o repositório
```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd SupplyAnalytics
```

2. Instalar as dependências
```bash
pip install -r requirements.txt
```

3. Processar os dados (Pipeline ETL)
```bash
python pipeline_logistica.py
```

4. Executar o Dashboard Streamlit
```bash
python -m streamlit run app.py
```

O dashboard abrirá automaticamente no seu navegador no endereço http://localhost:8501.