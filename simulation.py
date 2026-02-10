"""
Moteur de simulation du réseau électrique.
Dispatch de la production selon le merit order, calcul des coûts et émissions.
"""

import numpy as np
import pandas as pd
from data import (
    MOYENS_PRODUCTION, DEMANDE_HORAIRE, HEURES, LABELS_HEURES,
    PROFIL_SOLAIRE, PROFIL_EOLIEN, ORDRE_MERIT
)


def calculer_production_horaire(choix_joueur: dict) -> pd.DataFrame:
    """
    Calcule la production horaire de chaque source sur 24h.

    Args:
        choix_joueur: dict {type_source: nombre_unites, ...}
                      ex: {"nucleaire": 2, "solaire": 5, "eolien": 3}

    Returns:
        DataFrame avec colonnes : heure, label, demande_mw,
        + une colonne par source active (MW produits),
        + production_totale, deficit, surplus
    """
    df = pd.DataFrame({
        "heure": HEURES,
        "label": LABELS_HEURES,
        "demande_mw": DEMANDE_HORAIRE.copy(),
    })

    # Calculer la capacité disponible par source et par heure
    # Dispatch en 2 passes :
    #   1. Sources NON-pilotables (nucléaire, solaire, éolien) : produisent tout ce qu'elles peuvent
    #   2. Sources pilotables (hydro, gaz, charbon, pétrole) : comblent le gap restant (merit order)

    sources_actives = {k: v for k, v in choix_joueur.items() if v > 0}

    # Séparer pilotables et non-pilotables
    sources_non_pilotables = sorted(
        [s for s in sources_actives if not MOYENS_PRODUCTION[s]["pilotable"]],
        key=lambda s: MOYENS_PRODUCTION[s]["cout_production"]
    )
    sources_pilotables = sorted(
        [s for s in sources_actives if MOYENS_PRODUCTION[s]["pilotable"]],
        key=lambda s: MOYENS_PRODUCTION[s]["cout_production"]
    )

    # Initialiser les colonnes de production
    for source in MOYENS_PRODUCTION:
        df[source] = 0.0

    # Pour chaque heure, dispatcher la production
    for h in range(24):
        demande_restante = DEMANDE_HORAIRE[h]

        # Passe 1 : sources non-pilotables — produisent tout ce qu'elles peuvent
        for source in sources_non_pilotables:
            info = MOYENS_PRODUCTION[source]
            nb_unites = sources_actives[source]
            capacite_nominale = nb_unites * info["puissance"]

            # Appliquer le facteur de disponibilité selon la source
            if source == "solaire":
                facteur = PROFIL_SOLAIRE[h]
            elif source == "eolien":
                facteur = PROFIL_EOLIEN[h]
            else:
                # Nucléaire : production constante à son taux de disponibilité
                facteur = info["disponibilite"]

            production = capacite_nominale * facteur
            df.at[h, source] = production
            demande_restante -= production

        # Passe 2 : sources pilotables — comblent le gap (merit order par coût croissant)
        for source in sources_pilotables:
            info = MOYENS_PRODUCTION[source]
            nb_unites = sources_actives[source]
            capacite_nominale = nb_unites * info["puissance"]
            capacite_disponible = capacite_nominale * info["disponibilite"]

            # Ne produire que ce qui est encore nécessaire
            production = min(capacite_disponible, max(0, demande_restante))
            df.at[h, source] = production
            demande_restante -= production

    # Calcul des totaux
    colonnes_production = [s for s in MOYENS_PRODUCTION if s in df.columns]
    df["production_totale"] = df[colonnes_production].sum(axis=1)
    df["deficit"] = np.maximum(0, df["demande_mw"] - df["production_totale"])
    df["surplus"] = np.maximum(0, df["production_totale"] - df["demande_mw"])

    return df


def calculer_indicateurs(choix_joueur: dict, df_production: pd.DataFrame) -> dict:
    """
    Calcule les indicateurs globaux de performance.

    Returns:
        dict avec coût_construction, coût_production, coût_total,
        co2_total, taux_couverture, energie_totale_produite,
        energie_totale_demandee, heures_deficit, details_par_source
    """
    sources_actives = {k: v for k, v in choix_joueur.items() if v > 0}

    # --- Coût de construction total (M€) ---
    cout_construction = sum(
        MOYENS_PRODUCTION[s]["cout_construction"] * n
        for s, n in sources_actives.items()
    )

    # --- Coût de production total (M€) ---
    # Pour chaque source : production en MWh × coût marginal
    cout_production = 0
    details = {}
    for source in sources_actives:
        info = MOYENS_PRODUCTION[source]
        # Production totale en MWh (chaque pas = 1h, donc MW = MWh)
        prod_mwh = df_production[source].sum()
        cout_prod_source = prod_mwh * info["cout_production"] / 1e6  # en M€
        co2_source = prod_mwh * info["co2"] * 1000 / 1e6  # en tonnes CO₂ (gCO₂/kWh → tCO₂)
        cout_production += cout_prod_source

        details[source] = {
            "nom": info["nom"],
            "nb_unites": sources_actives[source],
            "production_mwh": prod_mwh,
            "cout_construction": MOYENS_PRODUCTION[source]["cout_construction"] * sources_actives[source],
            "cout_production": cout_prod_source,
            "co2_tonnes": co2_source,
        }

    # --- CO₂ total (tonnes) ---
    co2_total = sum(d["co2_tonnes"] for d in details.values())

    # --- Couverture de la demande ---
    energie_demandee = df_production["demande_mw"].sum()
    energie_deficit = df_production["deficit"].sum()
    taux_couverture = ((energie_demandee - energie_deficit) / energie_demandee) * 100

    heures_deficit = (df_production["deficit"] > 0).sum()
    heures_surplus = (df_production["surplus"] > 0).sum()

    # --- Coût amorti annuel (LCOE-like) ---
    # On amortit le coût de construction sur la durée de vie de chaque source
    # puis on ajoute le coût de production annualisé
    cout_amorti_annuel = 0  # M€/an
    for source in sources_actives:
        info = MOYENS_PRODUCTION[source]
        nb = sources_actives[source]
        duree_vie = info.get("duree_vie", 30)
        # Construction amortie par an
        cout_amorti_annuel += (nb * info["cout_construction"]) / duree_vie
    # Production annualisée (coût journalier × 365)
    cout_amorti_annuel += cout_production * 365

    # Énergie annuelle produite (MWh)
    energie_produite_jour = df_production["production_totale"].sum()
    energie_annuelle = max(1, energie_produite_jour * 365)

    # LCOE en €/MWh
    lcoe = (cout_amorti_annuel * 1e6) / energie_annuelle

    cout_total = cout_construction + cout_production

    # --- Score composite ---
    # Score sur 100 basé sur 4 critères :
    # 1. Couverture (40 pts) : 40 pts si 100%, 0 si < 80%
    # 2. CO₂ (30 pts) : comparé à un scénario 100% charbon
    # 3. Coût (30 pts) : basé sur le LCOE (coût amorti par MWh)
    # 4. Malus surplus : pénalité proportionnelle à la surproduction

    # Score couverture
    if taux_couverture >= 100:
        score_couverture = 40
    elif taux_couverture >= 80:
        score_couverture = 40 * (taux_couverture - 80) / 20
    else:
        score_couverture = 0

    # Score CO₂ : référence = tout au charbon
    co2_reference = energie_demandee * 820 * 1000 / 1e6  # tCO₂
    if co2_total <= 0:
        score_co2 = 30
    else:
        ratio_co2 = co2_total / co2_reference
        score_co2 = max(0, 30 * (1 - ratio_co2))

    # Score coût : basé sur le LCOE
    # Référence = 80 €/MWh (coût moyen scénario 100% gaz avec taxe carbone)
    # Meilleur LCOE possible ~ 20 €/MWh (nucléaire + hydro)
    lcoe_reference = 80.0  # €/MWh
    if lcoe <= 0:
        score_cout = 30
    else:
        score_cout = max(0, 30 * (1 - lcoe / lcoe_reference))

    # Malus surplus : pénalité si surproduction
    # Ratio surplus = énergie gaspillée / énergie demandée
    # 0% surplus → malus 0 | 20% surplus → malus -10 | 50%+ surplus → malus -25
    energie_surplus = df_production["surplus"].sum()
    ratio_surplus = energie_surplus / energie_demandee if energie_demandee > 0 else 0
    malus_surplus = min(25, ratio_surplus * 50)  # max -25 pts

    score_total = round(max(0, score_couverture + score_co2 + score_cout - malus_surplus), 1)

    return {
        "cout_construction": round(cout_construction, 1),
        "cout_production": round(cout_production, 1),
        "cout_total": round(cout_total, 1),
        "lcoe": round(lcoe, 1),
        "co2_total": round(co2_total, 1),
        "taux_couverture": round(taux_couverture, 1),
        "energie_demandee": round(energie_demandee, 1),
        "energie_produite": round(df_production["production_totale"].sum(), 1),
        "energie_deficit": round(energie_deficit, 1),
        "energie_surplus": round(energie_surplus, 1),
        "ratio_surplus": round(ratio_surplus * 100, 1),
        "heures_deficit": int(heures_deficit),
        "heures_surplus": int(heures_surplus),
        "score_couverture": round(score_couverture, 1),
        "score_co2": round(score_co2, 1),
        "score_cout": round(score_cout, 1),
        "malus_surplus": round(malus_surplus, 1),
        "score_total": round(score_total, 1),
        "details_par_source": details,
    }


def get_puissance_installee(choix_joueur: dict) -> dict:
    """Retourne la puissance installée par source."""
    result = {}
    for source, nb in choix_joueur.items():
        if nb > 0:
            info = MOYENS_PRODUCTION[source]
            result[source] = {
                "nom": info["nom"],
                "puissance_unitaire": info["puissance"],
                "nb_unites": nb,
                "puissance_totale": nb * info["puissance"],
            }
    return result
