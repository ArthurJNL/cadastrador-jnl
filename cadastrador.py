import streamlit as st
import urllib.parse
from datetime import datetime

# 1. SETUP DA PÁGINA
st.set_page_config(page_title="Gerador de Cadastro", page_icon="💳", layout="centered")

# --- DESIGN PREMIUM CLEAN ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Calibri', sans-serif; }
    .main { background-color: #F8F9FB; }
    .stTextInput > div > div > input, .stTextArea > div > textarea, .stSelectbox > div > div {
        border-radius: 8px; border: 1px solid #D0D5DD;
    }
    .stButton > button {
        background-color: #111111; color: white; border-radius: 8px; font-weight: bold; width: 100%;
    }
    .stButton > button:hover {
        background-color: #333333; color: white; border-color: #111111;
    }
    .caixa-resultado {
        background-color: white; border: 1px solid #E0E4E8; border-radius: 12px; padding: 20px;
        font-family: 'Calibri', sans-serif; font-size: 15px; color: #1A1C1E; white-space: pre-wrap;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💳 Gerador de Análise de Crédito")
st.markdown("Preencha os dados abaixo para gerar o padrão de e-mail automaticamente.")
st.markdown("---")

# 2. DEFINIÇÃO DA SAUDAÇÃO AUTOMÁTICA
hora_atual = datetime.now().hour
saudacao_sugerida = "bom dia" if hora_atual < 12 else "boa tarde"

# 3. FORMULÁRIO DE PREENCHIMENTO
col1, col2 = st.columns(2)

with col1:
    saudacao = st.selectbox("Saudação", ["bom dia", "boa tarde"], index=0 if saudacao_sugerida == "bom dia" else 1)
    tipo_cliente = st.selectbox("Tipo de Solicitação", ["Cliente novo", "Renovação", "Aumento de limite"])
    valor_compra = st.text_input("Valor da Compra (R$)", placeholder="Ex: 9.500,00")

with col2:
    status_doc = st.selectbox("Status dos Documentos", [
        "Mandou todos os documentos",
        "Temos todos os documentos",
        "Faltam documentos (Especificar)"
    ])
    
    docs_extra = ""
    if status_doc == "Faltam documentos (Especificar)":
        docs_extra = st.text_input("Quais documentos faltam?", placeholder="Ex: Faltam as notas fiscais")

st.markdown("#### Análise SPC / Serasa")
col3, col4, col5 = st.columns([1, 1, 2])

with col3:
    tem_pendencia = st.radio("Possui pendências?", ["Não", "Sim"])

with col4:
    if tem_pendencia == "Sim":
        qtd_pendencias = st.number_input("Quantas?", min_value=1, step=1)
    else:
        qtd_pendencias = 0

with col5:
    if tem_pendencia == "Sim":
        valor_pendencia = st.text_input("Valor da(s) pendência(s) (R$)", placeholder="Ex: 34,37")
        detalhe_pendencia = st.text_input("Detalhes da pendência", placeholder="Ex: Protesto da KALUNGA")

st.markdown("#### Score e Considerações")
col6, col7 = st.columns([1, 3])

with col6:
    score = st.text_input("Score", placeholder="Ex: 850")

with col7:
    consideracoes = st.text_area("Considerações finais", placeholder="Ex: Cadastro aprovado mesmo com pendência da KALUNGA, cliente antigo...")

# 4. BOTÃO DE GERAÇÃO
if st.button("⚙️ Gerar Análise de Crédito"):
    
    # Montagem do texto das pendências
    if tem_pendencia == "Não":
        txt_pendencias = "Sem pendências registradas."
    else:
        plural = "pendência" if int(qtd_pendencias) == 1 else "pendências"
        txt_pendencias = f"{qtd_pendencias} {plural} de R$ {valor_pendencia}"
        if detalhe_pendencia:
            txt_pendencias += f" ({detalhe_pendencia})"
            
    # Montagem do texto de documentos
    if status_doc == "Faltam documentos (Especificar)":
        txt_documentos = docs_extra
    else:
        txt_documentos = status_doc

    # MONTAGEM FINAL DO E-MAIL
    email_texto = f"""Jé, {saudacao}! Espero que esteja bem.
Segue análise de crédito para aprovação.

{tipo_cliente};
Compra de R$ {valor_compra};
{txt_documentos};
{txt_pendencias}.
Score de {score}.

Considerações finais: {consideracoes}"""

    st.markdown("### 📋 E-mail Gerado:")
    
    # Exibe o texto numa caixa bonita para copiar facilmente
    st.markdown(f'<div class="caixa-resultado">{email_texto}</div>', unsafe_allow_html=True)
    
    # LÓGICA DO BOTÃO PARA ABRIR O OUTLOOK DIRETO
    assunto_codificado = urllib.parse.quote("ANÁLISE DE CRÉDITO")
    corpo_codificado = urllib.parse.quote(email_texto)
    
    link_outlook = f"mailto:?subject={assunto_codificado}&body={corpo_codificado}"
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <a href="{link_outlook}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #0078D4; color: white; padding: 12px; text-align: center; border-radius: 8px; font-weight: bold; font-family: Calibri;">
                ✉️ ABRIR DIRETO NO OUTLOOK
            </div>
        </a>
        """, 
        unsafe_allow_html=True
    )