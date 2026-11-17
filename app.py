
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="FOREX TRADER",
    page_icon="📈",
    layout="wide"
)

st.title("📈 FOREX TRADER")
st.subheader("Votre tableau de bord d'analyse Forex")

paires = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X",
    "USD/CHF": "CHF=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CAD": "CAD=X"
}

@st.cache_data(ttl=900)
def obtenir_donnees(symbole):
    data = yf.download(
        symbole,
        period="3mo",
        interval="1d",
        progress=False
    )
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data.dropna()

choix = st.sidebar.selectbox(
    "Choisir une paire Forex",
    list(paires.keys())
)

st.sidebar.markdown("---")
st.sidebar.write("FOREX TRADER")
st.sidebar.caption("Analyse technique indicative")

with st.spinner("Chargement des données..."):
    data = obtenir_donnees(paires[choix])

if data.empty or len(data) < 50:
    st.error("Données indisponibles. Réessayez plus tard.")
    st.stop()

data["SMA20"] = data["Close"].rolling(20).mean()
data["SMA50"] = data["Close"].rolling(50).mean()

prix = float(data["Close"].iloc[-1])
sma20 = float(data["SMA20"].iloc[-1])
sma50 = float(data["SMA50"].iloc[-1])

support = float(data["Low"].tail(20).min())
resistance = float(data["High"].tail(20).max())

if sma20 > sma50 and prix > sma20:
    signal = "BUY"
elif sma20 < sma50 and prix < sma20:
    signal = "SELL"
else:
    signal = "WAIT"

st.header(f"Analyse de {choix}")

c1, c2, c3 = st.columns(3)
c1.metric("Dernier cours", f"{prix:.5f}")
c2.metric("Signal", signal)
c3.metric("Tendance", "Haussière" if sma20 > sma50 else "Baissière" if sma20 < sma50 else "Neutre")

st.subheader("Graphique des prix")

fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=data.index,
    open=data["Open"],
    high=data["High"],
    low=data["Low"],
    close=data["Close"],
    name=choix
))

fig.add_trace(go.Scatter(
    x=data.index,
    y=data["SMA20"],
    name="Moyenne 20 jours"
))

fig.add_trace(go.Scatter(
    x=data.index,
    y=data["SMA50"],
    name="Moyenne 50 jours"
))

fig.add_hline(y=support, line_dash="dash",
              annotation_text="Support")

fig.add_hline(y=resistance, line_dash="dash",
              annotation_text="Résistance")

fig.update_layout(
    template="plotly_dark",
    height=500,
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("📊 Niveaux techniques")

a, b = st.columns(2)
a.metric("Support indicatif", f"{support:.5f}")
b.metric("Résistance indicative", f"{resistance:.5f}")

st.subheader("💰 Calculateur de risque")

capital = st.number_input(
    "Capital en dollars ($)",
    min_value=1.0,
    value=100.0
)

risque = st.slider(
    "Risque par opération (%)",
    min_value=0.5,
    max_value=5.0,
    value=1.0
)

stop_loss = st.number_input(
    "Stop Loss (pips)",
    min_value=1.0,
    value=20.0
)

montant = capital * risque / 100
lot = montant / (stop_loss * 10)

st.metric("Montant risqué", f"{montant:.2f} $")
st.metric("Lot estimé", f"{lot:.3f}")

st.caption(
    "Calcul indicatif basé sur une valeur de pip de 10 $ "
    "par lot standard. La valeur réelle dépend de la paire "
    "et de la devise du compte."
)

st.subheader("📋 Historique de l'analyse")

if "historique" not in st.session_state:
    st.session_state.historique = []

if st.button("Enregistrer cette analyse"):
    st.session_state.historique.append({
        "Date": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
        "Paire": choix,
        "Prix": prix,
        "Signal": signal
    })

if st.session_state.historique:
    historique = pd.DataFrame(st.session_state.historique)
    st.dataframe(historique, use_container_width=True)

    st.download_button(
        "Télécharger l'historique CSV",
        historique.to_csv(index=False).encode("utf-8"),
        file_name="historique_forex.csv",
        mime="text/csv"
    )

st.divider()
st.caption(
    "FOREX TRADER | Outil d'analyse éducatif. "
    "Les signaux ne garantissent aucun résultat de trading."
)
