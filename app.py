"""
⚡ Équilibre du Réseau Électrique
Application Dash principale — point d'entrée et callbacks.
"""

from dash import Dash, html, dcc, dash_table, Input, Output, callback

from data import MOYENS_PRODUCTION, DEMANDE_HORAIRE, ORDRE_MERIT
from simulation import calculer_production_horaire, calculer_indicateurs

from components.sidebar import creer_sidebar, lire_choix_joueur
from components.metrics import creer_metriques, creer_message_etat, creer_tableau_details
from components.charts import (
    graphique_production_vs_demande,
    graphique_mix_energetique,
    graphique_decomposition_score,
    graphique_cout_par_source,
    graphique_co2_par_source,
)
from components.welcome import creer_ecran_accueil, creer_section_pedagogique


# =============================================================================
# Initialisation de l'application Dash
# =============================================================================

app = Dash(
    __name__,
    title="⚡ Équilibre du Réseau Électrique",
    update_title=None,
    assets_folder="assets",
)

server = app.server  # pour déploiement WSGI (gunicorn, etc.)


# =============================================================================
# Layout
# =============================================================================

app.layout = html.Div(className="app-container", children=[
    # Sidebar
    creer_sidebar(),

    # Zone principale
    html.Div(className="main-content", children=[
        html.H1("⚡ Équilibre du Réseau Électrique", className="main-title"),
        html.P(
            "Construisez votre mix énergétique pour couvrir la demande française sur 24h. "
            "Minimisez les coûts et les émissions de CO₂ tout en garantissant la sécurité d'approvisionnement.",
            className="subtitle",
        ),

        # Contenu dynamique (accueil ou résultats)
        html.Div(id="contenu-principal"),
    ]),
])


# =============================================================================
# Callback principal — mis à jour à chaque changement de slider
# =============================================================================

@callback(
    Output("contenu-principal", "children"),
    Output("sidebar-investissement", "children"),
    Output("sidebar-puissance", "children"),
    Output("sidebar-warning", "children"),
    [Input(f"slider-{source_id}", "value") for source_id in ORDRE_MERIT],
)
def mettre_a_jour(*slider_values):
    """Callback principal : recalcule tout à chaque changement de slider."""
    choix_joueur = lire_choix_joueur(slider_values)

    # --- Résumé sidebar ---
    cout_construction = sum(
        (v or 0) * MOYENS_PRODUCTION[s]["cout_construction"]
        for s, v in choix_joueur.items()
    )
    puissance_installee = sum(
        (v or 0) * MOYENS_PRODUCTION[s]["puissance"]
        for s, v in choix_joueur.items()
    )

    sidebar_invest = f"💰 Investissement : {cout_construction:,.0f} M€"
    sidebar_puissance = f"⚡ Puissance installée : {puissance_installee:,.0f} MW"

    sidebar_warning = None
    if puissance_installee < DEMANDE_HORAIRE.max():
        sidebar_warning = html.Div(
            "⚠️ Puissance installée inférieure au pic de demande !",
            className="sidebar-warning",
        )

    # --- Contenu principal ---
    total_unites = sum(choix_joueur.values())

    if total_unites == 0:
        return creer_ecran_accueil(), sidebar_invest, sidebar_puissance, sidebar_warning

    # Simulation
    df_prod = calculer_production_horaire(choix_joueur)
    indicateurs = calculer_indicateurs(choix_joueur, df_prod)

    # Tableau détaillé
    colonnes_detail, donnees_detail = creer_tableau_details(indicateurs)

    contenu = html.Div([
        html.Hr(),

        # Métriques
        creer_metriques(indicateurs),

        # Message d'état
        creer_message_etat(indicateurs),

        # Graphique principal
        html.H3("📈 Production vs Demande — Vue 24h", className="section-title"),
        dcc.Graph(
            figure=graphique_production_vs_demande(df_prod, choix_joueur),
            config={"displayModeBar": False},
        ),

        # Graphiques secondaires côte à côte
        html.Div(className="charts-row", children=[
            html.Div([
                html.H3("🥧 Mix énergétique", className="section-title"),
                dcc.Graph(
                    figure=graphique_mix_energetique(df_prod, choix_joueur),
                    config={"displayModeBar": False},
                ),
            ]),
            html.Div([
                html.H3("🏆 Décomposition du score", className="section-title"),
                dcc.Graph(
                    figure=graphique_decomposition_score(indicateurs),
                    config={"displayModeBar": False},
                ),
            ]),
        ]),

        # Tableau détaillé
        html.H3("📊 Détails par source de production", className="section-title"),
        dash_table.DataTable(
            columns=colonnes_detail,
            data=donnees_detail,
            style_table={"overflowX": "auto"},
            style_header={
                "backgroundColor": "#252b3b",
                "color": "#ffffff",
                "fontWeight": "bold",
                "border": "1px solid #333",
            },
            style_cell={
                "backgroundColor": "#1a1f2e",
                "color": "#e0e0e0",
                "border": "1px solid #333",
                "textAlign": "center",
                "padding": "10px",
            },
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "#1e2433"},
            ],
        ),

        # Graphiques coût vs CO₂
        html.H3("💰 Coût vs CO₂ par source", className="section-title"),
        html.Div(className="charts-row", children=[
            html.Div([
                dcc.Graph(
                    figure=graphique_cout_par_source(indicateurs),
                    config={"displayModeBar": False},
                ),
            ]),
            html.Div([
                dcc.Graph(
                    figure=graphique_co2_par_source(indicateurs),
                    config={"displayModeBar": False},
                ),
            ]),
        ]),

        # Section pédagogique
        creer_section_pedagogique(),

        # Footer
        html.Hr(),
        html.P(
            "⚡ Jeu pédagogique — Équilibre du Réseau Électrique — 2026",
            className="footer",
        ),
    ])

    return contenu, sidebar_invest, sidebar_puissance, sidebar_warning


# =============================================================================
# Point d'entrée
# =============================================================================

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8501)
