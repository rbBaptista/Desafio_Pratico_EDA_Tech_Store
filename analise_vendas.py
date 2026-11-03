"""Análise exploratória dos dados de vendas da TechStore."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.ticker import FuncFormatter
from openpyxl.worksheet.worksheet import Worksheet

NOME_ARQUIVO = "vendas.csv"
NOME_DIRETORIO_SAIDA = "saidas"

MESES = ["jan", "fev", "mar", "abr", "mai", "jun",
         "jul", "ago", "set", "out", "nov", "dez"]

COR_SERIE = "#2a78d6"
COR_FUNDO = "#fcfcfb"
COR_TEXTO = "#0b0b0b"
COR_TEXTO_SECUNDARIO = "#52514e"
COR_GRADE = "#e5e4e0"
FUNDO_ROTULO = {"facecolor": COR_FUNDO, "edgecolor": "none", "pad": 1.5}

FORMATO_MOEDA_EXCEL = '"R$" #,##0'


def obter_diretorio_base() -> Path:
    """Retorna a pasta do script, ou a pasta atual em notebooks."""
    try:
        return Path(__file__).parent
    except NameError:
        return Path.cwd()


def carregar_dados(caminho: Path) -> pd.DataFrame:
    """Carrega o CSV de vendas e cria a coluna derivada de receita."""
    if not caminho.is_file():
        raise FileNotFoundError(f"Arquivo de dados não encontrado: {caminho}")

    df = pd.read_csv(caminho, parse_dates=["data"], encoding="utf-8")
    df["receita"] = df["quantidade"] * df["preco_unitario"]
    return df


def calcular_receita_total(df: pd.DataFrame) -> int:
    """Retorna a soma da receita de todas as vendas."""
    return int(df["receita"].sum())


def vendas_por_categoria(df: pd.DataFrame, categoria: str) -> pd.DataFrame:
    """Retorna as vendas de uma categoria."""
    return df[df["categoria"] == categoria]


def maiores_totais(df: pd.DataFrame, grupo: str, metrica: str) -> pd.Series:
    """Soma a métrica por grupo e retorna o maior total, incluindo empates."""
    totais = df.groupby(grupo)[metrica].sum()
    return totais[totais == totais.max()]


def produto_mais_vendido(df: pd.DataFrame) -> pd.Series:
    """Retorna o(s) produto(s) com a maior soma de quantidade."""
    return maiores_totais(df, "produto", "quantidade")


def regiao_maior_valor(df: pd.DataFrame) -> pd.Series:
    """Retorna a(s) região(ões) com a maior soma de receita."""
    return maiores_totais(df, "regiao", "receita")


def receita_por_categoria(df: pd.DataFrame) -> pd.Series:
    """Retorna a receita de cada categoria, da maior para a menor."""
    return df.groupby("categoria")["receita"].sum().sort_values(ascending=False)


def receita_por_mes(df: pd.DataFrame) -> pd.Series:
    """Retorna a receita por ano-mês, em ordem cronológica e sem pular meses."""
    meses = df["data"].dt.to_period("M")
    receita = df.groupby(meses)["receita"].sum()
    calendario = pd.period_range(receita.index.min(), receita.index.max(), freq="M")
    return receita.reindex(calendario, fill_value=0)


def tabela_dinamica_receita(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna a receita por região x categoria, com totais."""
    return pd.pivot_table(
        df,
        values="receita",
        index="regiao",
        columns="categoria",
        aggfunc="sum",
        fill_value=0,
        margins=True,
        margins_name="Total",
    )


def formatar_moeda(valor: float) -> str:
    """Formata um valor como moeda, com ponto como separador de milhar."""
    return f"R$ {valor:,.0f}".replace(",", ".")


def rotular_mes(periodo: pd.Period) -> str:
    """Formata um período mensal como jan/25."""
    return f"{MESES[periodo.month - 1]}/{periodo.year % 100:02d}"


def exibir_titulo(titulo: str) -> None:
    """Exibe o título de uma seção da saída."""
    print(f"\n{'=' * 60}\n{titulo}\n{'=' * 60}")


def exibir_informacoes_basicas(df: pd.DataFrame) -> None:
    """Exibe as primeiras linhas, o total de registros e a receita total."""
    exibir_titulo("Primeiras 5 linhas")
    print(df.head().to_string(index=False))

    exibir_titulo("Total de registros e receita total")
    print(f"Total de registros: {len(df)}")
    print(f"Receita total: {formatar_moeda(calcular_receita_total(df))}")


def exibir_vendas_eletronicos(df: pd.DataFrame) -> None:
    """Exibe as vendas da categoria Eletrônicos."""
    vendas = vendas_por_categoria(df, "Eletrônicos")
    exibir_titulo("Vendas da categoria Eletrônicos")
    print(vendas.to_string(index=False))
    print(f"\nTotal de vendas na categoria: {len(vendas)}")


def exibir_produto_mais_vendido(df: pd.DataFrame) -> None:
    """Exibe o(s) produto(s) mais vendido(s) em quantidade."""
    exibir_titulo("Produto mais vendido")
    for produto, quantidade in produto_mais_vendido(df).items():
        print(f"{produto}: {quantidade} unidades")


def exibir_regiao_maior_valor(df: pd.DataFrame) -> None:
    """Exibe a(s) região(ões) com maior valor de compras."""
    exibir_titulo("Região com maior valor de compras")
    for regiao, receita in regiao_maior_valor(df).items():
        print(f"{regiao}: {formatar_moeda(receita)}")


def exibir_tabela_dinamica(df: pd.DataFrame) -> None:
    """Exibe a tabela dinâmica de receita por região x categoria."""
    exibir_titulo("Receita por região x categoria")
    print(tabela_dinamica_receita(df).map(formatar_moeda).to_string())


def exibir_arquivos_gerados(arquivos: list[Path]) -> None:
    """Exibe os caminhos dos gráficos e do relatório."""
    exibir_titulo("Arquivos gerados")
    print("\n".join(str(arquivo) for arquivo in arquivos))


def criar_grafico(titulo: str, rotulo_x: str) -> tuple[plt.Figure, Axes]:
    """Cria uma figura com o estilo comum aos gráficos de receita."""
    figura, eixo = plt.subplots(figsize=(9, 5), facecolor=COR_FUNDO)
    eixo.set_facecolor(COR_FUNDO)
    eixo.set_title(titulo, loc="left", color=COR_TEXTO, fontsize=14, pad=16)
    eixo.set_xlabel(rotulo_x, color=COR_TEXTO_SECUNDARIO, labelpad=8)
    eixo.set_ylabel("Receita (R$)", color=COR_TEXTO_SECUNDARIO, labelpad=8)
    eixo.yaxis.set_major_formatter(FuncFormatter(lambda valor, _: f"{valor:,.0f}".replace(",", ".")))
    eixo.tick_params(colors=COR_TEXTO_SECUNDARIO, length=0)
    eixo.grid(axis="y", color=COR_GRADE, linewidth=0.8)
    eixo.set_axisbelow(True)
    eixo.spines[["top", "right", "left"]].set_visible(False)
    eixo.spines["bottom"].set_color(COR_GRADE)
    return figura, eixo


def salvar_grafico(figura: plt.Figure, caminho: Path) -> Path:
    """Salva o gráfico em arquivo e libera a figura da memória."""
    figura.savefig(caminho, dpi=150, bbox_inches="tight", facecolor=COR_FUNDO)
    plt.close(figura)
    return caminho


def grafico_receita_por_categoria(df: pd.DataFrame, diretorio: Path) -> Path:
    """Gera o gráfico de barras de receita por categoria."""
    receita = receita_por_categoria(df)
    figura, eixo = criar_grafico("Receita por categoria", "Categoria")
    barras = eixo.bar(receita.index, receita.to_numpy(), color=COR_SERIE, width=0.5)
    eixo.bar_label(
        barras,
        labels=receita.map(formatar_moeda).tolist(),
        padding=4,
        color=COR_TEXTO,
        bbox=FUNDO_ROTULO,
    )
    eixo.margins(y=0.12)
    return salvar_grafico(figura, diretorio / "receita_por_categoria.png")


def grafico_vendas_por_mes(df: pd.DataFrame, diretorio: Path) -> Path:
    """Gera o gráfico de linha da receita mensal, destacando o pico e o último mês."""
    receita = receita_por_mes(df)
    rotulos = [rotular_mes(periodo) for periodo in receita.index]
    valores = receita.to_numpy()

    figura, eixo = criar_grafico("Evolução das vendas por mês (receita)", "Mês")
    eixo.plot(rotulos, valores, color=COR_SERIE, linewidth=2, solid_capstyle="round")
    eixo.set_ylim(0, valores.max() * 1.15)
    eixo.margins(x=0.06)

    destaques = sorted({int(valores.argmax()), len(valores) - 1})
    eixo.plot(
        [rotulos[posicao] for posicao in destaques],
        valores[destaques],
        linestyle="none",
        marker="o",
        markersize=8,
        color=COR_SERIE,
        markeredgecolor=COR_FUNDO,
        markeredgewidth=2,
    )
    for posicao in destaques:
        eixo.annotate(
            formatar_moeda(valores[posicao]),
            (posicao, valores[posicao]),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center",
            color=COR_TEXTO,
            bbox=FUNDO_ROTULO,
        )
    return salvar_grafico(figura, diretorio / "vendas_por_mes.png")


def montar_resumo(df: pd.DataFrame) -> pd.DataFrame:
    """Monta os indicadores principais para a aba de resumo do relatório."""
    produtos = produto_mais_vendido(df)
    regioes = regiao_maior_valor(df)
    return pd.DataFrame(
        [
            ("Total de registros", len(df)),
            ("Receita total", calcular_receita_total(df)),
            ("Produto mais vendido", ", ".join(produtos.index)),
            ("Unidades do produto mais vendido", int(produtos.iloc[0])),
            ("Região com maior valor de compras", ", ".join(regioes.index)),
            ("Receita da região com maior valor", int(regioes.iloc[0])),
        ],
        columns=["Indicador", "Valor"],
    )


def formatar_planilha(planilha: Worksheet, colunas_moeda: list[str]) -> None:
    """Aplica formato de moeda, largura das colunas e congelamento do cabeçalho."""
    for coluna in planilha.iter_cols():
        if coluna[0].value in colunas_moeda:
            for celula in coluna[1:]:
                celula.number_format = FORMATO_MOEDA_EXCEL
        largura = max(len(str(celula.value)) for celula in coluna)
        planilha.column_dimensions[coluna[0].column_letter].width = largura + 6
    planilha.freeze_panes = "A2"


def exportar_relatorio(df: pd.DataFrame, diretorio: Path) -> Path:
    """Exporta o resumo, as agregações e as vendas para um arquivo .xlsx."""
    caminho = diretorio / "relatorio_vendas.xlsx"
    categorias = receita_por_categoria(df).rename_axis("Categoria").reset_index(name="Receita")
    meses = receita_por_mes(df)
    por_mes = pd.DataFrame({"Mês": [rotular_mes(mes) for mes in meses.index], "Receita": meses.to_numpy()})
    tabela = tabela_dinamica_receita(df).rename_axis(index="Região", columns=None).reset_index()

    abas = {
        "Resumo": (montar_resumo(df), []),
        "Receita por categoria": (categorias, ["Receita"]),
        "Receita por mês": (por_mes, ["Receita"]),
        "Região x categoria": (tabela, tabela.columns[1:].tolist()),
        "Vendas": (df.assign(data=df["data"].dt.date), ["preco_unitario", "receita"]),
    }

    with pd.ExcelWriter(caminho, engine="openpyxl", date_format="YYYY-MM-DD") as escritor:
        for nome, (dados, colunas_moeda) in abas.items():
            dados.to_excel(escritor, sheet_name=nome, index=False)
            formatar_planilha(escritor.sheets[nome], colunas_moeda)

        for linha in escritor.sheets["Resumo"].iter_rows(min_row=2):
            if "Receita" in linha[0].value:
                linha[1].number_format = FORMATO_MOEDA_EXCEL
    return caminho


def main() -> None:
    """Executa a análise, exibe os resultados e gera gráficos e relatório."""
    try:
        diretorio_base = obter_diretorio_base()
        df = carregar_dados(diretorio_base / NOME_ARQUIVO)
    except FileNotFoundError as erro:
        raise SystemExit(f"Erro: {erro}") from None

    exibir_informacoes_basicas(df)
    exibir_vendas_eletronicos(df)
    exibir_produto_mais_vendido(df)
    exibir_regiao_maior_valor(df)
    exibir_tabela_dinamica(df)

    diretorio_saida = diretorio_base / NOME_DIRETORIO_SAIDA
    diretorio_saida.mkdir(exist_ok=True)
    exibir_arquivos_gerados([
        grafico_receita_por_categoria(df, diretorio_saida),
        grafico_vendas_por_mes(df, diretorio_saida),
        exportar_relatorio(df, diretorio_saida),
    ])


if __name__ == "__main__":
    main()
