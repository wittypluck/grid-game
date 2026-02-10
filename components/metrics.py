"""
Composant des cartes métriques et messages d'état.
"""

from dash import html

from data import MOYENS_PRODUCTION, ORDRE_MERIT
from translations import t, nom_source


def _carte_metrique(valeur: str, label: str, couleur: str) -> html.Div:
    """Génère une carte métrique individuelle."""
    return html.Div(className="metric-card", children=[
        html.Div(valeur, className="metric-value", style={"color": couleur}),
        html.Div(label, className="metric-label"),
    ])


def creer_metriques(indicateurs: dict, lang: str = "fr") -> html.Div:
    """Crée la barre de 6 métriques clés."""
    score = indicateurs["score_total"]
    if score >= 70:
        score_color, score_emoji = "#44ff44", "🏆"
    elif score >= 40:
        score_color, score_emoji = "#ffaa00", "📊"
    else:
        score_color, score_emoji = "#ff4444", "⚠️"

    couverture = indicateurs["taux_couverture"]
    couv_color = "#44ff44" if couverture >= 100 else "#ffaa00" if couverture >= 90 else "#ff4444"

    deficit_color = "#44ff44" if indicateurs["heures_deficit"] == 0 else "#ff4444"

    surplus_pct = indicateurs.get("ratio_surplus", 0)
    surplus_color = "#44ff44" if surplus_pct < 5 else "#ffaa00" if surplus_pct < 20 else "#ff4444"
    malus = indicateurs.get("malus_surplus", 0)

    return html.Div(className="metrics-row", children=[
        _carte_metrique(f"{score_emoji} {score}/100", t("metric_score", lang), score_color),
        _carte_metrique(f"{couverture}%", t("metric_couverture", lang), couv_color),
        _carte_metrique(f"{indicateurs['cout_total']:,.0f} M€", t("metric_cout", lang), "#00AAFF"),
        _carte_metrique(f"{indicateurs['co2_total']:,.0f} t", t("metric_co2", lang), "#A0D911"),
        _carte_metrique(f"{indicateurs['heures_deficit']}h / 24h", t("metric_blackout", lang), deficit_color),
        _carte_metrique(
            f"{surplus_pct}%",
            t("metric_surplus", lang).format(malus=f"{malus:.0f}"),
            surplus_color,
        ),
    ])


def creer_message_etat(indicateurs: dict, lang: str = "fr") -> html.Div:
    """Crée le message de feedback (succès, avertissement ou alerte)."""
    couverture = indicateurs["taux_couverture"]
    heures_deficit = indicateurs["heures_deficit"]

    if couverture >= 100 and heures_deficit == 0:
        return html.Div(className="success-box", children=[
            html.Span("✅ "),
            html.B(t("msg_bravo", lang)),
            html.Span(t("msg_bravo_detail", lang)),
        ])
    elif couverture >= 90:
        return html.Div(className="warning-box", children=[
            html.Span("⚠️ "),
            html.B(t("msg_presque", lang)),
            html.Span(t("msg_presque_detail", lang).format(couverture=couverture)),
            html.B(t("msg_presque_blackout", lang).format(heures=heures_deficit)),
            html.Span(t("msg_presque_fin", lang)),
        ])
    else:
        return html.Div(className="warning-box", children=[
            html.Span("🚨 "),
            html.B(t("msg_alerte", lang)),
            html.Span(t("msg_alerte_detail", lang).format(couverture=couverture)),
            html.B(t("msg_presque_blackout", lang).format(heures=heures_deficit)),
            html.Span(t("msg_alerte_fin", lang)),
        ])


def creer_tableau_details(indicateurs: dict, lang: str = "fr") -> list:
    """Retourne les colonnes et les données pour le DataTable des détails par source."""
    colonnes = [
        {"name": "", "id": "emoji"},
        {"name": t("col_source", lang), "id": "source"},
        {"name": t("col_unites", lang), "id": "unites"},
        {"name": t("col_production", lang), "id": "production"},
        {"name": t("col_cout_constr", lang), "id": "cout_constr"},
        {"name": t("col_cout_prod", lang), "id": "cout_prod"},
        {"name": t("col_co2_tonnes", lang), "id": "co2"},
    ]

    donnees = []
    for source_id, detail in indicateurs["details_par_source"].items():
        info = MOYENS_PRODUCTION[source_id]
        donnees.append({
            "emoji": info["emoji"],
            "source": nom_source(source_id, lang),
            "unites": detail["nb_unites"],
            "production": f"{detail['production_mwh']:,.0f}",
            "cout_constr": f"{detail['cout_construction']:,.0f}",
            "cout_prod": f"{detail['cout_production']:,.1f}",
            "co2": f"{detail['co2_tonnes']:,.0f}",
        })

    return colonnes, donnees


def creer_tableau_caracteristiques(lang: str = "fr") -> tuple:
    """Retourne colonnes et données du tableau des caractéristiques (écran d'accueil)."""
    colonnes = [
        {"name": "", "id": "emoji"},
        {"name": t("col_source", lang), "id": "source"},
        {"name": t("col_puissance", lang), "id": "puissance"},
        {"name": t("col_cout_construction", lang), "id": "cout_constr"},
        {"name": t("col_cout_production", lang), "id": "cout_prod"},
        {"name": t("col_disponibilite", lang), "id": "disponibilite"},
        {"name": t("col_co2_intensite", lang), "id": "co2"},
        {"name": t("col_pilotable", lang), "id": "pilotable"},
    ]

    donnees = []
    for source_id in ORDRE_MERIT:
        info = MOYENS_PRODUCTION[source_id]
        donnees.append({
            "emoji": info["emoji"],
            "source": nom_source(source_id, lang),
            "puissance": info["puissance"],
            "cout_constr": info["cout_construction"],
            "cout_prod": info["cout_production"],
            "disponibilite": f"{info['disponibilite'] * 100:.0f}%",
            "co2": info["co2"],
            "pilotable": "✅" if info["pilotable"] else "❌",
        })

    return colonnes, donnees
