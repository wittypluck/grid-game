"""
Composant graphiques — tous les graphiques Plotly de l'application.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from data import MOYENS_PRODUCTION, DEMANDE_HORAIRE, LABELS_HEURES, ORDRE_MERIT


# =============================================================================
# Utilitaires
# =============================================================================

def _hex_to_rgba(hex_color: str, alpha: float = 0.8) -> str:
    """Convertit une couleur hex (#RRGGBB) en chaîne rgba()."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


_LAYOUT_COMMUN = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    hoverlabel=dict(
        bgcolor="#1a1f2e",
        bordercolor="#333",
        font=dict(color="#ffffff"),
    ),
)


# =============================================================================
# Graphiques
# =============================================================================

def graphique_demande_seule() -> go.Figure:
    """Courbe de demande seule (écran d'accueil)."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=LABELS_HEURES, y=DEMANDE_HORAIRE,
        mode="lines+markers",
        name="Demande",
        line=dict(color="#ff6b6b", width=3),
        marker=dict(size=6),
        fill="tozeroy",
        fillcolor="rgba(255, 107, 107, 0.15)",
    ))
    fig.update_layout(
        **_LAYOUT_COMMUN,
        xaxis_title="Heure",
        yaxis_title="Puissance (MW)",
        height=400,
        margin=dict(l=60, r=30, t=30, b=60),
        yaxis=dict(range=[0, DEMANDE_HORAIRE.max() * 1.15]),
    )
    return fig


def graphique_production_vs_demande(
    df_prod: pd.DataFrame,
    choix_joueur: dict,
) -> go.Figure:
    """Graphique principal : aires empilées de production + courbe de demande."""
    fig = go.Figure()

    sources_a_afficher = [s for s in ORDRE_MERIT if choix_joueur.get(s, 0) > 0]

    # Aires empilées par source
    for source_id in sources_a_afficher:
        info = MOYENS_PRODUCTION[source_id]
        fig.add_trace(go.Scatter(
            x=LABELS_HEURES,
            y=df_prod[source_id],
            name=f"{info['emoji']} {info['nom']}",
            stackgroup="production",
            fillcolor=_hex_to_rgba(info["couleur"], 0.8),
            line=dict(width=0.5, color=info["couleur"]),
            hovertemplate=(
                f"<b>{info['nom']}</b><br>"
                "Heure: %{x}<br>"
                "Production: %{y:,.0f} MW<br>"
                "<extra></extra>"
            ),
        ))

    # Courbe de demande
    fig.add_trace(go.Scatter(
        x=LABELS_HEURES,
        y=DEMANDE_HORAIRE,
        name="📊 Demande",
        mode="lines+markers",
        line=dict(color="#ff6b6b", width=3, dash="dot"),
        marker=dict(size=6, color="#ff6b6b"),
        hovertemplate=(
            "<b>Demande</b><br>"
            "Heure: %{x}<br>"
            "Demande: %{y:,.0f} MW<br>"
            "<extra></extra>"
        ),
    ))

    # Marqueurs de déficit
    deficit_mask = df_prod["deficit"] > 0
    if deficit_mask.any():
        fig.add_trace(go.Scatter(
            x=LABELS_HEURES,
            y=np.where(deficit_mask, DEMANDE_HORAIRE, None),
            name="⚠️ Déficit (blackout)",
            mode="markers",
            marker=dict(size=12, color="red", symbol="x"),
        ))

    fig.update_layout(
        **_LAYOUT_COMMUN,
        xaxis_title="Heure de la journée",
        yaxis_title="Puissance (MW)",
        height=500,
        margin=dict(l=60, r=30, t=30, b=60),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        hovermode="x unified",
        yaxis=dict(range=[0, max(DEMANDE_HORAIRE.max(), df_prod["production_totale"].max()) * 1.1]),
    )
    return fig


def graphique_mix_energetique(
    df_prod: pd.DataFrame,
    choix_joueur: dict,
) -> go.Figure:
    """Camembert (donut) du mix énergétique."""
    sources = [s for s in ORDRE_MERIT if choix_joueur.get(s, 0) > 0]
    prod_par_source = {s: df_prod[s].sum() for s in sources if df_prod[s].sum() > 0}

    if not prod_par_source:
        return go.Figure()

    fig = go.Figure(data=[go.Pie(
        labels=[f"{MOYENS_PRODUCTION[s]['emoji']} {MOYENS_PRODUCTION[s]['nom']}" for s in prod_par_source],
        values=list(prod_par_source.values()),
        marker_colors=[MOYENS_PRODUCTION[s]["couleur"] for s in prod_par_source],
        hole=0.4,
        textinfo="label+percent",
        textposition="outside",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Production: %{value:,.0f} MWh<br>"
            "Part: %{percent}<br>"
            "<extra></extra>"
        ),
    )])
    fig.update_layout(**_LAYOUT_COMMUN, height=400, margin=dict(l=20, r=20, t=20, b=20), showlegend=False)
    return fig


def graphique_decomposition_score(indicateurs: dict) -> go.Figure:
    """Barres de décomposition du score (max en fond, score réel par-dessus)."""
    couverture = indicateurs["taux_couverture"]
    couv_color = "#44ff44" if couverture >= 100 else "#ffaa00" if couverture >= 90 else "#ff4444"

    categories = ["Couverture\n(/40)", "CO₂\n(/30)", "Coût\n(/30)", "Surplus\n(malus)"]
    valeurs = [
        indicateurs["score_couverture"],
        indicateurs["score_co2"],
        indicateurs["score_cout"],
        -indicateurs.get("malus_surplus", 0),
    ]
    max_valeurs = [40, 30, 30, 0]
    couleurs = [couv_color, "#A0D911", "#00AAFF", "#ff4444"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories, y=max_valeurs, name="Maximum",
        marker_color="rgba(100,100,100,0.3)", hoverinfo="skip",
    ))
    fig.add_trace(go.Bar(
        x=categories, y=valeurs, name="Votre score",
        marker_color=couleurs,
        text=[f"{v:+.0f}" if v < 0 else f"{v:.0f}" for v in valeurs],
        textposition="auto",
        textfont=dict(size=16, color="white"),
    ))
    fig.update_layout(
        **_LAYOUT_COMMUN,
        height=400, margin=dict(l=40, r=20, t=20, b=60),
        barmode="overlay", showlegend=False,
        yaxis=dict(range=[-30, 45]),
    )
    return fig


def graphique_cout_par_source(indicateurs: dict) -> go.Figure:
    """Barres empilées construction + production par source."""
    details = indicateurs["details_par_source"]
    if not details:
        return go.Figure()

    sources = list(details.keys())
    noms = [MOYENS_PRODUCTION[s]["nom"] for s in sources]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=noms,
        y=[details[s]["cout_construction"] for s in sources],
        name="Construction", marker_color="#00AAFF",
    ))
    fig.add_trace(go.Bar(
        x=noms,
        y=[details[s]["cout_production"] for s in sources],
        name="Production", marker_color="#A0D911",
    ))
    fig.update_layout(
        **_LAYOUT_COMMUN,
        barmode="stack", height=350, margin=dict(l=40, r=20, t=20, b=60),
        yaxis_title="Coût (M€)",
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
    )
    return fig


def graphique_co2_par_source(indicateurs: dict) -> go.Figure:
    """Barres de CO₂ par source."""
    details = indicateurs["details_par_source"]
    if not details:
        return go.Figure()

    sources = list(details.keys())

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[MOYENS_PRODUCTION[s]["nom"] for s in sources],
        y=[details[s]["co2_tonnes"] for s in sources],
        marker_color=[MOYENS_PRODUCTION[s]["couleur"] for s in sources],
        text=[f"{details[s]['co2_tonnes']:,.0f}" for s in sources],
        textposition="auto",
    ))
    fig.update_layout(
        **_LAYOUT_COMMUN,
        height=350, margin=dict(l=40, r=20, t=20, b=60),
        yaxis_title="CO₂ (tonnes)", showlegend=False,
    )
    return fig
