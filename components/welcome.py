"""
Composant écran d'accueil et section pédagogique.
"""

from dash import html, dcc, dash_table

from data import ORDRE_MERIT, MOYENS_PRODUCTION
from components.charts import graphique_demande_seule
from components.metrics import creer_tableau_caracteristiques


def creer_ecran_accueil() -> html.Div:
    """Construit l'écran d'accueil affiché quand aucune unité n'est sélectionnée."""
    colonnes, donnees = creer_tableau_caracteristiques()

    return html.Div([
        html.Hr(),

        # 3 boîtes objectif / comment jouer / scoring
        html.Div(className="welcome-grid", children=[
            html.Div(className="info-box", children=[
                html.H3("🎯 Objectif"),
                html.P(
                    "Couvrir 100% de la demande électrique sur une journée de 24 heures "
                    "en construisant un parc de production optimal."
                ),
            ]),
            html.Div(className="info-box", children=[
                html.H3("📊 Comment jouer"),
                html.P(
                    "Utilisez les curseurs dans le panneau de gauche pour choisir "
                    "le nombre de centrales de chaque type. Les résultats s'afficheront automatiquement."
                ),
            ]),
            html.Div(className="info-box", children=[
                html.H3("🏆 Scoring"),
                html.P([
                    html.B("Couverture"), " (40 pts) — Couvrir toute la demande", html.Br(),
                    html.B("CO₂"), " (30 pts) — Minimiser les émissions", html.Br(),
                    html.B("Coût"), " (30 pts) — Maîtriser le budget",
                ]),
            ]),
        ]),

        # Courbe de demande
        html.H3("📈 Courbe de charge à couvrir (journée type)", className="section-title"),
        dcc.Graph(figure=graphique_demande_seule(), config={"displayModeBar": False}),

        # Tableau des caractéristiques
        html.H3("📋 Caractéristiques des moyens de production", className="section-title"),
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
            html.H4("💡 Conseils"),
            html.Ul([
                html.Li([html.B("Sources pilotables"), " (✅) : produisent à la demande, très utiles pour suivre la courbe de charge."]),
                html.Li([html.B("Sources intermittentes"), " (❌) : produisent selon la météo, pas selon vos besoins. Le solaire ne produit rien la nuit !"]),
                html.Li([html.B("Merit order"), " : les sources les moins chères à produire sont appelées en priorité."]),
                html.Li(["Attention à l'", html.B("équilibre"), " : trop de production = surplus coûteux, pas assez = blackout !"]),
            ]),
        ]),
    ])


def creer_section_pedagogique() -> html.Details:
    """Crée la section pédagogique repliable."""
    return html.Details(
        style={"marginTop": "1.5rem"},
        children=[
            html.Summary(
                "💡 Comprendre les résultats — Guide pédagogique",
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
                    html.H4("Merit Order (Ordre de mérite)"),
                    html.P(
                        "Les centrales sont appelées par ordre de coût marginal croissant : "
                        "d'abord les moins chères à produire (renouvelables, nucléaire), "
                        "puis les plus chères (gaz, charbon, pétrole). "
                        "C'est le même principe utilisé sur les vrais marchés de l'électricité en Europe."
                    ),
                    html.H4("L'intermittence"),
                    html.Ul([
                        html.Li("☀️ Le solaire ne produit que quand il y a du soleil (entre 7h et 20h, pic à 13h)."),
                        html.Li("🌬️ L'éolien produit de façon variable, souvent plus la nuit."),
                        html.Li("Ces sources ne sont pas pilotables : elles produisent indépendamment de la demande."),
                    ]),
                    html.H4("Le défi de l'équilibre"),
                    html.P("À chaque instant, la production doit être exactement égale à la consommation. Un déséquilibre provoque :"),
                    html.Ul([
                        html.Li([html.B("Déficit"), " → coupures de courant (blackout)"]),
                        html.Li([html.B("Surplus"), " → gaspillage d'énergie et coûts inutiles"]),
                    ]),
                    html.H4("Dans la vraie vie"),
                    html.P(
                        "Les producteurs d'électricité exploitent un mix diversifié : centrales à gaz, "
                        "parcs éoliens et solaires, barrages hydroélectriques, et développent le stockage "
                        "d'énergie et l'hydrogène vert. L'enjeu : atteindre la neutralité carbone tout en "
                        "garantissant la sécurité d'approvisionnement."
                    ),
                ],
            ),
        ],
    )
