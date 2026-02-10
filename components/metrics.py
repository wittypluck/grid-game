"""
Composant des cartes métriques et messages d'état.
"""

from dash import html

from data import MOYENS_PRODUCTION, ORDRE_MERIT


def _carte_metrique(valeur: str, label: str, couleur: str) -> html.Div:
    """Génère une carte métrique individuelle."""
    return html.Div(className="metric-card", children=[
        html.Div(valeur, className="metric-value", style={"color": couleur}),
        html.Div(label, className="metric-label"),
    ])


def creer_metriques(indicateurs: dict) -> html.Div:
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
        _carte_metrique(f"{score_emoji} {score}/100", "SCORE GLOBAL", score_color),
        _carte_metrique(f"{couverture}%", "COUVERTURE DEMANDE", couv_color),
        _carte_metrique(f"{indicateurs['cout_total']:,.0f} M€", "COÛT TOTAL", "#00AAFF"),
        _carte_metrique(f"{indicateurs['co2_total']:,.0f} t", "CO₂ ÉMIS", "#A0D911"),
        _carte_metrique(f"{indicateurs['heures_deficit']}h / 24h", "HEURES DE BLACKOUT", deficit_color),
        _carte_metrique(f"{surplus_pct}%", f"SURPLUS (-{malus:.0f} pts)", surplus_color),
    ])


def creer_message_etat(indicateurs: dict) -> html.Div:
    """Crée le message de feedback (succès, avertissement ou alerte)."""
    couverture = indicateurs["taux_couverture"]
    heures_deficit = indicateurs["heures_deficit"]

    if couverture >= 100 and heures_deficit == 0:
        return html.Div(className="success-box", children=[
            html.Span("✅ "),
            html.B("Bravo !"),
            html.Span(
                " Votre mix couvre 100% de la demande. Aucun blackout ! "
                "Essayez maintenant d'optimiser les coûts et les émissions de CO₂."
            ),
        ])
    elif couverture >= 90:
        return html.Div(className="warning-box", children=[
            html.Span("⚠️ "),
            html.B("Presque !"),
            html.Span(f" Votre mix couvre {couverture}% de la demande, mais il reste "),
            html.B(f"{heures_deficit} heures de blackout"),
            html.Span(". Ajoutez de la capacité pour sécuriser l'approvisionnement."),
        ])
    else:
        return html.Div(className="warning-box", children=[
            html.Span("🚨 "),
            html.B("Alerte !"),
            html.Span(f" Votre mix ne couvre que {couverture}% de la demande ! Il y a "),
            html.B(f"{heures_deficit} heures de blackout"),
            html.Span(". Vous devez investir dans plus de capacité de production."),
        ])


def creer_tableau_details(indicateurs: dict) -> list:
    """Retourne les colonnes et les données pour le DataTable des détails par source."""
    colonnes = [
        {"name": "", "id": "emoji"},
        {"name": "Source", "id": "source"},
        {"name": "Unités", "id": "unites"},
        {"name": "Production (MWh)", "id": "production"},
        {"name": "Coût constr. (M€)", "id": "cout_constr"},
        {"name": "Coût prod. (M€)", "id": "cout_prod"},
        {"name": "CO₂ (tonnes)", "id": "co2"},
    ]

    donnees = []
    for source_id, detail in indicateurs["details_par_source"].items():
        info = MOYENS_PRODUCTION[source_id]
        donnees.append({
            "emoji": info["emoji"],
            "source": detail["nom"],
            "unites": detail["nb_unites"],
            "production": f"{detail['production_mwh']:,.0f}",
            "cout_constr": f"{detail['cout_construction']:,.0f}",
            "cout_prod": f"{detail['cout_production']:,.1f}",
            "co2": f"{detail['co2_tonnes']:,.0f}",
        })

    return colonnes, donnees


def creer_tableau_caracteristiques() -> tuple:
    """Retourne colonnes et données du tableau des caractéristiques (écran d'accueil)."""
    colonnes = [
        {"name": "", "id": "emoji"},
        {"name": "Source", "id": "source"},
        {"name": "Puissance (MW)", "id": "puissance"},
        {"name": "Coût construction (M€)", "id": "cout_constr"},
        {"name": "Coût production (€/MWh)", "id": "cout_prod"},
        {"name": "Disponibilité", "id": "disponibilite"},
        {"name": "CO₂ (gCO₂/kWh)", "id": "co2"},
        {"name": "Pilotable", "id": "pilotable"},
    ]

    donnees = []
    for source_id in ORDRE_MERIT:
        info = MOYENS_PRODUCTION[source_id]
        donnees.append({
            "emoji": info["emoji"],
            "source": info["nom"],
            "puissance": info["puissance"],
            "cout_constr": info["cout_construction"],
            "cout_prod": info["cout_production"],
            "disponibilite": f"{info['disponibilite'] * 100:.0f}%",
            "co2": info["co2"],
            "pilotable": "✅" if info["pilotable"] else "❌",
        })

    return colonnes, donnees
