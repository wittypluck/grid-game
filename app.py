"""
⚡ Équilibre du Réseau Électrique
Application Dash principale — point d'entrée et callbacks.
"""

from dash import Dash, html, dcc, dash_table, Input, Output, State, callback, clientside_callback

from data import MOYENS_PRODUCTION, DEMANDE_HORAIRE, ORDRE_MERIT
from simulation import calculer_production_horaire, calculer_indicateurs
from translations import t

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
    # Store pour la langue sélectionnée
    dcc.Store(id="lang-store", data="fr"),

    # Sidebar (reconstruite dynamiquement lors du changement de langue)
    html.Div(id="sidebar-wrapper", children=[creer_sidebar("fr")]),

    # Zone principale
    html.Div(className="main-content", children=[
        # Sélecteur de langue (drapeaux) — en haut à droite
        html.Div(className="lang-switcher", children=[
            html.Button(
                "🇫🇷", id="btn-lang-fr", className="lang-btn lang-btn-active",
                title="Français", n_clicks=0,
            ),
            html.Button(
                "🇬🇧", id="btn-lang-en", className="lang-btn",
                title="English", n_clicks=0,
            ),
        ]),

        html.H1(id="main-title", className="main-title"),
        html.P(id="main-subtitle", className="subtitle"),

        # Contenu dynamique (accueil ou résultats)
        html.Div(id="contenu-principal"),
    ]),
])


# =============================================================================
# Callback de sélection de langue (clientside pour la réactivité)
# =============================================================================

clientside_callback(
    """
    function(n_fr, n_en, current_lang) {
        const ctx = dash_clientside.callback_context;
        if (!ctx.triggered.length) return current_lang || "fr";
        const triggered_id = ctx.triggered[0].prop_id.split(".")[0];
        return triggered_id === "btn-lang-fr" ? "fr" : "en";
    }
    """,
    Output("lang-store", "data"),
    Input("btn-lang-fr", "n_clicks"),
    Input("btn-lang-en", "n_clicks"),
    State("lang-store", "data"),
)


# =============================================================================
# Callback pour le style actif des boutons de langue
# =============================================================================

clientside_callback(
    """
    function(lang) {
        return [
            lang === "fr" ? "lang-btn lang-btn-active" : "lang-btn",
            lang === "en" ? "lang-btn lang-btn-active" : "lang-btn"
        ];
    }
    """,
    Output("btn-lang-fr", "className"),
    Output("btn-lang-en", "className"),
    Input("lang-store", "data"),
)


# =============================================================================
# Callback principal — mis à jour à chaque changement de slider ou de langue
# =============================================================================

@callback(
    Output("contenu-principal", "children"),
    Output("main-title", "children"),
    Output("main-subtitle", "children"),
    Output("sidebar-wrapper", "children"),
    Output("sidebar-investissement", "children"),
    Output("sidebar-puissance", "children"),
    Output("sidebar-warning", "children"),
    Input("lang-store", "data"),
    [Input(f"slider-{source_id}", "value") for source_id in ORDRE_MERIT],
)
def mettre_a_jour(lang, *slider_values):
    """Callback principal : recalcule tout à chaque changement de slider ou de langue."""
    lang = lang or "fr"
    choix_joueur = lire_choix_joueur(slider_values)

    # --- Titres ---
    titre = t("titre_principal", lang)
    sous_titre = t("sous_titre", lang)

    # --- Sidebar reconstruite (pour la langue des labels) ---
    sidebar = creer_sidebar(lang, choix_joueur)

    # --- Résumé sidebar ---
    cout_construction = sum(
        (v or 0) * MOYENS_PRODUCTION[s]["cout_construction"]
        for s, v in choix_joueur.items()
    )
    puissance_installee = sum(
        (v or 0) * MOYENS_PRODUCTION[s]["puissance"]
        for s, v in choix_joueur.items()
    )

    sidebar_invest = t("sidebar_investissement", lang).format(montant=f"{cout_construction:,.0f}")
    sidebar_puissance = t("sidebar_puissance", lang).format(puissance=f"{puissance_installee:,.0f}")

    sidebar_warning = None
    if puissance_installee < DEMANDE_HORAIRE.max():
        sidebar_warning = html.Div(
            t("sidebar_warning", lang),
            className="sidebar-warning",
        )

    # --- Contenu principal ---
    total_unites = sum(choix_joueur.values())

    if total_unites == 0:
        return (
            creer_ecran_accueil(lang), titre, sous_titre,
            sidebar, sidebar_invest, sidebar_puissance, sidebar_warning,
        )

    # Simulation
    df_prod = calculer_production_horaire(choix_joueur)
    indicateurs = calculer_indicateurs(choix_joueur, df_prod)

    # Tableau détaillé
    colonnes_detail, donnees_detail = creer_tableau_details(indicateurs, lang)

    contenu = html.Div([
        html.Hr(),

        # Métriques
        creer_metriques(indicateurs, lang),

        # Message d'état
        creer_message_etat(indicateurs, lang),

        # Graphique principal
        html.H3(t("section_production_vs_demande", lang), className="section-title"),
        dcc.Graph(
            figure=graphique_production_vs_demande(df_prod, choix_joueur, lang),
            config={"displayModeBar": False},
        ),

        # Graphiques secondaires côte à côte
        html.Div(className="charts-row", children=[
            html.Div([
                html.H3(t("section_mix", lang), className="section-title"),
                dcc.Graph(
                    figure=graphique_mix_energetique(df_prod, choix_joueur, lang),
                    config={"displayModeBar": False},
                ),
            ]),
            html.Div([
                html.H3(t("section_score", lang), className="section-title"),
                dcc.Graph(
                    figure=graphique_decomposition_score(indicateurs, lang),
                    config={"displayModeBar": False},
                ),
            ]),
        ]),

        # Tableau détaillé
        html.H3(t("section_details", lang), className="section-title"),
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
        html.H3(t("section_cout_co2", lang), className="section-title"),
        html.Div(className="charts-row", children=[
            html.Div([
                dcc.Graph(
                    figure=graphique_cout_par_source(indicateurs, lang),
                    config={"displayModeBar": False},
                ),
            ]),
            html.Div([
                dcc.Graph(
                    figure=graphique_co2_par_source(indicateurs, lang),
                    config={"displayModeBar": False},
                ),
            ]),
        ]),

        # Section pédagogique
        creer_section_pedagogique(lang),

        # Footer
        html.Hr(),
        html.P(t("footer", lang), className="footer"),
    ])

    return (
        contenu, titre, sous_titre,
        sidebar, sidebar_invest, sidebar_puissance, sidebar_warning,
    )


# =============================================================================
# Point d'entrée
# =============================================================================

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8501)
