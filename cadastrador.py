import streamlit as st
import urllib.parse
from datetime import datetime

# 1. SETUP DA PÁGINA
st.set_page_config(page_title="Gerador de Análise de Crédito", page_icon="💳", layout="centered")

# --- DESIGN PREMIUM CLEAN ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Calibri', sans-serif; }
    .main { background-color: #F8F9FB; }
    .stTextInput > div > div > input, .stTextArea > div > textarea, .stSelectbox > div > div {
        border-radius: 8px; border: 1px solid #D0D5DD;
    }
    /* Estilo para a métrica da barra de progresso */
    .chance-alta { color: #10B981; font-weight: bold; font-size: 24px; }
    .chance-media { color: #F59E0B; font-weight: bold; font-size: 24px; }
    .chance-baixa { color: #EF4444; font-weight: bold; font-size: 24px; }
    </style>
    """, unsafe_allow_html=True)

st.title("💳 Análise de Crédito JNL")
st.markdown("Preencha os dados e deixe a inteligência calcular as chances e gerar o relatório.")
st.markdown("---")

# 2. DEFINIÇÃO DA SAUDAÇÃO AUTOMÁTICA
hora_atual = datetime.now().hour
saudacao_sugerida = "bom dia" if hora_atual < 12 else "boa tarde"

# 3. FORMULÁRIO DE PREENCHIMENTO
col_dest1, col_dest2 = st.columns(2)
with col_dest1:
    destinatario = st.text_input("Para quem enviar?", value="Jé")
with col_dest2:
    saudacao = st.selectbox("Saudação", ["bom dia", "boa tarde"], index=0 if saudacao_sugerida == "bom dia" else 1)

col1, col2 = st.columns(2)
with col1:
    tipo_cliente = st.selectbox("Tipo de Solicitação", ["Cliente novo", "Renovação", "Aumento de limite"])
    valor_compra = st.text_input("Valor da Compra (R$)", placeholder="Ex: 9.500,00")
with col2:
    status_doc = st.selectbox("Status dos Documentos", [
        "Mandou todos os documentos",
        "Temos todos os documentos",
        "Faltam documentos"
    ])
    status_notas = st.selectbox("Análise das Notas Fiscais", [
        "As notas cobrem o valor e são faturadas",
        "As notas NÃO cobrem o valor da compra",
        "Não enviou notas fiscais / Não se aplica"
    ])

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
        detalhe_pendencia = st.text_input("Detalhes", placeholder="Ex: Protesto da KALUNGA")

st.markdown("#### Score e Considerações")
col6, col7 = st.columns([1, 3])

with col6:
    score = st.number_input("Score (0 a 1000)", min_value=0, max_value=1000, value=500, step=10)

with col7:
    consideracoes = st.text_area("Considerações finais", placeholder="Ex: Cadastro aprovado mesmo com pendência, cliente antigo...")

# ==========================================
# MOTOR DE INTELIGÊNCIA (CHANCE DE APROVAÇÃO)
# ==========================================
chance = 50 # Base de início

# Lógica dos Documentos
if status_doc in ["Mandou todos os documentos", "Temos todos os documentos"]: chance += 15
else: chance -= 20

# Lógica das Notas Fiscais
if status_notas == "As notas cobrem o valor e são faturadas": chance += 15
elif status_notas == "As notas NÃO cobrem o valor da compra": chance -= 15
else: chance -= 5

# Lógica de Pendências
if tem_pendencia == "Não": chance += 20
else: chance -= 30

# Lógica de Score
if score >= 700: chance += 20
elif score >= 500: chance += 5
elif score < 300: chance -= 20

# Trava a chance entre 0 e 100
chance_final = max(0, min(100, chance))

st.markdown("---")
st.markdown("### 📊 Termômetro de Aprovação")

# Mostra a barra visual
st.progress(chance_final / 100.0)

# Formata a cor e a mensagem dependendo do valor
if chance_final >= 75:
    st.markdown(f"<p class='chance-alta'>🔥 Chance Alta: {chance_final}%</p>", unsafe_allow_html=True)
elif chance_final >= 40:
    st.markdown(f"<p class='chance-media'>⚠️ Chance Média: {chance_final}% (Requer atenção)</p>", unsafe_allow_html=True)
else:
    st.markdown(f"<p class='chance-baixa'>🛑 Chance Baixa: {chance_final}% (Risco elevado)</p>", unsafe_allow_html=True)


# ==========================================
# MONTAGEM DO E-MAIL
# ==========================================
# Montagem do texto das notas
txt_notas = f"{status_notas}"

# Montagem do texto das pendências
if tem_pendencia == "Não":
    txt_pendencias = "Nenhuma pendência registrada"
else:
    plural = "pendência" if int(qtd_pendencias) == 1 else "pendências"
    txt_pendencias = f"{qtd_pendencias} {plural} de R$ {valor_pendencia}"
    if detalhe_pendencia:
        txt_pendencias += f" ({detalhe_pendencia})"

# TEXTO FINAL EXATO COM QUEBRAS DE LINHA (1 linha por tópico)
email_texto = f"""{destinatario}, {saudacao}! Espero que esteja bem.
Segue análise de crédito para aprovação.

{tipo_cliente};
Compra de R$ {valor_compra};
{status_doc};
{txt_notas};
{txt_pendencias}.
Score de {score}.

Considerações finais: {consideracoes}"""

st.markdown("---")
st.markdown("### 📋 E-mail Gerado")

# Exibe o texto numa caixa onde é fácil de ler e tem botão de copiar
st.code(email_texto, language='text')

st.write("💡 *Dica: Pode clicar no ícone de copiar no canto superior direito da caixa preta acima, ou usar os botões abaixo.*")

# 4. BOTÕES DE AÇÃO PREMIUM
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    # BOTÃO PARA BAIXAR (.TXT) COM O FORMATO EXATO
    st.download_button(
        label="💾 SALVAR TEXTO COMO .TXT",
        data=email_texto,
        file_name=f"Analise_{destinatario}_{datetime.now().strftime('%d%m')}.txt",
        mime="text/plain",
        use_container_width=True
    )

with col_btn2:
    # BOTÃO PARA ABRIR NO OUTLOOK
    assunto_codificado = urllib.parse.quote("ANÁLISE DE CRÉDITO")
    corpo_codificado = urllib.parse.quote(email_texto)
    link_outlook = f"mailto:?subject={assunto_codificado}&body={corpo_codificado}"
    
    st.markdown(
        f"""
        <a href="{link_outlook}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #0078D4; color: white; padding: 10px; text-align: center; border-radius: 8px; font-weight: bold; font-family: Calibri; transition: 0.3s;">
                ✉️ ABRIR DIRETO NO OUTLOOK
            </div>
        </a>
        """, 
        unsafe_allow_html=True
    )