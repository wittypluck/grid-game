"""
🔌 Équilibre du Réseau Électrique
Application Streamlit principale.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

from data import MOYENS_PRODUCTION, DEMANDE_HORAIRE, LABELS_HEURES, ORDRE_MERIT
from simulation import calculer_production_horaire, calculer_indicateurs, get_puissance_installee

# =============================================================================
# Configuration de la page
# =============================================================================
st.set_page_config(
    page_title="⚡ Équilibre du Réseau Électrique",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# CSS personnalisé aux couleurs Engie
# =============================================================================
st.markdown("""
<style>
    :root {
        --primary-blue: #00AAFF;
        --primary-green: #A0D911;
        --primary-dark: #1B2A4A;
    }

    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }

    /* Titres de sections (h3, h4) */
    .stApp h3, .stApp h4 {
        color: #ffffff !important;
    }

    /* Texte dans les expanders */
    .stApp .streamlit-expanderContent p,
    .stApp .streamlit-expanderContent li,
    .stApp .streamlit-expanderContent h4 {
        color: #e0e0e0 !important;
    }

    /* Markdown général */
    .stApp .stMarkdown p,
    .stApp .stMarkdown li {
        color: #d0d0d0 !important;
    }

    .main-title {
        background: linear-gradient(135deg, #00AAFF, #A0D911);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0;
    }

    .subtitle {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: linear-gradient(135deg, #1a1f2e, #252b3b);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #333;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #aaa;
        margin-top: 4px;
    }

    .score-badge {
        display: inline-block;
        font-size: 3rem;
        font-weight: 800;
        padding: 10px 30px;
        border-radius: 16px;
        text-align: center;
    }

    .source-card {
        background: #1a1f2e;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 8px;
        border-left: 4px solid;
    }

    div[data-testid="stSidebar"] {
        background-color: #151922;
    }

    .info-box {
        background: #1a2332;
        border-left: 4px solid #00AAFF;
        padding: 15px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
    }

    .warning-box {
        background: #2a1a1a;
        border-left: 4px solid #ff4444;
        padding: 15px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
    }

    .success-box {
        background: #1a2a1a;
        border-left: 4px solid #44ff44;
        padding: 15px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# En-tête
# =============================================================================
st.markdown('<h1 class="main-title">⚡ Équilibre du Réseau Électrique</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Construisez votre mix énergétique pour couvrir la demande française sur 24h.<br>'
            'Minimisez les coûts et les émissions de CO₂ tout en garantissant la sécurité d\'approvisionnement.</p>',
            unsafe_allow_html=True)


# =============================================================================
# Sidebar — Sélection des moyens de production
# =============================================================================
st.sidebar.markdown("## 🏗️ Vos investissements")
st.sidebar.markdown("Choisissez le nombre d'unités pour chaque moyen de production :")

st.sidebar.markdown("---")

choix_joueur = {}
cout_construction_preview = 0

for source_id in ORDRE_MERIT:
    info = MOYENS_PRODUCTION[source_id]
    emoji = info["emoji"]
    nom = info["nom"]

    with st.sidebar.container():
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            st.markdown(f"**{emoji} {nom}**")
            st.caption(f"{info['puissance']} MW | {info['cout_construction']} M€ | "
                       f"{info['co2']} gCO₂/kWh")

        nb = st.sidebar.slider(
            f"Nombre de {nom}",
            min_value=0,
            max_value=info["max_unites"],
            value=0,
            key=f"slider_{source_id}",
            label_visibility="collapsed"
        )
        choix_joueur[source_id] = nb
        cout_construction_preview += nb * info["cout_construction"]

st.sidebar.markdown("---")
st.sidebar.markdown(f"### 💰 Investissement : {cout_construction_preview:,.0f} M€")

puissance_totale_installee = sum(
    choix_joueur[s] * MOYENS_PRODUCTION[s]["puissance"] for s in choix_joueur
)
st.sidebar.markdown(f"### ⚡ Puissance installée : {puissance_totale_installee:,.0f} MW")
st.sidebar.markdown(f"📊 Demande max : **{int(DEMANDE_HORAIRE.max()):,} MW**")

if puissance_totale_installee < DEMANDE_HORAIRE.max():
    st.sidebar.warning("⚠️ Puissance installée inférieure au pic de demande !")


# =============================================================================
# Vérifier si le joueur a fait des choix
# =============================================================================
total_unites = sum(choix_joueur.values())

if total_unites == 0:
    # Écran d'accueil
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="info-box">
            <h3>🎯 Objectif</h3>
            <p>Couvrir 100% de la demande électrique sur une journée de 24 heures
            en construisant un parc de production optimal.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="info-box">
            <h3>📊 Comment jouer</h3>
            <p>Utilisez les curseurs dans le panneau de gauche pour choisir
            le nombre de centrales de chaque type. Les résultats s'afficheront automatiquement.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="info-box">
            <h3>🏆 Scoring</h3>
            <p><b>Couverture</b> (40 pts) — Couvrir toute la demande<br>
            <b>CO₂</b> (30 pts) — Minimiser les émissions<br>
            <b>Coût</b> (30 pts) — Maîtriser le budget</p>
        </div>
        """, unsafe_allow_html=True)

    # Afficher la courbe de demande seule
    st.markdown("### 📈 Courbe de charge à couvrir (journée type)")

    fig_demande = go.Figure()
    fig_demande.add_trace(go.Scatter(
        x=LABELS_HEURES, y=DEMANDE_HORAIRE,
        mode='lines+markers',
        name='Demande',
        line=dict(color='#ff6b6b', width=3),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(255, 107, 107, 0.15)',
    ))
    fig_demande.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Heure",
        yaxis_title="Puissance (MW)",
        height=400,
        margin=dict(l=60, r=30, t=30, b=60),
        yaxis=dict(range=[0, DEMANDE_HORAIRE.max() * 1.15]),
    )
    st.plotly_chart(fig_demande, width='stretch')

    # Tableau des caractéristiques
    st.markdown("### 📋 Caractéristiques des moyens de production")

    data_table = []
    for source_id in ORDRE_MERIT:
        info = MOYENS_PRODUCTION[source_id]
        data_table.append({
            "": f"{info['emoji']}",
            "Source": info["nom"],
            "Puissance (MW)": info["puissance"],
            "Coût construction (M€)": info["cout_construction"],
            "Coût production (€/MWh)": info["cout_production"],
            "Disponibilité": f"{info['disponibilite']*100:.0f}%",
            "CO₂ (gCO₂/kWh)": info["co2"],
            "Pilotable": "✅" if info["pilotable"] else "❌",
        })

    df_table = pd.DataFrame(data_table)
    st.dataframe(df_table, width='stretch', hide_index=True)

    st.markdown("---")
    st.markdown("""
    <div class="info-box">
        <h4>💡 Conseils</h4>
        <ul>
            <li><b>Sources pilotables</b> (✅) : produisent à la demande, très utiles pour suivre la courbe de charge.</li>
            <li><b>Sources intermittentes</b> (❌) : produisent selon la météo, pas selon vos besoins. Le solaire ne produit rien la nuit !</li>
            <li><b>Merit order</b> : les sources les moins chères à produire sont appelées en priorité.</li>
            <li>Attention à l'<b>équilibre</b> : trop de production = surplus coûteux, pas assez = blackout !</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# =============================================================================
# SIMULATION
# =============================================================================
df_prod = calculer_production_horaire(choix_joueur)
indicateurs = calculer_indicateurs(choix_joueur, df_prod)


# =============================================================================
# Indicateurs clés en haut
# =============================================================================
st.markdown("---")

col1, col2, col3, col4, col5, col6 = st.columns(6)

# Score
score = indicateurs["score_total"]
if score >= 70:
    score_color = "#44ff44"
    score_emoji = "🏆"
elif score >= 40:
    score_color = "#ffaa00"
    score_emoji = "📊"
else:
    score_color = "#ff4444"
    score_emoji = "⚠️"

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: {score_color}">{score_emoji} {score}/100</div>
        <div class="metric-label">SCORE GLOBAL</div>
    </div>
    """, unsafe_allow_html=True)

# Couverture
couverture = indicateurs["taux_couverture"]
couv_color = "#44ff44" if couverture >= 100 else "#ffaa00" if couverture >= 90 else "#ff4444"
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: {couv_color}">{couverture}%</div>
        <div class="metric-label">COUVERTURE DEMANDE</div>
    </div>
    """, unsafe_allow_html=True)

# Coût total
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #00AAFF">{indicateurs['cout_total']:,.0f} M€</div>
        <div class="metric-label">COÛT TOTAL</div>
    </div>
    """, unsafe_allow_html=True)

# CO₂
with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #A0D911">{indicateurs['co2_total']:,.0f} t</div>
        <div class="metric-label">CO₂ ÉMIS</div>
    </div>
    """, unsafe_allow_html=True)

# Heures de déficit
with col5:
    deficit_color = "#44ff44" if indicateurs["heures_deficit"] == 0 else "#ff4444"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: {deficit_color}">{indicateurs['heures_deficit']}h / 24h</div>
        <div class="metric-label">HEURES DE BLACKOUT</div>
    </div>
    """, unsafe_allow_html=True)

# Surplus
with col6:
    surplus_pct = indicateurs.get("ratio_surplus", 0)
    surplus_color = "#44ff44" if surplus_pct < 5 else "#ffaa00" if surplus_pct < 20 else "#ff4444"
    malus = indicateurs.get("malus_surplus", 0)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: {surplus_color}">{surplus_pct}%</div>
        <div class="metric-label">SURPLUS (-{malus:.0f} pts)</div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# Messages d'état
# =============================================================================
if indicateurs["taux_couverture"] >= 100 and indicateurs["heures_deficit"] == 0:
    st.markdown("""
    <div class="success-box">
        ✅ <b>Bravo !</b> Votre mix couvre 100% de la demande. Aucun blackout !
        Essayez maintenant d'optimiser les coûts et les émissions de CO₂.
    </div>
    """, unsafe_allow_html=True)
elif indicateurs["taux_couverture"] >= 90:
    st.markdown(f"""
    <div class="warning-box">
        ⚠️ <b>Presque !</b> Votre mix couvre {indicateurs['taux_couverture']}% de la demande,
        mais il reste <b>{indicateurs['heures_deficit']} heures de blackout</b>.
        Ajoutez de la capacité pour sécuriser l'approvisionnement.
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="warning-box">
        🚨 <b>Alerte !</b> Votre mix ne couvre que {indicateurs['taux_couverture']}% de la demande !
        Il y a <b>{indicateurs['heures_deficit']} heures de blackout</b>.
        Vous devez investir dans plus de capacité de production.
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# Graphique principal : Production empilée vs Demande
# =============================================================================
st.markdown("### 📈 Production vs Demande — Vue 24h")

fig_main = go.Figure()

# Production empilée par source (merit order)
sources_a_afficher = [s for s in ORDRE_MERIT if choix_joueur.get(s, 0) > 0]

def hex_to_rgba(hex_color, alpha=0.8):
    """Convertit une couleur hex en rgba."""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

for source_id in sources_a_afficher:
    info = MOYENS_PRODUCTION[source_id]
    fig_main.add_trace(go.Scatter(
        x=LABELS_HEURES,
        y=df_prod[source_id],
        name=f"{info['emoji']} {info['nom']}",
        stackgroup='production',
        fillcolor=hex_to_rgba(info["couleur"], 0.8),
        line=dict(width=0.5, color=info["couleur"]),
        hovertemplate=f"<b>{info['nom']}</b><br>" +
                      "Heure: %{x}<br>" +
                      "Production: %{y:,.0f} MW<br>" +
                      "<extra></extra>",
    ))

# Courbe de demande par-dessus
fig_main.add_trace(go.Scatter(
    x=LABELS_HEURES,
    y=DEMANDE_HORAIRE,
    name='📊 Demande',
    mode='lines+markers',
    line=dict(color='#ff6b6b', width=3, dash='dot'),
    marker=dict(size=6, color='#ff6b6b'),
    hovertemplate="<b>Demande</b><br>" +
                  "Heure: %{x}<br>" +
                  "Demande: %{y:,.0f} MW<br>" +
                  "<extra></extra>",
))

# Zones de déficit
deficit_mask = df_prod["deficit"] > 0
if deficit_mask.any():
    fig_main.add_trace(go.Scatter(
        x=LABELS_HEURES,
        y=np.where(deficit_mask, DEMANDE_HORAIRE, None),
        name='⚠️ Déficit (blackout)',
        mode='markers',
        marker=dict(size=12, color='red', symbol='x'),
    ))

fig_main.update_layout(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis_title="Heure de la journée",
    yaxis_title="Puissance (MW)",
    height=500,
    margin=dict(l=60, r=30, t=30, b=60),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.25,
        xanchor="center",
        x=0.5,
    ),
    hovermode="x unified",
    yaxis=dict(range=[0, max(DEMANDE_HORAIRE.max(), df_prod["production_totale"].max()) * 1.1]),
)

st.plotly_chart(fig_main, width='stretch')


# =============================================================================
# Graphiques secondaires
# =============================================================================
col_left, col_right = st.columns(2)

# --- Mix énergétique (camembert) ---
with col_left:
    st.markdown("### 🥧 Mix énergétique")

    prod_par_source = {}
    for source_id in sources_a_afficher:
        prod_total = df_prod[source_id].sum()
        if prod_total > 0:
            prod_par_source[source_id] = prod_total

    if prod_par_source:
        fig_mix = go.Figure(data=[go.Pie(
            labels=[f"{MOYENS_PRODUCTION[s]['emoji']} {MOYENS_PRODUCTION[s]['nom']}" for s in prod_par_source],
            values=list(prod_par_source.values()),
            marker_colors=[MOYENS_PRODUCTION[s]["couleur"] for s in prod_par_source],
            hole=0.4,
            textinfo='label+percent',
            textposition='outside',
            hovertemplate="<b>%{label}</b><br>" +
                          "Production: %{value:,.0f} MWh<br>" +
                          "Part: %{percent}<br>" +
                          "<extra></extra>",
        )])
        fig_mix.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=False,
        )
        st.plotly_chart(fig_mix, width='stretch')

# --- Décomposition des scores ---
with col_right:
    st.markdown("### 🏆 Décomposition du score")

    fig_score = go.Figure()

    categories = ['Couverture\n(/40)', 'CO₂\n(/30)', 'Coût\n(/30)', 'Surplus\n(malus)']
    valeurs = [indicateurs["score_couverture"], indicateurs["score_co2"], indicateurs["score_cout"], -indicateurs.get("malus_surplus", 0)]
    max_valeurs = [40, 30, 30, 0]
    couleurs = [couv_color, '#A0D911', '#00AAFF', '#ff4444']

    fig_score.add_trace(go.Bar(
        x=categories,
        y=max_valeurs,
        name='Maximum',
        marker_color='rgba(100,100,100,0.3)',
        hoverinfo='skip',
    ))

    fig_score.add_trace(go.Bar(
        x=categories,
        y=valeurs,
        name='Votre score',
        marker_color=couleurs,
        text=[f"{v:+.0f}" if v < 0 else f"{v:.0f}" for v in valeurs],
        textposition='auto',
        textfont=dict(size=16, color='white'),
    ))

    fig_score.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(l=40, r=20, t=20, b=60),
        barmode='overlay',
        showlegend=False,
        yaxis=dict(range=[-30, 45]),
    )
    st.plotly_chart(fig_score, width='stretch')


# =============================================================================
# Détails par source
# =============================================================================
st.markdown("### 📊 Détails par source de production")

if indicateurs["details_par_source"]:
    detail_data = []
    for source_id, detail in indicateurs["details_par_source"].items():
        info = MOYENS_PRODUCTION[source_id]
        detail_data.append({
            "": info["emoji"],
            "Source": detail["nom"],
            "Unités": detail["nb_unites"],
            "Production (MWh)": f"{detail['production_mwh']:,.0f}",
            "Coût constr. (M€)": f"{detail['cout_construction']:,.0f}",
            "Coût prod. (M€)": f"{detail['cout_production']:,.1f}",
            "CO₂ (tonnes)": f"{detail['co2_tonnes']:,.0f}",
        })

    df_details = pd.DataFrame(detail_data)
    st.dataframe(df_details, width='stretch', hide_index=True)


# =============================================================================
# Graphique Coût vs CO₂
# =============================================================================
st.markdown("### 💰 Coût vs CO₂ par source")

col_a, col_b = st.columns(2)

with col_a:
    # Barres de coût par source
    if indicateurs["details_par_source"]:
        sources_detail = list(indicateurs["details_par_source"].keys())
        fig_cout = go.Figure()

        fig_cout.add_trace(go.Bar(
            x=[MOYENS_PRODUCTION[s]["nom"] for s in sources_detail],
            y=[indicateurs["details_par_source"][s]["cout_construction"] for s in sources_detail],
            name="Construction",
            marker_color="#00AAFF",
        ))
        fig_cout.add_trace(go.Bar(
            x=[MOYENS_PRODUCTION[s]["nom"] for s in sources_detail],
            y=[indicateurs["details_par_source"][s]["cout_production"] for s in sources_detail],
            name="Production",
            marker_color="#A0D911",
        ))
        fig_cout.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            barmode='stack',
            height=350,
            margin=dict(l=40, r=20, t=20, b=60),
            yaxis_title="Coût (M€)",
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig_cout, width='stretch')

with col_b:
    # Barres de CO₂ par source
    if indicateurs["details_par_source"]:
        fig_co2 = go.Figure()
        fig_co2.add_trace(go.Bar(
            x=[MOYENS_PRODUCTION[s]["nom"] for s in sources_detail],
            y=[indicateurs["details_par_source"][s]["co2_tonnes"] for s in sources_detail],
            marker_color=[MOYENS_PRODUCTION[s]["couleur"] for s in sources_detail],
            text=[f"{indicateurs['details_par_source'][s]['co2_tonnes']:,.0f}" for s in sources_detail],
            textposition='auto',
        ))
        fig_co2.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=350,
            margin=dict(l=40, r=20, t=20, b=60),
            yaxis_title="CO₂ (tonnes)",
            showlegend=False,
        )
        st.plotly_chart(fig_co2, width='stretch')


# =============================================================================
# Section pédagogique
# =============================================================================
with st.expander("💡 Comprendre les résultats — Guide pédagogique"):
    st.markdown("""
    #### Merit Order (Ordre de mérite)
    Les centrales sont appelées par **ordre de coût marginal croissant** :
    d'abord les moins chères à produire (renouvelables, nucléaire), puis les plus chères (gaz, charbon, pétrole).
    C'est le même principe utilisé sur les vrais marchés de l'électricité en Europe.

    #### L'intermittence
    - ☀️ Le **solaire** ne produit que quand il y a du soleil (entre 7h et 20h, pic à 13h).
    - 🌬️ L'**éolien** produit de façon variable, souvent plus la nuit.
    - Ces sources **ne sont pas pilotables** : elles produisent indépendamment de la demande.

    #### Le défi de l'équilibre
    À chaque instant, **la production doit être exactement égale à la consommation**.
    Un déséquilibre provoque :
    - **Déficit** → coupures de courant (blackout)
    - **Surplus** → gaspillage d'énergie et coûts inutiles

    #### Dans la vraie vie
    Les producteurs d'électricité exploitent un mix diversifié : centrales à gaz, parcs éoliens et solaires,
    barrages hydroélectriques, et développent le stockage d'énergie et l'hydrogène vert.
    L'enjeu : atteindre la **neutralité carbone** tout en garantissant la **sécurité d'approvisionnement**.
    """)


# =============================================================================
# Footer
# =============================================================================
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #666; font-size: 0.8rem;">'
    '⚡ Jeu pédagogique — Équilibre du Réseau Électrique — 2026</p>',
    unsafe_allow_html=True,
)
