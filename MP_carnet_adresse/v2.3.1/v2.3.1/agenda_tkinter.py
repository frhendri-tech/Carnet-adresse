import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime, date
from rendez_vous import RendezVous
from services import ServicesPolyclinique
from authentification import Authentification

class AgendaPolyclinique:
    """Interface graphique Tkinter pour l'agenda des rendez-vous"""
    
    def __init__(self, root, admin_info):
        """
        Initialise l'interface de l'agenda
        
        Args:
            root: Fenêtre principale Tkinter
            admin_info (dict): Informations de l'admin connecté
        """
        self.root = root
        self.admin_info = admin_info
        self.root.title(f"📅 Agenda Polyclinique - {admin_info['nom_utilisateur']}")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        # Initialiser les modules
        self.rdv = RendezVous()
        self.services = ServicesPolyclinique()
        self.auth = Authentification()
        
        # Variables
        self.date_selectionnee = date.today()
        self.service_selectionne = None
        
        # Créer l'interface
        self.creer_interface()
        
        # Charger les données initiales
        self.charger_services()
    
    def creer_interface(self):
        """Crée tous les éléments de l'interface"""
        
        # ==================== HEADER ====================
        frame_header = tk.Frame(self.root, bg="#2c3e50", height=80)
        frame_header.pack(fill=tk.X, padx=10, pady=10)
        frame_header.pack_propagate(False)
        
        # Titre
        role_texte = "DIRECTEUR" if self.auth.est_super_admin(self.admin_info) else "RESPONSABLE"
        tk.Label(
            frame_header,
            text=f"📅 AGENDA POLYCLINIQUE\n{role_texte} : {self.admin_info['nom_utilisateur'].upper()}",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(pady=15)
        
        # ==================== BODY ====================
        frame_body = tk.Frame(self.root, bg="#ecf0f1")
        frame_body.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Layout en 2 colonnes
        # Colonne gauche : Calendrier + Sélection service
        frame_gauche = tk.Frame(frame_body, bg="#ecf0f1", width=400)
        frame_gauche.pack(side=tk.LEFT, fill=tk.BOTH, padx=10)
        
        # Colonne droite : Créneaux disponibles
        frame_droite = tk.Frame(frame_body, bg="#ecf0f1")
        frame_droite.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        # === COLONNE GAUCHE ===
        
        # Sélection du service
        tk.Label(
            frame_gauche,
            text="🏥 Sélectionnez un service",
            font=("Arial", 12, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(pady=(10, 5))
        
        self.combo_services = ttk.Combobox(
            frame_gauche,
            font=("Arial", 11),
            state="readonly",
            width=35
        )
        self.combo_services.pack(pady=5)
        self.combo_services.bind('<<ComboboxSelected>>', self.on_service_change)
        
        # Calendrier
        tk.Label(
            frame_gauche,
            text="📆 Sélectionnez une date",
            font=("Arial", 12, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(pady=(20, 5))
        
        self.calendrier = Calendar(
            frame_gauche,
            selectmode='day',
            year=date.today().year,
            month=date.today().month,
            day=date.today().day,
            date_pattern='yyyy-mm-dd',
            background='#2c3e50',
            foreground='white',
            bordercolor='#2c3e50',
            headersbackground='#34495e',
            normalbackground='white',
            normalforeground='black',
            weekendbackground='#ecf0f1',
            weekendforeground='black',
            selectbackground='#3498db',
            selectforeground='white'
        )
        self.calendrier.pack(pady=10, padx=10)
        self.calendrier.bind("<<CalendarSelected>>", self.on_date_change)
        
        # Bouton actualiser
        tk.Button(
            frame_gauche,
            text="🔄 Actualiser",
            command=self.actualiser_creneaux,
            bg="#3498db",
            fg="white",
            font=("Arial", 11, "bold"),
            width=20,
            height=2
        ).pack(pady=10)
        
        # Statistiques
        self.frame_stats = tk.LabelFrame(
            frame_gauche,
            text="📊 Statistiques",
            font=("Arial", 11, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        self.frame_stats.pack(pady=10, padx=10, fill=tk.X)
        
        self.label_stats = tk.Label(
            self.frame_stats,
            text="Sélectionnez un service",
            font=("Arial", 10),
            bg="#ecf0f1",
            fg="#7f8c8d"
        )
        self.label_stats.pack(pady=10)
        
        # === COLONNE DROITE ===
        
        # Titre créneaux
        tk.Label(
            frame_droite,
            text="⏰ Créneaux disponibles (30 minutes)",
            font=("Arial", 14, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(pady=10)
        
        # Info date sélectionnée
        self.label_date_info = tk.Label(
            frame_droite,
            text=f"📅 {self.date_selectionnee.strftime('%d/%m/%Y')}",
            font=("Arial", 12),
            bg="#ecf0f1",
            fg="#34495e"
        )
        self.label_date_info.pack(pady=5)
        
        # Frame scrollable pour les créneaux
        canvas = tk.Canvas(frame_droite, bg="#ecf0f1", highlightthickness=0)
        scrollbar = tk.Scrollbar(frame_droite, orient="vertical", command=canvas.yview)
        self.frame_creneaux = tk.Frame(canvas, bg="#ecf0f1")
        
        self.frame_creneaux.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.frame_creneaux, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ==================== FOOTER ====================
        frame_footer = tk.Frame(self.root, bg="#34495e", height=50)
        frame_footer.pack(fill=tk.X, padx=10, pady=10)
        frame_footer.pack_propagate(False)
        
        tk.Label(
            frame_footer,
            text="© 2026 Polyclinique - Système de gestion des rendez-vous",
            font=("Arial", 10),
            bg="#34495e",
            fg="white"
        ).pack(pady=12)
    
    def charger_services(self):
        """Charge les services dans le combobox"""
        if self.auth.est_super_admin(self.admin_info):
            # Super-admin voit tous les services
            services = self.services.obtenir_services_actifs()
        else:
            # Admin voit seulement son service
            service_id = self.admin_info.get('service_id')
            if service_id:
                service = self.services.obtenir_service_par_id(service_id)
                services = [service] if service else []
            else:
                services = []
        
        self.combo_services['values'] = [s['nom'] for s in services]
        self.services_dict = {s['nom']: s for s in services}
        
        if services:
            self.combo_services.current(0)
            self.on_service_change(None)
    
    def on_service_change(self, event):
        """Appelé quand le service change"""
        nom_service = self.combo_services.get()
        if nom_service in self.services_dict:
            self.service_selectionne = self.services_dict[nom_service]
            self.actualiser_creneaux()
            self.actualiser_statistiques()
    
    def on_date_change(self, event):
        """Appelé quand la date change"""
        date_str = self.calendrier.get_date()
        self.date_selectionnee = datetime.strptime(date_str, '%Y-%m-%d').date()
        self.label_date_info.config(text=f"📅 {self.date_selectionnee.strftime('%d/%m/%Y')}")
        self.actualiser_creneaux()
    
    def actualiser_creneaux(self):
        """Actualise l'affichage des créneaux"""
        # Nettoyer les créneaux existants
        for widget in self.frame_creneaux.winfo_children():
            widget.destroy()
        
        if not self.service_selectionne:
            tk.Label(
                self.frame_creneaux,
                text="⚠️ Veuillez sélectionner un service",
                font=("Arial", 12),
                bg="#ecf0f1",
                fg="#e74c3c"
            ).pack(pady=50)
            return
        
        # Obtenir les créneaux
        creneaux = self.rdv.obtenir_creneaux_disponibles(
            self.service_selectionne['id'],
            self.date_selectionnee.strftime('%Y-%m-%d'),
            self.service_selectionne['horaire_debut'],
            self.service_selectionne['horaire_fin']
        )
        
        # Afficher les créneaux
        row = 0
        col = 0
        for heure_debut, heure_fin, disponible in creneaux:
            couleur = "#27ae60" if disponible else "#95a5a6"
            texte = f"{heure_debut} - {heure_fin}"
            etat = "normal" if disponible else "disabled"
            
            btn = tk.Button(
                self.frame_creneaux,
                text=texte,
                bg=couleur,
                fg="white",
                font=("Arial", 11, "bold"),
                width=15,
                height=2,
                state=etat,
                cursor="hand2" if disponible else "arrow",
                command=lambda h1=heure_debut, h2=heure_fin: self.prendre_rdv(h1, h2)
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            # Tooltip
            if not disponible:
                self.creer_tooltip(btn, "❌ Créneau déjà réservé")
            else:
                self.creer_tooltip(btn, "✅ Créneau disponible - Cliquez pour réserver")
            
            col += 1
            if col >= 3:  # 3 créneaux par ligne
                col = 0
                row += 1
    
    def creer_tooltip(self, widget, text):
        """Crée un tooltip pour un widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="#2c3e50", 
                           foreground="white", relief=tk.SOLID, borderwidth=1,
                           font=("Arial", 9))
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def prendre_rdv(self, heure_debut, heure_fin):
        """Ouvre le formulaire de prise de RDV"""
        dialog = tk.Toplevel(self.root)
        dialog.title("📝 Prendre un rendez-vous")
        dialog.geometry("500x450")
        dialog.configure(bg="#ecf0f1")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Titre
        tk.Label(
            dialog,
            text=f"Rendez-vous\n{self.service_selectionne['nom']}\n{self.date_selectionnee.strftime('%d/%m/%Y')} à {heure_debut}",
            font=("Arial", 12, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(pady=15)
        
        # Frame formulaire
        frame_form = tk.Frame(dialog, bg="#ecf0f1")
        frame_form.pack(pady=10, padx=30)
        
        # Champs
        tk.Label(frame_form, text="Nom du patient :", bg="#ecf0f1", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        entry_nom = tk.Entry(frame_form, font=("Arial", 10), width=30)
        entry_nom.grid(row=0, column=1, pady=5, padx=5)
        entry_nom.focus()
        
        tk.Label(frame_form, text="Prénom du patient :", bg="#ecf0f1", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        entry_prenom = tk.Entry(frame_form, font=("Arial", 10), width=30)
        entry_prenom.grid(row=1, column=1, pady=5, padx=5)
        
        tk.Label(frame_form, text="Téléphone :", bg="#ecf0f1", font=("Arial", 10)).grid(row=2, column=0, sticky="w", pady=5)
        entry_tel = tk.Entry(frame_form, font=("Arial", 10), width=30)
        entry_tel.grid(row=2, column=1, pady=5, padx=5)
        
        tk.Label(frame_form, text="Email (optionnel) :", bg="#ecf0f1", font=("Arial", 10)).grid(row=3, column=0, sticky="w", pady=5)
        entry_email = tk.Entry(frame_form, font=("Arial", 10), width=30)
        entry_email.grid(row=3, column=1, pady=5, padx=5)
        
        tk.Label(frame_form, text="Motif :", bg="#ecf0f1", font=("Arial", 10)).grid(row=4, column=0, sticky="w", pady=5)
        text_motif = tk.Text(frame_form, font=("Arial", 10), width=30, height=4)
        text_motif.grid(row=4, column=1, pady=5, padx=5)
        
        def valider():
            nom = entry_nom.get().strip()
            prenom = entry_prenom.get().strip()
            tel = entry_tel.get().strip()
            email = entry_email.get().strip()
            motif = text_motif.get("1.0", tk.END).strip()
            
            if not (nom and prenom and tel):
                messagebox.showerror("Erreur", "Les champs Nom, Prénom et Téléphone sont obligatoires !")
                return
            
            # Validation téléphone (10 chiffres)
            chiffres = ''.join(filter(str.isdigit, tel))
            if len(chiffres) != 10:
                messagebox.showerror("Erreur", f"Le téléphone doit contenir 10 chiffres (Trouvé: {len(chiffres)})")
                return
            
            success, message, rdv_id = self.rdv.prendre_rendez_vous(
                self.service_selectionne['id'],
                nom, prenom, tel,
                self.date_selectionnee.strftime('%Y-%m-%d'),
                heure_debut, heure_fin,
                motif, email,
                self.admin_info['id']
            )
            
            if success:
                messagebox.showinfo("Succès", message)
                dialog.destroy()
                self.actualiser_creneaux()
                self.actualiser_statistiques()
            else:
                messagebox.showerror("Erreur", message)
        
        # Boutons
        frame_btn = tk.Frame(dialog, bg="#ecf0f1")
        frame_btn.pack(pady=20)
        
        tk.Button(
            frame_btn,
            text="✅ Confirmer",
            command=valider,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            width=15
        ).grid(row=0, column=0, padx=5)
        
        tk.Button(
            frame_btn,
            text="❌ Annuler",
            command=dialog.destroy,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11, "bold"),
            width=15
        ).grid(row=0, column=1, padx=5)
    
    def actualiser_statistiques(self):
        """Actualise les statistiques du service"""
        if not self.service_selectionne:
            return
        
        stats = self.rdv.obtenir_statistiques_service(self.service_selectionne['id'])
        
        texte = f"📊 Statistiques - {self.service_selectionne['nom']}\n\n"
        texte += f"Total RDV : {stats['total']}\n"
        texte += f"Confirmés : {stats['confirmes']} ✅\n"
        texte += f"Annulés : {stats['annules']} ❌"
        
        self.label_stats.config(text=texte)


def main():
    """Fonction principale de test"""
    # Créer un admin de test
    auth = Authentification()
    
    # Simuler une connexion
    admin_info = {
        'id': 1,
        'nom_utilisateur': 'directeur',
        'role': 'super_admin',
        'service_id': None
    }
    
    root = tk.Tk()
    app = AgendaPolyclinique(root, admin_info)
    root.mainloop()


if __name__ == "__main__":
    main()