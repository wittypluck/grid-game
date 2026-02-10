"""
Modèle de données pour le jeu d'équilibrage du réseau électrique.
Définition des moyens de production et de la courbe de charge.
"""

import numpy as np
import pandas as pd

# =============================================================================
# Moyens de production
# =============================================================================
# Chaque moyen de production est défini par :
#   - nom : nom affiché
#   - emoji : icône visuelle
#   - couleur : couleur pour les graphiques
#   - cout_construction : coût de construction par unité (M€)
#   - cout_production : coût marginal de production (€/MWh)
#   - disponibilite : taux de disponibilité moyen (0-1)
#   - co2 : émissions de CO₂ (gCO₂/kWh)
#   - puissance : puissance nominale par unité (MW)
#   - pilotable : si la source est pilotable (True) ou intermittente (False)
#   - description : description pédagogique

MOYENS_PRODUCTION = {
    "charbon": {
        "nom": "Charbon",
        "emoji": "🏭",
        "couleur": "#4a4a4a",
        "cout_construction": 120,
        "cout_production": 95,
        "disponibilite": 0.85,
        "co2": 820,
        "puissance": 600,
        "pilotable": True,
        "max_unites": 120,
        "duree_vie": 40,
        "description": "Centrale thermique à charbon. Très polluante mais fiable et pilotable. "
                       "Coût de production élevé (taxe carbone incluse). Source la plus émettrice de CO₂."
    },
    "gaz": {
        "nom": "Gaz naturel",
        "emoji": "🔥",
        "couleur": "#e67e22",
        "cout_construction": 80,
        "cout_production": 75,
        "disponibilite": 0.90,
        "co2": 490,
        "puissance": 400,
        "pilotable": True,
        "max_unites": 170,
        "duree_vie": 30,
        "description": "Centrale à cycle combiné gaz. Plus flexible et moins polluante que le charbon, "
                       "mais reste une énergie fossile (taxe carbone incluse). Idéal pour les pics."
    },
    "petrole": {
        "nom": "Pétrole",
        "emoji": "🛢️",
        "couleur": "#2c3e50",
        "cout_construction": 80,
        "cout_production": 110,
        "disponibilite": 0.85,
        "co2": 720,
        "puissance": 300,
        "pilotable": True,
        "max_unites": 230,
        "duree_vie": 30,
        "description": "Centrale thermique au fioul. Très coûteuse à exploiter et fortement émettrice. "
                       "Utilisée principalement en dernier recours pour les pointes."
    },
    "nucleaire": {
        "nom": "Nucléaire",
        "emoji": "⚛️",
        "couleur": "#8e44ad",
        "cout_construction": 3500,
        "cout_production": 15,
        "disponibilite": 0.80,
        "co2": 12,
        "puissance": 1300,
        "pilotable": False,
        "max_unites": 60,
        "duree_vie": 60,
        "description": "Centrale nucléaire. Très faible empreinte carbone et coût de production bas, "
                       "mais investissement initial très élevé. Production constante (inertie forte) : "
                       "impossible de moduler rapidement. Idéal pour fournir la base, mais génère du surplus la nuit."
    },
    "hydraulique": {
        "nom": "Hydraulique",
        "emoji": "💧",
        "couleur": "#2980b9",
        "cout_construction": 200,
        "cout_production": 5,
        "disponibilite": 0.55,
        "co2": 24,
        "puissance": 500,
        "pilotable": True,
        "max_unites": 50,
        "duree_vie": 80,
        "description": "Barrage hydroélectrique. Énergie renouvelable, pilotable et très peu émettrice. "
                       "Disponibilité limitée par les ressources en eau."
    },
    "solaire": {
        "nom": "Solaire",
        "emoji": "☀️",
        "couleur": "#f1c40f",
        "cout_construction": 70,
        "cout_production": 3,
        "disponibilite": 0.15,
        "co2": 45,
        "puissance": 100,
        "pilotable": False,
        "max_unites": 100,
        "duree_vie": 25,
        "description": "Parc photovoltaïque. Coût de production quasi nul mais production uniquement "
                       "en journée. Intermittent : dépend de l'ensoleillement."
    },
    "eolien": {
        "nom": "Éolien",
        "emoji": "🌬️",
        "couleur": "#1abc9c",
        "cout_construction": 100,
        "cout_production": 5,
        "disponibilite": 0.25,
        "co2": 11,
        "puissance": 150,
        "pilotable": False,
        "max_unites": 80,
        "duree_vie": 20,
        "description": "Parc éolien. Renouvelable et faible empreinte carbone, mais production variable "
                       "selon le vent. Produit plus la nuit et en hiver."
    },
}

# Ordre des couleurs pour le graphique empilé (du bas vers le haut = merit order)
ORDRE_MERIT = ["nucleaire", "hydraulique", "eolien", "solaire", "charbon", "gaz", "petrole"]


# =============================================================================
# Courbe de charge (demande) — Journée type France métropolitaine
# =============================================================================
# Demande en MW pour chaque heure (0h à 23h)
# Profil réaliste : creux nocturne, pic matin ~9h, creux début d'après-midi, pic soir ~19h

DEMANDE_HORAIRE = np.array([
    32000,  # 00h
    29000,  # 01h
    27000,  # 02h
    26000,  # 03h
    26000,  # 04h
    27000,  # 05h
    31000,  # 06h
    38000,  # 07h
    45000,  # 08h
    48000,  # 09h
    49000,  # 10h
    50000,  # 11h
    48000,  # 12h
    46000,  # 13h
    45000,  # 14h
    46000,  # 15h
    48000,  # 16h
    51000,  # 17h
    55000,  # 18h
    58000,  # 19h - pic du soir
    54000,  # 20h
    48000,  # 21h
    42000,  # 22h
    36000,  # 23h
], dtype=float)

HEURES = list(range(24))
LABELS_HEURES = [f"{h:02d}h" for h in HEURES]


# =============================================================================
# Profils de production intermittente (facteur de charge horaire)
# =============================================================================
# Solaire : production entre 7h et 20h, pic à 13h
PROFIL_SOLAIRE = np.array([
    0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,  # 00h-06h
    0.05, 0.15, 0.35, 0.55, 0.75, 0.90, 1.00,   # 07h-13h
    0.95, 0.80, 0.60, 0.35, 0.15, 0.03, 0.00,   # 14h-20h
    0.00, 0.00, 0.00                               # 21h-23h
])

# Éolien : plus de vent la nuit et en fin de journée
PROFIL_EOLIEN = np.array([
    0.35, 0.38, 0.40, 0.42, 0.40, 0.38, 0.35,   # 00h-06h
    0.30, 0.25, 0.22, 0.20, 0.18, 0.18, 0.20,   # 07h-13h
    0.22, 0.25, 0.28, 0.30, 0.32, 0.35, 0.38,   # 14h-20h
    0.40, 0.38, 0.36                               # 21h-23h
])


def get_demande_dataframe():
    """Retourne la courbe de charge sous forme de DataFrame."""
    return pd.DataFrame({
        "heure": HEURES,
        "label": LABELS_HEURES,
        "demande_mw": DEMANDE_HORAIRE,
    })
