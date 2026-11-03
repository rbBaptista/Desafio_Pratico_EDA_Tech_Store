# CLAUDE.md — Análise de Vendas TechStore

## Visão geral

Sistema de análise exploratória de dados de vendas da empresa fictícia **TechStore**, feito do zero em Python a partir do arquivo `vendas.csv`. O objetivo é carregar os dados, exibir informações básicas, responder perguntas de negócio com consultas e, opcionalmente, gerar gráficos e relatórios.

Idioma do projeto: **português (pt-BR)** — comentários, docstrings, mensagens de saída, títulos de gráficos e nomes de variáveis/funções.

## Stack

- Python 3.10+
- `pandas` — leitura, filtros e agregações
- `matplotlib` — gráficos (desafio extra)
- `openpyxl` — exportação `.xlsx` (extra opcional)
- `reportlab` — exportação `.pdf` (extra opcional, só se o `.xlsx` não bastar)

Instalação: `pip install pandas matplotlib openpyxl`

## Como executar

```bash
python analise_vendas.py
```

- O `vendas.csv` deve estar no mesmo diretório do script.
- O script também precisa funcionar no Google Colab / Jupyter. Se for entregue como notebook, manter o mesmo código dividido em células (`analise_vendas.ipynb`), sem lógica diferente do `.py`.
- Caminhos de arquivo: usar `pathlib.Path(__file__).parent` (com fallback para `Path.cwd()` quando `__file__` não existir, como em notebooks), nunca caminhos absolutos.

## Estrutura esperada

```
.
├── CLAUDE.md
├── vendas.csv            # dados de entrada (não alterar)
├── analise_vendas.py     # script principal
└── saidas/               # gráficos e relatórios gerados (criado pelo script)
    ├── receita_por_categoria.png
    ├── vendas_por_mes.png
    └── relatorio_vendas.xlsx
```

## Modelo de dados real do `vendas.csv`

Atenção: o enunciado original descreve o arquivo de forma um pouco diferente do que ele realmente contém. **Vale o que está no arquivo**.

| Coluna           | Tipo      | Observações |
|------------------|-----------|-------------|
| `data`           | data      | Formato `YYYY-MM-DD`; vai de 2025-01-04 a 2025-12-31. No enunciado aparece como `data_venda`. |
| `produto`        | string    | 20 produtos distintos (ex.: Notebook X, Sofá Q, Camisa R). |
| `categoria`      | string    | 4 valores: `Eletrônicos`, `Móveis`, `Periféricos`, `Vestuário`. |
| `quantidade`     | inteiro   | |
| `preco_unitario` | inteiro   | No enunciado consta como float; no arquivo são inteiros. Não assumir casas decimais. |
| `cliente`        | string    | Coluna extra, não citada no enunciado. Manter no DataFrame. |
| `regiao`         | string    | 5 valores: Norte, Nordeste, Centro-Oeste, Sudeste, Sul. |

Fatos verificados: 100 linhas, 7 colunas, nenhum valor nulo.

Regras ao carregar:
- Usar `pd.read_csv("vendas.csv", parse_dates=["data"])`.
- Não renomear `data` para `data_venda` no arquivo; se preferir o nome do enunciado, renomear só em memória (`df.rename(columns={"data": "data_venda"})`) e manter coerente no código inteiro.
- Criar a coluna derivada `receita = quantidade * preco_unitario` logo após o carregamento e reutilizá-la em todas as análises.
- Acentos: ler com `encoding="utf-8"` explícito.

## Requisitos funcionais

### Obrigatórios

1. **Carregar** os dados de `vendas.csv`.
2. **Informações básicas**
   - Exibir as 5 primeiras linhas (`df.head()`).
   - Exibir o número total de registros.
   - Calcular e exibir a receita total (`quantidade × preco_unitario`, somada).
3. **Consultas específicas**
   - Filtrar e exibir as vendas da categoria `"Eletrônicos"`.
   - Identificar e exibir o **produto mais vendido em quantidade** (somar `quantidade` por produto, não contar linhas).
   - Identificar e exibir a **região com maior valor de compras** (somar `receita` por região).

### Desafio extra (opcional)

- Gráfico de **barras**: receita por categoria.
- Gráfico de **linha**: evolução das vendas por mês (agrupar por mês de `data`; indicar no título/eixo se a métrica é receita ou quantidade — preferir receita).
- Relatório exportado em `.xlsx` (ou `.pdf`).
- **Tabela dinâmica** de receita por região × categoria (`pd.pivot_table`, com `aggfunc="sum"` e totais via `margins=True`).

## Convenções de código

- Um único arquivo `analise_vendas.py`, organizado em funções pequenas e com uma responsabilidade cada, por exemplo: `carregar_dados`, `exibir_informacoes_basicas`, `vendas_por_categoria`, `produto_mais_vendido`, `regiao_maior_valor`, `grafico_receita_por_categoria`, `grafico_vendas_por_mes`, `exportar_relatorio`, `main`.
- Entrada do script em `if __name__ == "__main__": main()`.
- Funções de consulta **retornam** valores/DataFrames; a impressão fica em `main` ou em funções `exibir_*`. Isso facilita testar e reaproveitar em notebook.
- Seguir PEP 8, com type hints simples e docstrings curtas em português.
- Moeda: formatar como `R$ 1.234.567` (separador de milhar com ponto) apenas na exibição; manter números puros nos cálculos.
- Gráficos: sempre com título, rótulos de eixos, e salvos em `saidas/` com `plt.savefig(..., dpi=150, bbox_inches="tight")`; chamar `plt.close()` depois. Não depender de `plt.show()` para o script rodar no terminal.
- Não usar loops manuais onde uma operação do pandas resolve (`groupby`, `sum`, `idxmax`).
- Criar `saidas/` com `Path.mkdir(exist_ok=True)`.

## Cuidados e armadilhas

- **Produto mais vendido** = maior soma de `quantidade`, não maior número de linhas nem maior receita.
- **Região com maior valor de compras** = maior soma de `receita`, não de `quantidade`.
- Tratar empates em `idxmax` mostrando todos os empatados, ou ao menos deixar explícito qual critério de desempate foi usado.
- A ordem cronológica dos meses no gráfico de linha deve ser a do calendário (usar `dt.to_period("M")` ou `dt.month`), não ordem alfabética.
- Todos os dados são de 2025; agrupar por mês sem separar por ano é aceitável, mas se o dataset mudar, agrupar por ano-mês.
- Não modificar o `vendas.csv`; qualquer limpeza acontece em memória.
- Se o arquivo não for encontrado, falhar com mensagem clara em português em vez de traceback cru.

## Saída esperada no terminal

Seções separadas por títulos legíveis, nesta ordem:

1. Primeiras 5 linhas
2. Total de registros e receita total
3. Vendas da categoria Eletrônicos
4. Produto mais vendido (com a quantidade)
5. Região com maior valor de compras (com o valor)
6. (Extra) Caminhos dos gráficos e do relatório gerados

## Definição de pronto

- `python analise_vendas.py` roda sem erros a partir de um diretório limpo com apenas o `vendas.csv` e o script.
- Todos os requisitos obrigatórios aparecem na saída.
- Os resultados batem com uma conferência independente (ex.: soma manual em `pandas` ou planilha).
- Se os extras forem feitos, os arquivos aparecem em `saidas/` e abrem corretamente.
