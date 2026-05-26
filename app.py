import streamlit as st
import pandas as pd
import numpy as np
import os, os.path
import seaborn as sns
import tqdm
import matplotlib.pyplot as plt
import plotly.express as px
from utils import read_files_to_df_dict, concat_df_dict

st.set_page_config(page_title="Spotify Data App", layout="wide")

DATA_PATH = "spotify_data/"

st.title("🤬 Analiza wulgaryzmów w danych Spotify")
st.markdown("---")


@st.cache_data
def load_and_concat_data(path):
    df_dict = read_files_to_df_dict(path)
    return concat_df_dict(df_dict)


# Ładowanie danych
spotify_df = load_and_concat_data(DATA_PATH)

# ==========================================
# SEKCJA 1: ROZKŁAD W GATUNKACH
# ==========================================
st.subheader("Częstotliwość występowania wulgaryzmów")
st.info(
    "📊 **Rozkład w gatunkach**\n\nKtóre gatunki muzyczne najczęściej zawierają wulgaryzmy?"
)

odsetek_explicit = spotify_df.groupby("track_genre")["explicit"].mean() * 100
explicit_df = odsetek_explicit.reset_index()

explicit_df.columns = ["Gatunek", "Procent Wulgaryzmów"]
explicit_df = explicit_df.sort_values(by="Procent Wulgaryzmów", ascending=False)

top_n = st.slider(
    "Wybierz liczbę gatunków do wyświetlenia:", min_value=3, max_value=114, value=20
)
explicit_df_top = explicit_df.head(top_n)

fig = px.bar(
    explicit_df_top,
    x="Gatunek",
    y="Procent Wulgaryzmów",
    title=f"Top {top_n} gatunków muzycznych z największym odsetkiem wulgaryzmów",
    text="Procent Wulgaryzmów",
    color="Procent Wulgaryzmów",
    color_continuous_scale="Reds",
)
fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
st.plotly_chart(fig, use_container_width=True)


# ==========================================
# SEKCJA 2: POPULARNOŚĆ
# ==========================================
st.markdown("---")
st.subheader("Wpływ wulgarności na popularność")
st.success(
    "📈 **Popularność**\n\nCzy utwory zawierające wulgaryzmy są chętniej słuchane?"
)

wybrane_gatunki = st.multiselect(
    "Wybierz gatunki do porównania:",
    options=spotify_df["track_genre"].unique(),
    default=["hip-hop", "pop", "classical", "metal"],
)

df_violin = spotify_df[spotify_df["track_genre"].isin(wybrane_gatunki)].copy()

df_violin["explicit_label"] = df_violin["explicit"].map(
    {True: "Wulgarne (True)", False: "Czyste (False)"}
)

if not df_violin.empty:
    fig_violin = px.violin(
        df_violin,
        x="track_genre",
        y="popularity",
        color="explicit_label",
        violinmode="group",
        title="Rozkład popularności utworów wulgarnych vs czystych",
        category_orders={"explicit_label": ["Czyste (False)", "Wulgarne (True)"]},
        color_discrete_map={
            "Czyste (False)": "#1DB954",
            "Wulgarne (True)": "#E91429",
        },
    )

    fig_violin.update_traces(meanline_visible=True)
    fig_violin.update_layout(xaxis_title="Gatunek", yaxis_title="Popularność (0-100)")

    st.plotly_chart(fig_violin, use_container_width=True)
else:
    st.warning("Wybierz co najmniej jeden gatunek, aby zobaczyć wykres.")


# ==========================================
# SEKCJA 3: EMOCJE
# ==========================================
st.markdown("---")
st.subheader("Wulgarność a Emocje: Gdzie leżą przekleństwa?")
st.warning(
    "🎭 **Emocje i nastrój**\n\nCzy wulgaryzmy to domena utworów smutnych, czy agresywnych?"
)
st.markdown("""
Ten wykres opiera się na psychologicznym **[Kołowym Modelu Afektu (Koło Russella)](https://en.wikipedia.org/wiki/Emotion_classification#Circumplex_model)**. Zestawiając pozytywny wydźwięk utworu ze Spotify (**Valence**) z jego intensywnością (**Energy**), możemy podzielić mapę na cztery strefy klimatu:

* ↖️ **Lewy górny róg (Agresja / Napięcie):** Niskie Valence, wysoka Energy. Utwory intensywne, głośne i dynamiczne, ale o negatywnym zabarwieniu (np. death metal, agresywny rap).
* ↗️ **Prawy górny róg (Radość / Ekscytacja):** Wysokie Valence, wysoka Energy. Utwory wesołe, euforyczne, szybkie i optymistyczne.
* ↙️ **Lewy dolny róg (Smutek / Melancholia):** Niskie Valence, niska Energy. Utwory powolne, ciche, brzmiące smutno i przygnębiająco.
* ↘️ **Prawy dolny róg (Spokój / Relaks):** Wysokie Valence, niska Energy. Utwory pogodne i pozytywne, ale wyciszające (np. muzyka akustyczna, chillout).

*Analizujemy tylko gatunki wybrane w panelu powyżej.*
""")

if not df_violin.empty:
    fig_emotions = px.density_heatmap(
        df_violin,
        x="valence",
        y="energy",
        facet_col="explicit_label",
        nbinsx=20,
        nbinsy=20,
        color_continuous_scale="Viridis",
        title="Koncentracja utworów na mapie emocji (Valence vs Energy)",
        category_orders={"explicit_label": ["Czyste (False)", "Wulgarne (True)"]},
    )

    fig_emotions.update_layout(
        xaxis_title="Valence (Smutek -> Radość)",
        yaxis_title="Energy (Spokój -> Agresja)",
    )

    fig_emotions.for_each_xaxis(
        lambda axis: axis.update(title="Valence<br>(Smutek -> Radość)")
    )
    fig_emotions.for_each_yaxis(
        lambda axis: axis.update(title="Energy<br>(Spokój -> Agresja)")
    )

    st.plotly_chart(fig_emotions, use_container_width=True)
