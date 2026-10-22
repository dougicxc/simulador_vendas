import streamlit as st
import pandas as pd

# Função auxiliar para formatar os valores em Reais (BRL)
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Função para calcular SAC (Primeira Parcela, Última Parcela e Total Pago)
def calcular_financiamento_sac(principal, taxa_anual, anos):
    if principal <= 0:
        return 0, 0, 0
    meses = anos * 12
    # Conversão de taxa anual para mensal (juros compostos)
    taxa_mensal = (1 + taxa_anual / 100) ** (1 / 12) - 1
    amortizacao = principal / meses
    
    # Primeira parcela: Amortização + Juros sobre o saldo total
    primeira_parcela = amortizacao + (principal * taxa_mensal)
    
    # Última parcela: Amortização + Juros sobre a última cota de amortização
    ultima_parcela = amortizacao + (amortizacao * taxa_mensal)
    
    # Total de Juros (Soma da Progressão Aritmética)
    juros_total = ((principal * taxa_mensal) + (amortizacao * taxa_mensal)) * meses / 2
    total_pago = principal + juros_total
    
    return primeira_parcela, ultima_parcela, total_pago

# Configuração base da página
st.set_page_config(page_title="Simulador de Transição Imobiliária", layout="wide")

st.title("🏡 Simulador de Transição Imobiliária")
st.write("Altere os valores nas caixas abaixo para simular imediatamente novos cenários.")

st.divider()

# 1. Entradas de Dados
st.header("1. Valores de Negociação")
col_v1, col_v2, col_v3 = st.columns(3)
with col_v1:
    venda_apt = st.number_input("Valor de Venda do Apartamento", value=500000.0, step=10000.0, format="%f")
with col_v2:
    venda_casa = st.number_input("Valor de Venda da Casa da Mãe", value=410000.0, step=10000.0, format="%f")
with col_v3:
    compra_nova = st.number_input("Valor da Nova Compra", value=600000.0, step=10000.0, format="%f")

# Lógica e Variáveis Fixas
taxa_corretagem = 0.06
taxa_documentacao = 0.06
quitacao_apt_atual = 140000.00
repasse_pais = 100000.00
reforma_barracao = 50000.00

# Cálculos
corretagem_apt = venda_apt * taxa_corretagem
saldo_douglas_alessandra = venda_apt - corretagem_apt - quitacao_apt_atual - repasse_pais - reforma_barracao

corretagem_casa = venda_casa * taxa_corretagem
saldo_liquido_casa = venda_casa - corretagem_casa

custo_documentacao = compra_nova * taxa_documentacao
entrada_liquida_imovel = saldo_liquido_casa - custo_documentacao
valor_a_financiar = compra_nova - entrada_liquida_imovel

st.divider()

# 2. Exibição dos Resultados
st.header("2. Resultados da Simulação")
col_r1, col_r2, col_r3 = st.columns(3)

with col_r1:
    st.subheader("🏢 Apartamento")
    st.text(f"(-) Corretagem (6%): {formatar_moeda(corretagem_apt)}\n(-) Quitação: {formatar_moeda(quitacao_apt_atual)}\n(-) Repasses/Reformas: {formatar_moeda(repasse_pais + reforma_barracao)}")
    st.metric(label="Saldo Douglas e Alessandra", value=formatar_moeda(saldo_douglas_alessandra))

with col_r2:
    st.subheader("🏠 Casa da Mãe")
    st.text(f"(-) Corretagem (6%): {formatar_moeda(corretagem_casa)}")
    st.metric(label="Saldo para Nova Compra", value=formatar_moeda(saldo_liquido_casa))

with col_r3:
    st.subheader("🔑 Nova Casa")
    st.text(f"Valor do Imóvel: {formatar_moeda(compra_nova)}\n(-) Saldo Casa da Mãe: {formatar_moeda(saldo_liquido_casa)}\n(-) Documentação (6%): {formatar_moeda(custo_documentacao)}")
    st.metric(label="Valor a Financiar", value=formatar_moeda(valor_a_financiar))

st.divider()

# 3. Simulação de Financiamento Comparativa
st.header("3. Comparativo de Financiamento (SAC)")
st.write(f"**Valor base do financiamento:** {formatar_moeda(valor_a_financiar)}")

bancos = ["Inter", "Itaú", "Sicoob", "Caixa Econômica"]
taxas = {}
prazos = {}

# Layout de inputs lado a lado para os bancos
col_b1, col_b2, col_b3, col_b4 = st.columns(4)
colunas_bancos = [col_b1, col_b2, col_b3, col_b4]

for i, banco in enumerate(bancos):
    with colunas_bancos[i]:
        st.markdown(f"**{banco}**")
        taxas[banco] = st.number_input(f"Taxa a.a. (%)", value=10.5, step=0.1, key=f"taxa_{banco}")
        prazos[banco] = st.selectbox(f"Prazo", options=[20, 25, 30], index=0, key=f"prazo_{banco}")

# Processamento da tabela comparativa
resultados = []
for banco in bancos:
    p1, p_ult, total = calcular_financiamento_sac(valor_a_financiar, taxas[banco], prazos[banco])
    resultados.append({
        "Instituição": banco,
        "Prazo": f"{prazos[banco]} anos",
        "Taxa a.a.": f"{taxas[banco]}%",
        "1ª Parcela": formatar_moeda(p1),
        "Última Parcela": formatar_moeda(p_ult),
        "Custo Total Final": formatar_moeda(total)
    })

df_comparativo = pd.DataFrame(resultados)

st.markdown("### Quadro Comparativo")
st.dataframe(df_comparativo, hide_index=True, use_container_width=True)
st.caption("*Obs: Os valores são simulações matemáticas do Sistema SAC e não incluem os seguros habitacionais obrigatórios (MIP e DFI) ou taxas administrativas de cada banco, que encarecem levemente a prestação real.*")