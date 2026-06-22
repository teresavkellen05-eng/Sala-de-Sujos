import streamlit as st
import plotly.express as px
import pandas as pd
import math
from datetime import datetime

# ==========================================
# CONFIGURAÇÃO VISUAL DA PÁGINA (Tema Escuro)
# ==========================================
st.set_page_config(page_title="GLSMED Center · Sala de Sujos", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');
    
    body, .stApp { 
        background-color: #0F1923; 
        color: #E2EAF4;
        font-family: 'IBM Plex Sans', sans-serif;
    }
    
    div[data-testid="stMetricValue"] { 
        font-family: 'IBM Plex Mono', monospace; 
        font-size: 26px !important; 
        font-weight: 600;
    }
    
    .title-mark { 
        background-color: #00C6B8; 
        color: #0F1923; 
        padding: 5px 10px; 
        border-radius: 6px; 
        font-weight: bold;
        font-family: 'IBM Plex Mono', monospace;
    }
    
    .custom-card {
        background-color: #162130;
        border: 1px solid #243447;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# CONSTANTES REAIS (IDÊNTICAS AO JAVASCRIPT)
# ==========================================
TAXA_A_CX = 462.5
TAXA_B_CX = {"S": 45.80152672, "M": 32.0855615, "L": 12.605042015, "XL": 5.221932113}
TAXA_C_CX = 3.368704733
TAXA_D_CX_PICK = 21.96997437
TAXA_D_CX_CARGA = 27.54820937
TAXA_PREL_CX = 63.75
TAXA_B_IND = 6.801
TAXA_C_IND = 3.332
TAXA_D_IND = 27.548

TAB_CX = {"S": 1, "M": 1, "L": 2, "XL": 3}
TAB_RACK = 15
MAX_B_CX = 6
MAX_C_CX = 2
OPS_A_PICK = 1
OPS_B_IND = 3
OPS_C_IND = 1

VEL = 0.6
T_B_H = (6.0 / VEL) / 3600
T_D_H = (3.0 / VEL) / 3600
MANGAS_CONTENTOR = 45
MANGAS_POR_TAB = {"S": 19, "M": 11, "L": 4}

MAQ = [
    {"id": 'M1', "ciclo_h": 1.0, "cor": '#7C5CBF'},
    {"id": 'M2', "ciclo_h": 1.0, "cor": '#0089FF'},
    {"id": 'M3', "ciclo_h": 1.0, "cor": '#00C6B8'},
    {"id": 'M4', "ciclo_h": 0.5, "cor": '#FF9D3D'},
    {"id": 'M5', "ciclo_h": 0.5, "cor": '#E91E8C'}
]

COR_CX = '#0089FF'
COR_IND = '#E07B39'

DIA_SEMANA = {
    0: {"nome": 'Segunda', "totalContentores": 37, "contCamiao": 4, "mixS": 26.1, "mixM": 64.8, "mixL": 9.1, "porViagem": {"V1":4,"V2":5,"V3":7,"V4":3,"V5":6,"V6":4,"V7":1,"V8":5,"V9":2}},
    1: {"nome": 'Terça', "totalContentores": 69, "contCamiao": 8, "mixS": 24.5, "mixM": 65.8, "mixL": 9.7, "porViagem": {"V1":8,"V2":9,"V3":14,"V4":6,"V5":11,"V6":7,"V7":2,"V8":9,"V9":3}},
    2: {"nome": 'Quarta', "totalContentores": 59, "contCamiao": 7, "mixS": 28.6, "mixM": 62.4, "mixL": 9.0, "porViagem": {"V1":7,"V2":7,"V3":14,"V4":5,"V5":9,"V6":6,"V7":2,"V8":7,"V9":2}},
    3: {"nome": 'Quinta', "totalContentores": 64, "contCamiao": 7, "mixS": 29.5, "mixM": 60.1, "mixL": 10.4, "porViagem": {"V1":7,"V2":8,"V3":15,"V4":5,"V5":10,"V6":6,"V7":2,"V8":8,"V9":3}},
    4: {"nome": 'Sexta', "totalContentores": 58, "contCamiao": 6, "mixS": 27.4, "mixM": 62.7, "mixL": 9.9, "porViagem": {"V1":6,"V2":7,"V3":14,"V4":5,"V5":9,"V6":6,"V7":2,"V8":7,"V9":2}},
    5: {"nome": 'Sábado', "totalContentores": 35, "contCamiao": 4, "mixS": 18.7, "mixM": 69.5, "mixL": 11.8, "porViagem": {"V1":4,"V2":4,"V3":10,"V4":3,"V5":5,"V6":3,"V7":1,"V8":4,"V9":1}},
    6: {"nome": 'Domingo', "totalContentores": 4, "contCamiao": 0, "mixS": 7.0, "mixM": 71.9, "mixL": 21.1, "porViagem": {"V1":0,"V2":0,"V3":3,"V4":0,"V5":1,"V6":0,"V7":0,"V8":0,"V9":0}}
}

CHEGADAS = [
    {"id": 1, "hora": "06:00", "origem": "Sul", "viagem": "V1"},
    {"id": 2, "hora": "08:00", "origem": "Norte", "viagem": "V2"},
    {"id": 3, "hora": "10:15", "origem": "Sul", "viagem": "V3"},
    {"id": 4, "hora": "14:30", "origem": "Local", "viagem": "V4"},
    {"id": 5, "hora": "16:00", "origem": "Norte", "viagem": "V5"},
    {"id": 6, "hora": "18:45", "origem": "Sul", "viagem": "V6"},
    {"id": 7, "hora": "20:30", "origem": "Local", "viagem": "V7"},
    {"id": 8, "hora": "21:00", "origem": "Interno", "viagem": "V8"},
    {"id": 9, "hora": "23:15", "origem": "Norte", "viagem": "V9"}
]

# PERSISTÊNCIA E MONITORIZAÇÃO DE INTERAÇÃO
if "state" not in st.session_state:
    st.session_state.state = {c["id"]: {"ns": 0, "nm": 0, "nl": 0, "nxl": 0, "touched": False} for c in CHEGADAS}
if "activoId" not in st.session_state:
    st.session_state.activoId = 1
if "diaSeleccionado" not in st.session_state:
    st.session_state.diaSeleccionado = 0

# ==========================================
# FUNÇÃO DO BOTÃO LIMPAR TUDO (ZERA OS INPUTS VISUAIS TAMBÉM)
# ==========================================
def limpar_tudo():
    st.session_state.state = {c["id"]: {"ns": 0, "nm": 0, "nl": 0, "nxl": 0, "touched": False} for c in CHEGADAS}
    # Forçar a limpeza das chaves de input do componente Streamlit
    for c in CHEGADAS:
        for sufixo in ["s", "m", "l", "xl"]:
            chave = f"n_{sufixo}_val_{c['id']}"
            if chave in st.session_state:
                st.session_state[chave] = 0
    st.session_state.activoId = 1

# ==========================================
# FUNÇÕES DE TRATAMENTO TEMPORAL E CONVERSÃO
# ==========================================
def toMin(h):
    a, b = map(int, h.split(':'))
    return a * 60 + b

def toHora(m):
    h = int(math.floor(m / 60) % 24)
    mm = int(m % 60)
    return f"{h:02d}:{mm:02d}"

def getJanela(idx):
    ini = toMin(CHEGADAS[idx]["hora"])
    fim = toMin(CHEGADAS[idx+1]["hora"]) if idx < len(CHEGADAS)-1 else 24 * 60
    return {"horas": (fim - ini) / 60, "fimHora": toHora(fim), "iniHora": CHEGADAS[idx]["hora"]}

def fmt(h):
    return f"{h:.1f}h"

def fmtMin(h):
    return f"{round(h * 60)}min"

def getMixDia():
    d = DIA_SEMANA[st.session_state.diaSeleccionado]
    return {"S": d["mixS"]/100, "M": d["mixM"]/100, "L": d["mixL"]/100}

def getContentoresViagem(activoId):
    d = DIA_SEMANA[st.session_state.diaSeleccionado]
    idx = next(i for i, c in enumerate(CHEGADAS) if c["id"] == activoId)
    return d["porViagem"].get(CHEGADAS[idx]["viagem"], 0)

# ==========================================
# MOTORES DE CÁCULO DA SALA DE SUJOS
# ==========================================
def calcInd(nc):
    if nc == 0: return None
    mix = getMixDia()
    nM = nc * MANGAS_CONTENTOR
    ns = round(nM * mix["S"])
    nm = round(nM * mix["M"])
    nl = nM - ns - nm
    tS = ns / MANGAS_POR_TAB["S"]
    tM = nm / MANGAS_POR_TAB["M"]
    tL = nl / MANGAS_POR_TAB["L"]
    nTab = math.ceil(tS + tM + tL)
    nRacks = math.ceil(nTab / TAB_RACK)
    
    hBind = nc / (TAXA_B_IND * OPS_B_IND)
    taxa_c = TAXA_C_IND * OPS_C_IND
    tabPerCont = nTab / nc
    contsRack = max(1, math.ceil(15 / tabPerCont))
    t1 = 1 / (TAXA_B_IND * OPS_B_IND)
    hCind = nRacks / taxa_c
    hDind = nRacks / TAXA_D_IND + nRacks * T_D_H
    return {"nM": nM, "ns": ns, "nm": nm, "nl": nl, "nTab": nTab, "nRacks": nRacks, "hBind": hBind, "taxa_c": taxa_c, "tInicioC": contsRack * t1, "hCind": hCind, "hDind": hDind}

def calcCx(cx, horas):
    total = cx["s"] + cx["m"] + cx["l"] + cx["xl"]
    if total == 0: return None
    nTab = cx["s"] + cx["m"] + cx["l"] * 2 + cx["xl"] * 3
    nRacks = math.ceil(nTab / TAB_RACK)
    hAcx = total / (TAXA_A_CX * OPS_A_PICK)
    contrib = {"s": cx["s"]/TAXA_B_CX["S"], "m": cx["m"]/TAXA_B_CX["M"], "l": cx["l"]/TAXA_B_CX["L"], "xl": cx["xl"]/TAXA_B_CX["XL"]}
    hBbase = sum(contrib.values()) + T_B_H
    taxaPond = total / hBbase
    opsB_raw = hBbase / horas
    opsC_raw = nRacks / (TAXA_C_CX * horas)
    opsB = min(math.ceil(opsB_raw), MAX_B_CX)
    opsC = min(math.ceil(opsC_raw), MAX_C_CX)
    capBexc = math.ceil(opsB_raw) > MAX_B_CX
    capCexc = math.ceil(opsC_raw) > MAX_C_CX
    tempoBcx = hBbase / opsB
    tempoCcx = nRacks / (TAXA_C_CX * opsC)
    tInicioCcx = tempoBcx * (min(nTab, 15) / nTab)
    t1aRack = tInicioCcx + 1 / (TAXA_C_CX * opsC)
    tempoDcx = nRacks / TAXA_D_CX_PICK + nRacks / TAXA_D_CX_CARGA + nRacks * T_D_H
    return {"total": total, "nTab": nTab, "nRacks": nRacks, "hAcx": hAcx, "hBbase": hBbase, "opsB": opsB, "opsC": opsC, "opsB_raw": opsB_raw, "opsC_raw": opsC_raw, "taxaPond": taxaPond, "contrib": contrib, "capBexc": capBexc, "capCexc": capCexc, "tempoBcx": tempoBcx, "tempoCcx": tempoCcx, "tempoDcx": tempoDcx, "tInicioCcx": tInicioCcx, "t1aRack": t1aRack, "taxa_c_eff": TAXA_C_CX * opsC}

# ==========================================
# ALGORITMO INTEGRADO DE PRIORIDADES (SCHEDULER)
# ==========================================
def scheduler(rCx, rInd, tA_cx_fim):
    ev = []
    if rCx:
        for i in range(rCx["nRacks"]):
            td = tA_cx_fim + rCx["t1aRack"] + i / rCx["taxa_c_eff"] + (1 / TAXA_D_CX_PICK + T_D_H)
            ev.append({"tipo": "cx", "rack": i + 1, "t_disponivel": td, "prioridade": 0})
    if rInd:
        for i in range(rInd["nRacks"]):
            td = rInd["tInicioC"] + (i + 1) / rInd["taxa_c"] + (1 / TAXA_D_IND + T_D_H)
            ev.append({"tipo": "ind", "rack": i + 1, "t_disponivel": td, "prioridade": 1})
            
    ev.sort(key=lambda x: (x["t_disponivel"], x["prioridade"]))
    ml = [0.0] * 5
    sch = []
    for e in ev:
        bm, bt = 0, float('inf')
        for m in range(5):
            t = max(e["t_disponivel"], ml[m])
            if t < bt:
                bt, bm = t, m
        esp = max(0.0, ml[bm] - e["t_disponivel"])
        ml[bm] = bt + MAQ[bm]["ciclo_h"]
        sch.append({
            **e, "t_entrada": bt, "t_saida": bt + MAQ[bm]["ciclo_h"], "espera": esp,
            "ciclo": MAQ[bm]["ciclo_h"], "mi": bm, "maq": MAQ[bm]["id"], "cor": MAQ[bm]["cor"]
        })
    return sch

# ==========================================
# INTERFACE DO UTILIZADOR
# ==========================================
st.markdown("## <span class='title-mark'>GL</span> GLSMED Center · Sala de Sujos · Dashboard Integrado", unsafe_allow_html=True)

# BOTÃO DE LIMPEZA DE TURNO GLOBAL
if st.button("🧹 LIMPAR TODOS OS REGISTOS E REINICIAR", type="secondary", use_container_width=True):
    limpar_tudo()
    st.rerun()

# Bloco Selector de Dia da Semana
st.markdown("### Seleccione o Dia da Semana")
cols_dias = st.columns(7)
d_nomes_curtos = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
for d_idx in range(7):
    with cols_dias[d_idx]:
        txt_btn = f"**{d_nomes_curtos[d_idx]}**\n{DIA_SEMANA[d_idx]['totalContentores']}ct"
        if st.session_state.diaSeleccionado == d_idx:
            st.button(txt_btn, key=f"d_btn_{d_idx}", type="primary", use_container_width=True)
        else:
            if st.button(txt_btn, key=f"d_btn_{d_idx}", use_container_width=True):
                st.session_state.diaSeleccionado = d_idx
                st.rerun()

# 01 — Chegadas de Material
st.markdown("### 01 — Chegadas de material")
cols_tl = st.columns(len(CHEGADAS))
for idx, c in enumerate(CHEGADAS):
    with cols_tl[idx]:
        has_data = st.session_state.state[c["id"]]["touched"]
        marker = "✅" if has_data else "🚛"
        txt_c = f"{marker} **{c['viagem']}**\n{c['hora']}"
        if st.session_state.activoId == c["id"]:
            st.button(txt_c, key=f"tl_btn_{c['id']}", type="primary", use_container_width=True)
        else:
            if st.button(txt_c, key=f"tl_btn_{c['id']}", use_container_width=True):
                st.session_state.activoId = c["id"]
                st.rerun()

# Carregamento de variáveis ativas da Viagem
actId = st.session_state.activoId
idx_act = next(i for i, c in enumerate(CHEGADAS) if c["id"] == actId)
c_atual = CHEGADAS[idx_act]
janela_dados = getJanela(idx_act)
horas_janela = janela_dados["horas"]

st.markdown(f"**Viagem Ativa:** {c_atual['viagem']} | **Janela:** {horas_janela:.1f} horas ({janela_dados['iniHora']} → {janela_dados['fimHora']})")

# 3. Painel de Configuração de Volumetria
st.markdown("---")
col_panel_left, col_panel_right = st.columns(2)

with col_panel_left:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown(f"#### 📦 Caixas Cirúrgicas Solicitadas")
    s_state = st.session_state.state[actId]
    
    # Adicionado sufixo dinâmico por viagem nas chaves para permitir a limpeza via script
    in_s = st.number_input("Cx S (1 tab · 45,8/h)", min_value=0, value=s_state["ns"], key=f"n_s_val_{actId}")
    in_m = st.number_input("Cx M (1 tab · 32,1/h)", min_value=0, value=s_state["nm"], key=f"n_m_val_{actId}")
    in_l = st.number_input("Cx L (2 tab · 12,6/h)", min_value=0, value=s_state["nl"], key=f"n_l_val_{actId}")
    in_xl = st.number_input("Cx XL (3 tab · 5,2/h)", min_value=0, value=s_state["nxl"], key=f"n_xl_val_{actId}")
    
    is_touched = (in_s > 0 or in_m > 0 or in_l > 0 or in_xl > 0 or s_state["touched"])
    st.session_state.state[actId] = {"ns": in_s, "nm": in_m, "nl": in_l, "nxl": in_xl, "touched": is_touched}
    
    cx_dict = {"s": in_s, "m": in_m, "l": in_l, "xl": in_xl}
    tot_cx = sum(cx_dict.values())
    rCx = calcCx(cx_dict, horas_janela)
    
    st.markdown(f"**Total Caixas:** {tot_cx} | **Tabuleiros:** {rCx['nTab'] if rCx else 0} | **Racks:** {rCx['nRacks'] if rCx else 0}")
    st.markdown("</div>", unsafe_allow_html=True)

with col_panel_right:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown(f"#### 🧪 Material Individual: **{DIA_SEMANA[st.session_state.diaSeleccionado]['nome']}**")
    nc_viagem = getContentoresViagem(actId)
    st.markdown(f"**Contentores esperados nesta chegada:** `{nc_viagem} contentores`")
    
    if nc_viagem > 0 and not st.session_state.state[actId]["touched"]:
         st.session_state.state[actId]["touched"] = True
         
    rInd = calcInd(nc_viagem)
    
    if rInd:
        st.markdown(f"* Mix Médio Volumétrico em Trânsito: **{rInd['nM']} mangas**")
        st.markdown(f"  * Manga S (19/tab): **{rInd['ns']} mg**")
        st.markdown(f"  * Manga M (11/tab): **{rInd['nm']} mg**")
        st.markdown(f"  * Manga L (4/tab): **{rInd['nl']} mg**")
        st.markdown(f"**Conversão Logística:** `{rInd['nTab']} tabuleiros` estruturados in `{rInd['nRacks']} racks`")
    else:
        st.caption("Nenhum material individual previsto para esta rota.")
    st.markdown("</div>", unsafe_allow_html=True)

# Cálculo do motor se a viagem estiver ativa
if st.session_state.state[actId]["touched"]:
    tA_cx_fim = rCx["hAcx"] if rCx else 0
    sch = scheduler(rCx, rInd, tA_cx_fim)
    tConc = max([x["t_saida"] for x in sch]) if sch else 0
    fila_espera = [x for x in sch if x["espera"] > 0.001]
else:
    sch, tConc, fila_espera = [], 0, []

# ALERTAS INTEGRADOS
alertas = []
if rCx and rCx["capBexc"]: alertas.append(f"⚠️ **Posto B (cx):** Limite atingido — reforço necessário (excede {MAX_B_CX} op.).")
if rCx and rCx["capCexc"]: alertas.append(f"⚠️ **Posto C (cx):** Limite de {MAX_C_CX} op. atingido.")
if tConc > horas_janela and st.session_state.state[actId]["touched"]: alertas.append(f"🚨 **Atraso de Ciclo:** Ciclos de lavagem terminam às {tConc:.2f}h, ultrapassando a janela contratual.")
if fila_espera: alertas.append(f"ℹ️ **Retenção de Linha:** {len(fila_espera)} rack(s) em fila de espera.")

for al in alertas:
    st.warning(al)

# 02 & 03 — Postos de Trabalho Caixas e Individual
st.markdown("---")
st.subheader("02 & 03 — Postos Físicos de Trabalho")
col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)

with col_p1:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("**Posto A · Receção**")
    st.markdown(f"Picagem: <span style='color:#0089FF;'>462,5 cx/op.h</span>", unsafe_allow_html=True)
    st.metric("Operadores", "2", delta="Fixo")
    st.caption(f"Tempo Picagem: {rCx['hAcx']:.2f}h" if rCx else "Tempo Picagem: —")
    st.markdown("<p style='font-size:11px; color:#FF9D3D; margin-top:5px;'>💡 NOTA: Quando este trabalho acaba, os operadores dividem-se: um vai ocupar a função Di e o outro vai para a função D das caixas cirúrgicas.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_p2:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("**Posto B · Abertura Cx**")
    st.markdown("S:45.8 | M:32.1 | L:12.6 | XL:5.22")
    st.metric("Operadores", f"{rCx['opsB'] if rCx else 0}", delta=f"Teórico: {rCx['opsB_raw']:.2f}" if rCx else None, delta_color="inverse")
    st.caption(f"Tempo Estimado: {rCx['tempoBcx']:.2f}h" if rCx else "Tempo Estimado: —")
    st.markdown("</div>", unsafe_allow_html=True)

with col_p3:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("**Posto C · Pré-lavagem**")
    st.markdown("Taxa: <span style='color:#00C6B8;'>3,369 racks/op.h</span>", unsafe_allow_html=True)
    st.metric("Operadores", f"{rCx['opsC'] if rCx else 0}", delta=f"Teórico: {rCx['opsC_raw']:.2f}" if rCx else None, delta_color="inverse")
    st.caption(f"Tempo Estimado: {rCx['tempoCcx']:.2f}h" if rCx else "Tempo Estimado: —")
    st.markdown("</div>", unsafe_allow_html=True)

with col_p4:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("**Posto D · Picagem+Carga**")
    st.markdown("Picagem: 21.97/h | Carga: 27.55/h")
    st.metric("Operadores", "1", delta="Vem do A")
    st.caption(f"Tempo Estimado: {rCx['tempoDcx']:.2f}h" if rCx else "Tempo Estimado: —")
    st.markdown("</div>", unsafe_allow_html=True)

with col_p5:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("**Postos Bi/Ci/Di · Individual**")
    st.markdown("Bi:20.4 | Ci:3.332 | Di:27.548")
    st.metric("Operadores Fixos", "3 + 1 + 1", delta="Linha Fixo")
    st.caption(f"Abertura Bi: {rInd['hBind']:.2f}h" if rInd else "Abertura Bi: —")
    st.markdown("</div>", unsafe_allow_html=True)

# 04 — Resumo Integrado
st.markdown("---")
st.subheader("04 — Resumo integrado")
c_r1, c_r2, c_r3, c_r4 = st.columns(4)

total_ops_janela = 2 + (rCx["opsB"] + rCx["opsC"] + 1 if rCx else 0) + (5 if rInd else 0) if st.session_state.state[actId]["touched"] else 0
c_r1.metric("Total Operadores na Janela", f"{total_ops_janela} op.")
c_r2.metric("Janela Contratual", f"{horas_janela:.1f}h")
c_r3.metric("Conclusão Total (c/ Lavagem)", f"{tConc:.2f}h" if tConc > 0 else "—")

tempo_humano = max(rCx["tempoBcx"] if rCx else 0, rInd["hDind"] if rInd else 0, 0) if st.session_state.state[actId]["touched"] else 0
folga_h = horas_janela - tempo_humano if st.session_state.state[actId]["touched"] else 0
c_r4.metric("Folga / Atraso Laboral", f"{folga_h:.2f}h" if st.session_state.state[actId]["touched"] else "—", delta="Margem" if folga_h >= 0 and st.session_state.state[actId]["touched"] else None)

# 05 — Máquinas de Lavagem
st.markdown("---")
st.subheader("05 — Máquinas de lavagem")
mcx, mind = [0]*5, [0]*5
for x in sch:
    if x["tipo"] == "cx": mcx[x["mi"]] += 1
    else: mind[x["mi"]] += 1

cols_m = st.columns(5)
for m_idx, m in enumerate(MAQ):
    with cols_m[m_idx]:
        st.markdown(f"##### Machine **{m['id']}** ({m['ciclo_h']}h)")
        st.metric("Carga Racks", f"{mcx[m_idx] + mind[m_idx]}" if st.session_state.state[actId]["touched"] else "0", delta=f"Cx: {mcx[m_idx]} | Ind: {mind[m_idx]}" if st.session_state.state[actId]["touched"] else None)

# 06 — Fila de Espera Detalhada
st.markdown("---")
st.subheader("06 — Fila de espera")
if fila_espera and st.session_state.state[actId]["touched"]:
    df_fila = pd.DataFrame(sch)[["rack", "tipo", "t_disponivel", "maq", "ciclo", "t_entrada", "espera", "t_saida"]]
    df_fila.columns = ["Rack", "Tipo", "Pronta", "Máquina", "Ciclo (h)", "Entrada", "Espera", "Saída"]
    st.dataframe(df_fila.style.format({
        "Pronta": "{:.3f}h", "Entrada": "{:.3f}h", "Espera": "{:.3f}h", "Saída": "{:.3f}h"
    }), use_container_width=True)
else:
    st.success("Sem fila de espera activa nesta janela.")

# 07 — Gantt das Máquinas
st.markdown("---")
st.subheader("07 — Gantt das máquinas")
if sch and st.session_state.state[actId]["touched"]:
    df_gantt = pd.DataFrame(sch)
    start_time = datetime(2026, 6, 14, int(c_atual["hora"].split(':')[0]), int(c_atual["hora"].split(':')[1]))
    df_gantt["Início"] = df_gantt["t_entrada"].apply(lambda x: start_time + pd.Timedelta(hours=x))
    df_gantt["Fim"] = df_gantt["t_saida"].apply(lambda x: start_time + pd.Timedelta(hours=x))
    df_gantt["Rack ID"] = df_gantt.apply(lambda r: f"R{r['rack']} ({'Caixas' if r['tipo']=='cx' else 'Individual'})", axis=1)
    
    fig = px.timeline(
        df_gantt, x_start="Início", x_end="Fim", y="maq", color="tipo",
        text="Rack ID", color_discrete_map={"cx": COR_CX, "ind": COR_IND},
        labels={"maq": "Máquinas", "tipo": "Fluxo"}
    )
    fig.update_yaxes(categoryorder="array", categoryarray=["M5", "M4", "M3", "M2", "M1"])
    fig.update_layout(template="plotly_dark", height=320, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Aguardando ativação/registo desta chegada para projetar o cronograma de Gantt.")

# ==========================================
# 08 — HISTÓRICO CORRIGIDO (DEMANDA REAL)
# ==========================================
st.markdown("---")
st.subheader("08 — Histórico")
hist_matrix = []

for idx, c in enumerate(CHEGADAS):
    state_v = st.session_state.state[c["id"]]
    j_v = getJanela(idx)
    tot_cx_v = state_v["ns"] + state_v["nm"] + state_v["nl"] + state_v["nxl"]
    nc_v = getContentoresViagem(c["id"])
    
    if state_v["touched"]:
        rCx_v = calcCx({"s": state_v["ns"], "m": state_v["nm"], "l": state_v["nl"], "xl": state_v["nxl"]}, j_v["horas"])
        rInd_v = calcInd(nc_v)
        sch_v = scheduler(rCx_v, rInd_v, rCx_v["hAcx"] if rCx_v else 0)
        tConc_v = max([x["t_saida"] for x in sch_v]) if sch_v else 0
        
        opsB_v = rCx_v["opsB"] if rCx_v else 0
        opsC_v = rCx_v["opsC"] if rCx_v else 0
        racks_cx_v = rCx_v["nRacks"] if rCx_v else 0
        racks_ind_v = rInd_v["nRacks"] if rInd_v else 0
        tot_ops_v = 2 + (rCx_v["opsB"] + rCx_v["opsC"] + 1 if rCx_v else 0) + (5 if rInd_v else 0)
        
        status_v = "OK" if (tConc_v <= j_v["horas"] and not (rCx_v and (rCx_v["capBexc"] or rCx_v["capCexc"]))) else "Atraso/Atenção"
        conc_v_str = f"{tConc_v:.2f}h"
    else:
        status_v = "Por planear"
        opsB_v = opsC_v = racks_cx_v = racks_ind_v = tot_ops_v = 0
        conc_v_str = "—"
        tot_cx_v = "—"
        nc_v = "—"
        
    hist_matrix.append({
        "Viagem": c["viagem"], "Hora": c["hora"], "Janela": f"{j_v['horas']:.1f}h",
        "Cx S": state_v["ns"] if (state_v["ns"] > 0 and state_v["touched"]) else "—",
        "Cx M": state_v["nm"] if (state_v["nm"] > 0 and state_v["touched"]) else "—",
        "Cx L": state_v["nl"] if (state_v["nl"] > 0 and state_v["touched"]) else "—",
        "Cx XL": state_v["nxl"] if (state_v["nxl"] > 0 and state_v["touched"]) else "—",
        "Total Cx": tot_cx_v, 
        "Racks Cx": racks_cx_v if state_v["touched"] else 0, 
        "Cont. Ind": nc_v, 
        "Racks Ind": racks_ind_v if state_v["touched"] else 0,
        "Op B": opsB_v, "Op C": opsC_v, "Total Op": tot_ops_v, "Conclusão": conc_v_str, "Estado": status_v
    })

st.dataframe(pd.DataFrame(hist_matrix), use_container_width=True)