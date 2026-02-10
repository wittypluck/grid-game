"""
Module de traduction — toutes les chaînes de caractères de l'interface.

Usage :
    from translations import t
    t("titre_principal", lang)   # retourne le texte traduit

La langue est passée en paramètre (« fr » ou « en »).
"""

# =============================================================================
# Dictionnaire de traductions  { clé: { "fr": ..., "en": ... } }
# =============================================================================

_TRADUCTIONS: dict[str, dict[str, str]] = {

    # --- Titres et sous-titres ---
    "titre_principal": {
        "fr": "⚡ Équilibre du Réseau Électrique",
        "en": "⚡ Power Grid Balancing",
    },
    "sous_titre": {
        "fr": (
            "Construisez votre mix énergétique pour couvrir la demande française sur 24h. "
            "Minimisez les coûts et les émissions de CO₂ tout en garantissant la sécurité d'approvisionnement."
        ),
        "en": (
            "Build your energy mix to cover France's 24-hour demand. "
            "Minimize costs and CO₂ emissions while ensuring supply security."
        ),
    },

    # --- Sidebar ---
    "sidebar_titre": {
        "fr": "🏗️ Vos investissements",
        "en": "🏗️ Your investments",
    },
    "sidebar_instruction": {
        "fr": "Choisissez le nombre d'unités pour chaque moyen de production :",
        "en": "Choose the number of units for each power source:",
    },
    "sidebar_investissement": {
        "fr": "💰 Investissement : {montant} M€",
        "en": "💰 Investment: {montant} M€",
    },
    "sidebar_puissance": {
        "fr": "⚡ Puissance installée : {puissance} MW",
        "en": "⚡ Installed capacity: {puissance} MW",
    },
    "sidebar_demande_max": {
        "fr": "📊 Demande max : {demande} MW",
        "en": "📊 Peak demand: {demande} MW",
    },
    "sidebar_warning": {
        "fr": "⚠️ Puissance installée inférieure au pic de demande !",
        "en": "⚠️ Installed capacity is below peak demand!",
    },

    # --- Métriques ---
    "metric_score": {
        "fr": "SCORE GLOBAL",
        "en": "OVERALL SCORE",
    },
    "metric_couverture": {
        "fr": "COUVERTURE DEMANDE",
        "en": "DEMAND COVERAGE",
    },
    "metric_cout": {
        "fr": "COÛT TOTAL",
        "en": "TOTAL COST",
    },
    "metric_co2": {
        "fr": "CO₂ ÉMIS",
        "en": "CO₂ EMITTED",
    },
    "metric_blackout": {
        "fr": "HEURES DE BLACKOUT",
        "en": "BLACKOUT HOURS",
    },
    "metric_surplus": {
        "fr": "SURPLUS (-{malus} pts)",
        "en": "SURPLUS (-{malus} pts)",
    },

    # --- Messages d'état ---
    "msg_bravo": {
        "fr": "Bravo !",
        "en": "Well done!",
    },
    "msg_bravo_detail": {
        "fr": (
            " Votre mix couvre 100% de la demande. Aucun blackout ! "
            "Essayez maintenant d'optimiser les coûts et les émissions de CO₂."
        ),
        "en": (
            " Your mix covers 100% of demand. No blackout! "
            "Now try to optimize costs and CO₂ emissions."
        ),
    },
    "msg_presque": {
        "fr": "Presque !",
        "en": "Almost there!",
    },
    "msg_presque_detail": {
        "fr": " Votre mix couvre {couverture}% de la demande, mais il reste ",
        "en": " Your mix covers {couverture}% of demand, but there are still ",
    },
    "msg_presque_blackout": {
        "fr": "{heures} heures de blackout",
        "en": "{heures} blackout hours",
    },
    "msg_presque_fin": {
        "fr": ". Ajoutez de la capacité pour sécuriser l'approvisionnement.",
        "en": ". Add more capacity to secure supply.",
    },
    "msg_alerte": {
        "fr": "Alerte !",
        "en": "Alert!",
    },
    "msg_alerte_detail": {
        "fr": " Votre mix ne couvre que {couverture}% de la demande ! Il y a ",
        "en": " Your mix covers only {couverture}% of demand! There are ",
    },
    "msg_alerte_fin": {
        "fr": ". Vous devez investir dans plus de capacité de production.",
        "en": ". You must invest in more generation capacity.",
    },

    # --- Titres de sections ---
    "section_production_vs_demande": {
        "fr": "📈 Production vs Demande — Vue 24h",
        "en": "📈 Production vs Demand — 24h View",
    },
    "section_mix": {
        "fr": "🥧 Mix énergétique",
        "en": "🥧 Energy Mix",
    },
    "section_score": {
        "fr": "🏆 Décomposition du score",
        "en": "🏆 Score Breakdown",
    },
    "section_details": {
        "fr": "📊 Détails par source de production",
        "en": "📊 Details by Generation Source",
    },
    "section_cout_co2": {
        "fr": "💰 Coût vs CO₂ par source",
        "en": "💰 Cost vs CO₂ by Source",
    },
    "section_courbe_charge": {
        "fr": "📈 Courbe de charge à couvrir (journée type)",
        "en": "📈 Load Curve to Cover (typical day)",
    },
    "section_caracteristiques": {
        "fr": "📋 Caractéristiques des moyens de production",
        "en": "📋 Power Source Characteristics",
    },

    # --- Tableau détails ---
    "col_source": {"fr": "Source", "en": "Source"},
    "col_unites": {"fr": "Unités", "en": "Units"},
    "col_production": {"fr": "Production (MWh)", "en": "Production (MWh)"},
    "col_cout_constr": {"fr": "Coût constr. (M€)", "en": "Constr. cost (M€)"},
    "col_cout_prod": {"fr": "Coût prod. (M€)", "en": "Prod. cost (M€)"},
    "col_co2_tonnes": {"fr": "CO₂ (tonnes)", "en": "CO₂ (tonnes)"},

    # --- Tableau caractéristiques ---
    "col_puissance": {"fr": "Puissance (MW)", "en": "Power (MW)"},
    "col_cout_construction": {"fr": "Coût construction (M€)", "en": "Construction cost (M€)"},
    "col_cout_production": {"fr": "Coût production (€/MWh)", "en": "Production cost (€/MWh)"},
    "col_disponibilite": {"fr": "Disponibilité", "en": "Availability"},
    "col_co2_intensite": {"fr": "CO₂ (gCO₂/kWh)", "en": "CO₂ (gCO₂/kWh)"},
    "col_pilotable": {"fr": "Pilotable", "en": "Dispatchable"},

    # --- Graphiques : axes et légendes ---
    "axe_heure": {"fr": "Heure", "en": "Hour"},
    "axe_heure_journee": {"fr": "Heure de la journée", "en": "Hour of the day"},
    "axe_puissance": {"fr": "Puissance (MW)", "en": "Power (MW)"},
    "axe_cout": {"fr": "Coût (M€)", "en": "Cost (M€)"},
    "axe_co2": {"fr": "CO₂ (tonnes)", "en": "CO₂ (tonnes)"},
    "legende_demande": {"fr": "📊 Demande", "en": "📊 Demand"},
    "legende_deficit": {"fr": "⚠️ Déficit (blackout)", "en": "⚠️ Deficit (blackout)"},
    "legende_construction": {"fr": "Construction", "en": "Construction"},
    "legende_production": {"fr": "Production", "en": "Production"},

    # --- Graphique hover ---
    "hover_production": {"fr": "Production", "en": "Production"},
    "hover_demande": {"fr": "Demande", "en": "Demand"},
    "hover_heure": {"fr": "Heure", "en": "Hour"},
    "hover_part": {"fr": "Part", "en": "Share"},

    # --- Score breakdown ---
    "score_couverture": {"fr": "Couverture\n(/40)", "en": "Coverage\n(/40)"},
    "score_co2": {"fr": "CO₂\n(/30)", "en": "CO₂\n(/30)"},
    "score_cout": {"fr": "Coût\n(/30)", "en": "Cost\n(/30)"},
    "score_surplus": {"fr": "Surplus\n(malus)", "en": "Surplus\n(penalty)"},
    "score_max": {"fr": "Maximum", "en": "Maximum"},
    "score_votre": {"fr": "Votre score", "en": "Your score"},

    # --- Écran d'accueil ---
    "accueil_objectif_titre": {"fr": "🎯 Objectif", "en": "🎯 Objective"},
    "accueil_objectif_texte": {
        "fr": (
            "Couvrir 100% de la demande électrique sur une journée de 24 heures "
            "en construisant un parc de production optimal."
        ),
        "en": (
            "Cover 100% of electricity demand over a 24-hour day "
            "by building an optimal generation fleet."
        ),
    },
    "accueil_comment_titre": {"fr": "📊 Comment jouer", "en": "📊 How to Play"},
    "accueil_comment_texte": {
        "fr": (
            "Utilisez les curseurs dans le panneau de gauche pour choisir "
            "le nombre de centrales de chaque type. Les résultats s'afficheront automatiquement."
        ),
        "en": (
            "Use the sliders in the left panel to choose "
            "the number of plants of each type. Results will update automatically."
        ),
    },
    "accueil_scoring_titre": {"fr": "🏆 Scoring", "en": "🏆 Scoring"},
    "accueil_scoring_couverture": {
        "fr": " (40 pts) — Couvrir toute la demande",
        "en": " (40 pts) — Cover all demand",
    },
    "accueil_scoring_co2": {
        "fr": " (30 pts) — Minimiser les émissions",
        "en": " (30 pts) — Minimize emissions",
    },
    "accueil_scoring_cout": {
        "fr": " (30 pts) — Maîtriser le budget",
        "en": " (30 pts) — Control the budget",
    },

    # --- Conseils ---
    "conseils_titre": {"fr": "💡 Conseils", "en": "💡 Tips"},
    "conseil_pilotable": {
        "fr": " (✅) : produisent à la demande, très utiles pour suivre la courbe de charge.",
        "en": " (✅): produce on demand, very useful for following the load curve.",
    },
    "conseil_intermittent": {
        "fr": " (❌) : produisent selon la météo, pas selon vos besoins. Le solaire ne produit rien la nuit !",
        "en": " (❌): produce depending on weather, not your needs. Solar produces nothing at night!",
    },
    "conseil_merit": {
        "fr": " : les sources les moins chères à produire sont appelées en priorité.",
        "en": ": cheapest sources to operate are called first.",
    },
    "conseil_equilibre_pre": {
        "fr": "Attention à l'",
        "en": "Watch out for the ",
    },
    "conseil_equilibre_bold": {
        "fr": "équilibre",
        "en": "balance",
    },
    "conseil_equilibre_post": {
        "fr": " : trop de production = surplus coûteux, pas assez = blackout !",
        "en": ": too much production = costly surplus, not enough = blackout!",
    },
    "label_sources_pilotables": {
        "fr": "Sources pilotables",
        "en": "Dispatchable sources",
    },
    "label_sources_intermittentes": {
        "fr": "Sources intermittentes",
        "en": "Intermittent sources",
    },

    # --- Section pédagogique ---
    "pedago_titre": {
        "fr": "💡 Comprendre les résultats — Guide pédagogique",
        "en": "💡 Understanding Results — Educational Guide",
    },
    "pedago_merit_titre": {
        "fr": "Merit Order (Ordre de mérite)",
        "en": "Merit Order",
    },
    "pedago_merit_texte": {
        "fr": (
            "Les centrales sont appelées par ordre de coût marginal croissant : "
            "d'abord les moins chères à produire (renouvelables, nucléaire), "
            "puis les plus chères (gaz, charbon, pétrole). "
            "C'est le même principe utilisé sur les vrais marchés de l'électricité en Europe."
        ),
        "en": (
            "Power plants are called in increasing order of marginal cost: "
            "cheapest first (renewables, nuclear), then the most expensive (gas, coal, oil). "
            "This is the same principle used on real European electricity markets."
        ),
    },
    "pedago_intermittence_titre": {
        "fr": "L'intermittence",
        "en": "Intermittency",
    },
    "pedago_intermittence_1": {
        "fr": "☀️ Le solaire ne produit que quand il y a du soleil (entre 7h et 20h, pic à 13h).",
        "en": "☀️ Solar only produces when there is sunlight (between 7am and 8pm, peak at 1pm).",
    },
    "pedago_intermittence_2": {
        "fr": "🌬️ L'éolien produit de façon variable, souvent plus la nuit.",
        "en": "🌬️ Wind production varies, often higher at night.",
    },
    "pedago_intermittence_3": {
        "fr": "Ces sources ne sont pas pilotables : elles produisent indépendamment de la demande.",
        "en": "These sources are not dispatchable: they produce regardless of demand.",
    },
    "pedago_equilibre_titre": {
        "fr": "Le défi de l'équilibre",
        "en": "The Balancing Challenge",
    },
    "pedago_equilibre_texte": {
        "fr": "À chaque instant, la production doit être exactement égale à la consommation. Un déséquilibre provoque :",
        "en": "At every moment, production must exactly equal consumption. An imbalance causes:",
    },
    "pedago_deficit": {
        "fr": "Déficit",
        "en": "Deficit",
    },
    "pedago_deficit_suite": {
        "fr": " → coupures de courant (blackout)",
        "en": " → power cuts (blackout)",
    },
    "pedago_surplus": {
        "fr": "Surplus",
        "en": "Surplus",
    },
    "pedago_surplus_suite": {
        "fr": " → gaspillage d'énergie et coûts inutiles",
        "en": " → energy waste and unnecessary costs",
    },
    "pedago_realite_titre": {
        "fr": "Dans la vraie vie",
        "en": "In Real Life",
    },
    "pedago_realite_texte": {
        "fr": (
            "Les producteurs d'électricité exploitent un mix diversifié : centrales à gaz, "
            "parcs éoliens et solaires, barrages hydroélectriques, et développent le stockage "
            "d'énergie et l'hydrogène vert. L'enjeu : atteindre la neutralité carbone tout en "
            "garantissant la sécurité d'approvisionnement."
        ),
        "en": (
            "Power producers operate a diversified mix: gas plants, wind and solar farms, "
            "hydroelectric dams, and are developing energy storage and green hydrogen. "
            "The challenge: achieving carbon neutrality while ensuring supply security."
        ),
    },

    # --- Footer ---
    "footer": {
        "fr": "⚡ Jeu pédagogique — Équilibre du Réseau Électrique — 2026",
        "en": "⚡ Educational Game — Power Grid Balancing — 2026",
    },
}


# =============================================================================
# Noms des sources en anglais (pour les charts et tableaux)
# =============================================================================

NOMS_SOURCES_EN = {
    "charbon": "Coal",
    "gaz": "Natural Gas",
    "petrole": "Oil",
    "nucleaire": "Nuclear",
    "hydraulique": "Hydro",
    "solaire": "Solar",
    "eolien": "Wind",
}


# =============================================================================
# Fonction d'accès
# =============================================================================

def t(cle: str, lang: str = "fr") -> str:
    """
    Retourne la traduction de la clé dans la langue demandée.
    Fallback sur le français si la clé ou la langue n'existe pas.
    """
    entry = _TRADUCTIONS.get(cle)
    if entry is None:
        return cle
    return entry.get(lang, entry.get("fr", cle))


def nom_source(source_id: str, lang: str = "fr") -> str:
    """Retourne le nom affiché d'une source selon la langue."""
    from data import MOYENS_PRODUCTION
    if lang == "en":
        return NOMS_SOURCES_EN.get(source_id, source_id)
    return MOYENS_PRODUCTION[source_id]["nom"]
