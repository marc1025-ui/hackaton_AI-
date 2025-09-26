from hutchinson_analyzer import HutchinsonRegulatoryAnalyzer
from db import db
from datetime import datetime, timedelta
import time
import json

class HutchinsonMonitoringSystem:
    """
    Système de monitoring en temps réel pour les changements réglementaires
    Surveille les modifications et met à jour automatiquement les analyses
    """

    def __init__(self):
        self.analyzer = HutchinsonRegulatoryAnalyzer()
        self.regulations = db["regulations"]
        self.risk_analysis = db["risk_analysis"]
        self.alerts = db["alerts"]  # Nouvelle collection pour les alertes

    def monitor_regulation_changes(self, check_interval_minutes=5):
        """
        Surveillance continue des changements réglementaires

        Args:
            check_interval_minutes (int): Intervalle de vérification en minutes
        """
        print(f"🔄 Démarrage du monitoring (vérification toutes les {check_interval_minutes} minutes)")

        while True:
            try:
                print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Vérification des changements...")

                # Détecter les nouvelles réglementations
                new_regulations = self._detect_new_regulations()

                # Détecter les réglementations modifiées
                modified_regulations = self._detect_modified_regulations()

                # Traiter les nouvelles réglementations
                if new_regulations:
                    self._process_new_regulations(new_regulations)

                # Traiter les réglementations modifiées
                if modified_regulations:
                    self._process_modified_regulations(modified_regulations)

                # Générer des alertes si nécessaire
                self._generate_alerts_if_needed()

                print("✅ Vérification terminée")

                # Attendre avant la prochaine vérification
                time.sleep(check_interval_minutes * 60)

            except KeyboardInterrupt:
                print("\n🛑 Arrêt du monitoring demandé")
                break
            except Exception as e:
                print(f"❌ Erreur dans le monitoring: {e}")
                time.sleep(30)  # Attendre 30s avant de reprendre

    def _detect_new_regulations(self):
        """Détecte les nouvelles réglementations ajoutées"""
        # Récupérer les réglementations sans analyse
        analyzed_ids = set([
            doc["regulation_info"]["id_loi"]
            for doc in self.risk_analysis.find({}, {"regulation_info.id_loi": 1})
        ])

        all_reg_ids = set([
            doc["id_loi"]
            for doc in self.regulations.find({}, {"id_loi": 1})
        ])

        new_ids = all_reg_ids - analyzed_ids

        if new_ids:
            new_regulations = list(self.regulations.find({"id_loi": {"$in": list(new_ids)}}))
            return new_regulations

        return []

    def _detect_modified_regulations(self):
        """Détecte les réglementations modifiées récemment"""
        # Rechercher les réglementations avec updated_at récent
        recent_time = datetime.now() - timedelta(minutes=10)

        modified = list(self.regulations.find({
            "updated_at": {"$gte": recent_time}
        }))

        return modified

    def _process_new_regulations(self, new_regulations):
        """Traite les nouvelles réglementations"""
        print(f"🆕 {len(new_regulations)} nouvelles réglementations détectées")

        for reg in new_regulations:
            try:
                analysis = self.analyzer.analyze_regulation_impact_on_hutchinson(reg["id_loi"])
                score = analysis["hutchinson_impact"]["score_risque"]
                niveau = analysis["hutchinson_impact"]["niveau_impact"]

                print(f"  ✅ {reg['id_loi']}: {score}/100 ({niveau})")

                # Créer une alerte si le risque est élevé
                if score >= 50:
                    self._create_alert("NEW_HIGH_RISK", analysis)

            except Exception as e:
                print(f"  ❌ Erreur pour {reg['id_loi']}: {e}")

    def _process_modified_regulations(self, modified_regulations):
        """Traite les réglementations modifiées"""
        print(f"🔧 {len(modified_regulations)} réglementations modifiées détectées")

        for reg in modified_regulations:
            try:
                # Récupérer l'ancienne analyse
                old_analysis = self.risk_analysis.find_one({
                    "regulation_info.id_loi": reg["id_loi"]
                })

                # Créer la nouvelle analyse
                new_analysis = self.analyzer.analyze_regulation_impact_on_hutchinson(reg["id_loi"])

                old_score = old_analysis["hutchinson_impact"]["score_risque"] if old_analysis else 0
                new_score = new_analysis["hutchinson_impact"]["score_risque"]

                score_change = new_score - old_score

                print(f"  🔄 {reg['id_loi']}: {old_score} → {new_score} (Δ{score_change:+d})")

                # Créer une alerte si le changement est significatif
                if abs(score_change) >= 10:
                    self._create_alert("SCORE_CHANGE", new_analysis, {
                        "old_score": old_score,
                        "new_score": new_score,
                        "change": score_change
                    })

            except Exception as e:
                print(f"  ❌ Erreur pour {reg['id_loi']}: {e}")

    def _create_alert(self, alert_type, analysis, extra_data=None):
        """Crée une alerte dans la base de données"""

        alert = {
            "type": alert_type,
            "regulation_id": analysis["regulation_info"]["id_loi"],
            "regulation_name": analysis["regulation_info"]["nom_loi"],
            "current_score": analysis["hutchinson_impact"]["score_risque"],
            "impact_level": analysis["hutchinson_impact"]["niveau_impact"],
            "created_at": datetime.now(),
            "status": "UNREAD",
            "priority": self._determine_alert_priority(analysis["hutchinson_impact"]["score_risque"])
        }

        if extra_data:
            alert.update(extra_data)

        # Ajouter des détails spécifiques selon le type d'alerte
        if alert_type == "NEW_HIGH_RISK":
            alert["message"] = f"Nouvelle réglementation à haut risque détectée: {analysis['regulation_info']['nom_loi']}"
        elif alert_type == "SCORE_CHANGE":
            alert["message"] = f"Changement significatif de score pour {analysis['regulation_info']['nom_loi']}: {extra_data['old_score']} → {extra_data['new_score']}"

        self.alerts.insert_one(alert)
        print(f"  🚨 ALERTE créée: {alert['message']}")

    def _determine_alert_priority(self, score):
        """Détermine la priorité de l'alerte basée sur le score"""
        if score >= 70:
            return "CRITIQUE"
        elif score >= 50:
            return "HAUTE"
        elif score >= 30:
            return "MOYENNE"
        else:
            return "BASSE"

    def _generate_alerts_if_needed(self):
        """Génère des alertes basées sur des règles métier"""
        # Exemple: Alerte si plus de 3 réglementations critiques
        critical_count = self.risk_analysis.count_documents({
            "hutchinson_impact.niveau_impact": "CRITIQUE"
        })

        if critical_count >= 3:
            # Vérifier si cette alerte n'existe pas déjà
            existing_alert = self.alerts.find_one({
                "type": "MULTIPLE_CRITICAL",
                "created_at": {"$gte": datetime.now() - timedelta(days=1)}
            })

            if not existing_alert:
                alert = {
                    "type": "MULTIPLE_CRITICAL",
                    "message": f"Attention: {critical_count} réglementations critiques détectées",
                    "count": critical_count,
                    "created_at": datetime.now(),
                    "status": "UNREAD",
                    "priority": "CRITIQUE"
                }
                self.alerts.insert_one(alert)
                print(f"  🚨 ALERTE SYSTÈME: {alert['message']}")

    def get_unread_alerts(self):
        """Récupère toutes les alertes non lues"""
        return list(self.alerts.find({"status": "UNREAD"}).sort("created_at", -1))

    def mark_alert_as_read(self, alert_id):
        """Marque une alerte comme lue"""
        self.alerts.update_one(
            {"_id": alert_id},
            {"$set": {"status": "READ", "read_at": datetime.now()}}
        )

    def get_dashboard_data(self):
        """Récupère les données pour le dashboard Streamlit"""

        # Statistiques générales
        total_regulations = self.regulations.count_documents({})
        analyzed_regulations = self.risk_analysis.count_documents({})

        # Répartition par niveau de risque
        risk_distribution = {}
        for level in ["CRITIQUE", "ELEVE", "MOYEN", "FAIBLE"]:
            count = self.risk_analysis.count_documents({
                "hutchinson_impact.niveau_impact": level
            })
            risk_distribution[level] = count

        # Top 5 des réglementations les plus risquées
        top_risks = list(self.risk_analysis.find({}).sort(
            "hutchinson_impact.score_risque", -1
        ).limit(5))

        # Alertes récentes
        recent_alerts = list(self.alerts.find({}).sort("created_at", -1).limit(10))

        # Secteurs les plus impactés
        sector_impacts = {}
        for analysis in self.risk_analysis.find({}):
            for sector_impact in analysis["hutchinson_impact"]["secteurs_impactes"]:
                sector = sector_impact["secteur"]
                sector_impacts[sector] = sector_impacts.get(sector, 0) + 1

        return {
            "total_regulations": total_regulations,
            "analyzed_regulations": analyzed_regulations,
            "risk_distribution": risk_distribution,
            "top_risks": top_risks,
            "recent_alerts": recent_alerts,
            "sector_impacts": sector_impacts,
            "last_update": datetime.now()
        }

    def simulate_regulation_change(self, regulation_id):
        """Simule un changement de réglementation pour tester les alertes"""
        print(f"🧪 Simulation d'un changement pour {regulation_id}")

        # Marquer la réglementation comme modifiée
        self.regulations.update_one(
            {"id_loi": regulation_id},
            {"$set": {"updated_at": datetime.now()}}
        )

        print("✅ Réglementation marquée comme modifiée")
        print("💡 Le système de monitoring détectera ce changement au prochain cycle")

def demo_monitoring_system():
    """Démonstration du système de monitoring"""

    print("🔄 SYSTÈME DE MONITORING HUTCHINSON")
    print("=" * 50)

    monitor = HutchinsonMonitoringSystem()

    # Simuler un changement pour démonstration
    print("🧪 Simulation d'un changement réglementaire...")
    monitor.simulate_regulation_change("32025L0001")

    # Vérification manuelle des changements
    print("\n🔍 Vérification manuelle des changements...")
    new_regs = monitor._detect_new_regulations()
    modified_regs = monitor._detect_modified_regulations()

    print(f"Nouvelles réglementations: {len(new_regs)}")
    print(f"Réglementations modifiées: {len(modified_regs)}")

    if modified_regs:
        monitor._process_modified_regulations(modified_regs)

    # Afficher les alertes
    print("\n🚨 ALERTES:")
    alerts = monitor.get_unread_alerts()
    if alerts:
        for alert in alerts:
            print(f"  • [{alert['priority']}] {alert['message']}")
    else:
        print("  ✅ Aucune alerte")

    # Données du dashboard
    print("\n📊 DONNÉES DASHBOARD:")
    dashboard_data = monitor.get_dashboard_data()
    print(f"  Total réglementations: {dashboard_data['total_regulations']}")
    print(f"  Analysées: {dashboard_data['analyzed_regulations']}")
    print(f"  Répartition risques: {dashboard_data['risk_distribution']}")
    print(f"  Secteurs impactés: {dashboard_data['sector_impacts']}")

    print("\n💡 Pour démarrer le monitoring en continu:")
    print("  monitor.monitor_regulation_changes(check_interval_minutes=5)")

if __name__ == "__main__":
    demo_monitoring_system()
