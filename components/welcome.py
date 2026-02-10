"""
Composant écran d'accueil et section pédagogique.
"""

from dash import html, dcc, dash_table

from data import ORDRE_MERIT, MOYENS_PRODUCTION
from components.charts import graphique_demande_seule
from components.metrics import creer_tableau_caracteristiques
from translations import t


def creer_ecran_accueil(lang: str = "fr") -> html.Div:
    """Construit l'écran d'accueil affiché quand aucune unité n'est sélectionnée."""
    colonnes, donnees = creer_tableau_caracteristiques(lang)

    return html.Div([
        html.Hr(),

        # 3 boîtes objectif / comment jouer / scoring
        html.Div(className="welcome-grid", children=[
            html.Div(className="info-box", children=[
                html.H3(t("accueil_objectif_titre", lang)),
                html.P(t("accueil_objectif_texte", lang)),
            ]),
            html.Div(className="info-box", children=[
                html.H3(t("accueil_comment_titre", lang)),
                html.P(t("accueil_comment_texte", lang)),
            ]),
            html.Div(className="info-box", children=[
                html.H3(t("accueil_scoring_titre", lang)),
                html.P([
                    html.B("Couverture" if lang == "fr" else "Coverage"),
                    t("accueil_scoring_couverture", lang), html.Br(),
                    html.B("CO₂"),
                    t("accueil_scoring_co2", lang), html.Br(),
                    html.B("Coût" if lang == "fr" else "Cost"),
                    t("accueil_scoring_cout", lang),
                ]),
            ]),
        ]),

        # Courbe de demande
        html.H3(t("section_courbe_charge", lang), className="section-title"),
        dcc.Graph(figure=graphique_demande_seule(lang), config={"displayModeBar": False}),

        # Tableau des caractéristiques
        html.H3(t("section_caracteristiques", lang), className="section-title"),
        dash_table.DataTable(
            columns=colonnes,
            data=donnees,
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

        html.Hr(),

        # Conseils
        html.Div(className="info-box", children=[
            html.H4(t("conseils_titre", lang)),
            html.Ul([
                html.Li([
                    html.B(t("label_sources_pilotables", lang)),
                    t("conseil_pilotable", lang),
                ]),
                html.Li([
                    html.B(t("label_sources_intermittentes", lang)),
                    t("conseil_intermittent", lang),
                ]),
                html.Li([
                    html.B("Merit order"),
                    t("conseil_merit", lang),
                ]),
                html.Li([
                    t("conseil_equilibre_pre", lang),
                    html.B(t("conseil_equilibre_bold", lang)),
                    t("conseil_equilibre_post", lang),
                ]),
            ]),
        ]),
    ])


def creer_section_pedagogique(lang: str = "fr") -> html.Details:
    """Crée la section pédagogique repliable."""
    return html.Details(
        style={"marginTop": "1.5rem"},
        children=[
            html.Summary(
                t("pedago_titre", lang),
                style={
                    "cursor": "pointer",
                    "fontSize": "1.1rem",
                    "fontWeight": "600",
                    "color": "#ffffff",
                    "padding": "12px 16px",
                    "backgroundColor": "#1a1f2e",
                    "borderRadius": "8px",
                    "border": "1px solid #333",
                },
            ),
            html.Div(
                style={
                    "backgroundColor": "#1a1f2e",
                    "border": "1px solid #333",
                    "borderTop": "none",
                    "borderRadius": "0 0 8px 8px",
                    "padding": "20px",
                    "lineHeight": "1.7",
                    "color": "#e0e0e0",
                },
                children=[
                    html.H4(t("pedago_merit_titre", lang)),
                    html.P(t("pedago_merit_texte", lang)),
                    html.H4(t("pedago_intermittence_titre", lang)),
                    html.Ul([
                        html.Li(t("pedago_intermittence_1", lang)),
                        html.Li(t("pedago_intermittence_2", lang)),
                        html.Li(t("pedago_intermittence_3", lang)),
                    ]),
                    html.H4(t("pedago_equilibre_titre", lang)),
                    html.P(t("pedago_equilibre_texte", lang)),
                    html.Ul([
                        html.Li([html.B(t("pedago_deficit", lang)), t("pedago_deficit_suite", lang)]),
                        html.Li([html.B(t("pedago_surplus", lang)), t("pedago_surplus_suite", lang)]),
                    ]),
                    html.H4(t("pedago_realite_titre", lang)),
                    html.P(t("pedago_realite_texte", lang)),
                ],
            ),
        ],
    )
