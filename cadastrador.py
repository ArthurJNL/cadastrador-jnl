import streamlit as st
import urllib.parse
from datetime import datetime

# 1. SETUP DA PÁGINA (Ícone alterado para Boleto/Fatura)
st.set_page_config(page_title="Gerador de Análise de Crédito", page_icon="🧾", layout="centered")

# --- DESIGN PREMIUM CLEAN ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Calibri', sans-serif; }
    .main { background-color: #F8F9FB; }
    .stTextInput > div > div > input, .stTextArea > div > textarea, .stSelectbox > div > div {
        border-radius: 8px; border: 1px solid #D0D5DD;
    }
    .chance-alta { color: #10B981; font-weight: bold; font-size: 24px; }
    .chance-media { color: #F59E0B; font-weight: bold; font-size: 24px; }
    .chance-baixa { color: #EF4444; font-weight: bold; font-size: 24px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧾 Análise de Crédito JNL")
st.markdown("Preencha os dados e deixe a inteligência calcular as chances e gerar o relatório limpo.")
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

st.markdown("#### Informações da Venda")
col1, col2 = st.columns(2)
with col1:
    tipo_cliente = st.selectbox("Tipo de Solicitação", ["Cliente novo", "Renovação", "Aumento de limite"])
with col2:
    valor_compra = st.text_input("Valor da Compra (R$)", placeholder="Ex: 9.500,00")

st.markdown("#### 📁 Documentação de Prioridade")
col_doc1, col_doc2 = st.columns(2)
with col_doc1:
    contrato_social = st.selectbox("Contrato Social", ["Enviou", "Já temos", "Faltando"])
with col_doc2:
    notas_fiscais = st.selectbox("Notas Fiscais", ["Enviou", "Já temos", "Faltando"])

# O campo de cobertura SÓ APARECE se as notas existirem!
cobertura_notas = ""
if notas_fiscais in ["Enviou", "Já temos"]:
    cobertura_notas = st.radio("Sobre a Cobertura das Notas:", [
        "As notas cobrem o valor e são faturadas", 
        "As notas NÃO cobrem o valor da compra"
    ])

# Documentos extras para casos em que mandam coisas diferentes
doc_excedentes = st.text_input("Documentos Excedentes (Opcional)", placeholder="Ex: Enviou declaração de faturamento no lugar das notas")

st.markdown("#### 🚨 Análise SPC / Serasa")
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

st.markdown("#### 🎯 Score e Considerações")
col6, col7 = st.columns([1, 3])

with col6:
    score = st.number_input("Score (0 a 1000)", min_value=0, max_value=1000, value=0, step=10)

with col7:
    consideracoes = st.text_area("Considerações finais", placeholder="Ex: Cadastro não aprovado...")

# ==========================================
# MOTOR DE INTELIGÊNCIA (CHANCE DE APROVAÇÃO)
# ==========================================
chance = 50 

# Cálculos da Documentação (PESOS AJUSTADOS PELO COMANDANTE)
if notas_fiscais in ["Enviou", "Já temos"]: 
    chance += 10 # Prioridade Máxima
else: 
    chance -= 15 # Penalidade forte se não tiver faturamento comprovado

if contrato_social in ["Enviou", "Já temos"]: 
    chance += 7 # Formalidade Importante
else: 
    chance -= 7 # Penalidade leve, pode ser cobrado depois

if notas_fiscais in ["Enviou", "Já temos"]:
    if cobertura_notas == "As notas cobrem o valor e são faturadas": chance += 10
    else: chance -= 10

if doc_excedentes.strip(): chance += 5

# Cálculos de Pendências
if tem_pendencia == "Não": chance += 20
else: chance -= 20

# Cálculos de Score
if score >= 700: chance += 20
elif score >= 500: chance += 5
elif score < 300: chance -= 15

# Travar percentagem entre 0 e 100
chance_final = max(0, min(100, chance))

st.markdown("---")
st.markdown("### 📊 Termômetro de Aprovação")
st.progress(chance_final / 100.0)

if chance_final >= 75:
    st.markdown(f"<p class='chance-alta'>🔥 Chance Alta: {chance_final}%</p>", unsafe_allow_html=True)
elif chance_final >= 40:
    st.markdown(f"<p class='chance-media'>⚠️ Chance Média: {chance_final}% (Requer atenção)</p>", unsafe_allow_html=True)
else:
    st.markdown(f"<p class='chance-baixa'>🛑 Chance Baixa: {chance_final}% (Risco elevado)</p>", unsafe_allow_html=True)

# ==========================================
# MONTAGEM DO E-MAIL (O NOVO PADRÃO DE ESPAÇAMENTO)
# ==========================================

# 1. Lógica dos Documentos Principais combinados
if contrato_social == "Enviou" and notas_fiscais == "Enviou":
    txt_docs = "Mandou todos os documentos"
elif contrato_social == "Já temos" and notas_fiscais == "Já temos":
    txt_docs = "Temos todos os documentos"
else:
    partes = []
    # Avaliando Contrato
    if contrato_social == "Faltando": partes.append("Falta o Contrato Social")
    elif contrato_social == "Enviou": partes.append("Enviou o Contrato Social")
    else: partes.append("Já temos o Contrato Social")
    # Avaliando Notas
    if notas_fiscais == "Faltando": partes.append("Faltam as Notas Fiscais")
    elif notas_fiscais == "Enviou": partes.append("Enviou as Notas Fiscais")
    else: partes.append("Já temos as Notas Fiscais")
    
    txt_docs = " e ".join(partes)

# 2. Lógica das Pendências
if tem_pendencia == "Não":
    txt_pendencias = "Nenhuma pendência registrada"
else:
    plural = "pendência" if int(qtd_pendencias) == 1 else "pendências"
    txt_pendencias = f"{qtd_pendencias} {plural} de R$ {valor_pendencia}"
    if detalhe_pendencia:
        txt_pendencias += f" ({detalhe_pendencia})"

# 3. Montando a estrutura final em blocos para garantir 1 linha branca entre eles
linhas_email = []
linhas_email.append(f"{destinatario}, {saudacao}! Espero que esteja bem.")
linhas_email.append("Segue análise de crédito para aprovação.")
linhas_email.append(f"{tipo_cliente};")
linhas_email.append(f"Compra de R$ {valor_compra};")
linhas_email.append(f"{txt_docs};")

# Se houver documentos excedentes, ganha uma linha própria
if doc_excedentes.strip():
    linhas_email.append(f"Documentos excedentes: {doc_excedentes};")

# Se as notas existirem, a resposta da cobertura ganha uma linha própria
if notas_fiscais in ["Enviou", "Já temos"]:
    linhas_email.append(f"{cobertura_notas};")

linhas_email.append(f"{txt_pendencias}.")
linhas_email.append(f"Score de {score}.")
linhas_email.append(f"Considerações finais: {consideracoes}")

# O SEGREDO: Juntar todos os blocos com "\n\n" (Duas quebras de linha formam o espaço desejado)
email_texto = "\n\n".join(linhas_email)

st.markdown("---")
st.markdown("### 📋 E-mail Gerado")

# Exibe o texto de forma limpa, botão nativo de copiar no canto
st.code(email_texto, language='text')

# 4. BOTÕES DE AÇÃO
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    st.download_button(
        label="💾 SALVAR TEXTO COMO .TXT",
        data=email_texto,
        file_name=f"Analise_{destinatario}_{datetime.now().strftime('%d%m')}.txt",
        mime="text/plain",
        use_container_width=True
    )

with col_btn2:
    assunto_codificado = urllib.parse.quote("ANÁLISE DE CRÉDITO")
    corpo_codificado = urllib.parse.quote(email_texto)
    link_outlook = f"mailto:?subject={assunto_codificado}&body={corpo_codificado}"
    
    st.markdown(
        f"""
        <a href="{link_outlook}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #0078D4; color: white; padding: 10px; text-align: center; border-radius: 8px; font-weight: bold; font-family: Calibri;">
                ✉️ ABRIR DIRETO NO OUTLOOK
            </div>
        </a>
        """, 
        unsafe_allow_html=True
    )