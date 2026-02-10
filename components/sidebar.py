"""
Composant sidebar — sliders de sélection des moyens de production.
"""

from dash import html, dcc
from data import MOYENS_PRODUCTION, DEMANDE_HORAIRE, ORDRE_MERIT


def creer_slider_source(source_id: str) -> html.Div:
    """Crée un bloc slider pour une source d'énergie donnée."""
    info = MOYENS_PRODUCTION[source_id]
    return html.Div(className="source-block", children=[
        html.Div(f"{info['emoji']} {info['nom']}", className="source-header"),
        html.Div(
            f"{info['puissance']} MW | {info['cout_construction']} M€ | "
            f"{info['co2']} gCO₂/kWh",
            className="source-caption",
        ),
        dcc.Slider(
            id=f"slider-{source_id}",
            min=0,
            max=info["max_unites"],
            step=1,
            value=0,
            marks={0: "0", info["max_unites"]: str(info["max_unites"])},
            tooltip={
                "placement": "bottom",
                "always_visible": False,
                "style": {
                    "backgroundColor": "#1a1f2e",
                    "color": "#ffffff",
                    "border": "1px solid #333",
                    "borderRadius": "4px",
                    "padding": "4px 8px",
                    "fontSize": "0.9rem",
                },
            },
        ),
    ])


def creer_sidebar() -> html.Div:
    """Construit la sidebar complète avec tous les sliders et le résumé."""
    sliders = [creer_slider_source(source_id) for source_id in ORDRE_MERIT]

    return html.Div(className="sidebar", children=[
        html.H2("🏗️ Vos investissements"),
        html.P("Choisissez le nombre d'unités pour chaque moyen de production :"),
        html.Hr(),
        *sliders,
        html.Hr(),
        html.Div(id="sidebar-investissement", className="sidebar-summary"),
        html.Div(id="sidebar-puissance", className="sidebar-summary"),
        html.Div(
            f"📊 Demande max : {int(DEMANDE_HORAIRE.max()):,} MW",
            style={"color": "#aaa", "fontSize": "0.9rem", "marginTop": "8px"},
        ),
        html.Div(id="sidebar-warning"),
    ])


def lire_choix_joueur(slider_values: list) -> dict:
    """
    Convertit les valeurs des sliders en dictionnaire choix_joueur.

    Args:
        slider_values: liste de valeurs dans l'ordre de ORDRE_MERIT

    Returns:
        dict {source_id: nb_unites, ...}
    """
    return {
        source_id: (val or 0)
        for source_id, val in zip(ORDRE_MERIT, slider_values)
    }
