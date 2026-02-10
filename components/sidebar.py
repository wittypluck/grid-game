"""
Composant sidebar — sliders de sélection des moyens de production.
"""

from dash import html, dcc
from data import MOYENS_PRODUCTION, DEMANDE_HORAIRE, ORDRE_MERIT
from translations import t, nom_source


def creer_slider_source(source_id: str, lang: str = "fr", valeur: int = 0) -> html.Div:
    """Crée un bloc slider pour une source d'énergie donnée."""
    info = MOYENS_PRODUCTION[source_id]
    nom = nom_source(source_id, lang)
    return html.Div(className="source-block", children=[
        html.Div(f"{info['emoji']} {nom}", className="source-header"),
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
            value=valeur,
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


def creer_sidebar(lang: str = "fr", valeurs: dict | None = None) -> html.Div:
    """Construit la sidebar complète avec tous les sliders et le résumé."""
    valeurs = valeurs or {}
    sliders = [
        creer_slider_source(source_id, lang, valeurs.get(source_id, 0))
        for source_id in ORDRE_MERIT
    ]

    return html.Div(className="sidebar", id="sidebar-container", children=[
        html.H2(t("sidebar_titre", lang)),
        html.P(t("sidebar_instruction", lang)),
        html.Hr(),
        *sliders,
        html.Hr(),
        html.Div(id="sidebar-investissement", className="sidebar-summary"),
        html.Div(id="sidebar-puissance", className="sidebar-summary"),
        html.Div(
            t("sidebar_demande_max", lang).format(demande=f"{int(DEMANDE_HORAIRE.max()):,}"),
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
