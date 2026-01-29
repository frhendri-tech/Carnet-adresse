from flask import Flask, render_template, request, redirect, url_for, flash, session
from address_book import AddressBook
from authentification import Authentification
from communication import Communication
from services import ServicesPolyclinique
from rendez_vous import RendezVous
from functools import wraps
from datetime import datetime, timedelta, date

app = Flask(__name__)
app.secret_key = 'polyclinique_secret_key_super_securisee_2026'

# Initialiser les modules
carnet = AddressBook("polyclinique.db")
auth = Authentification("polyclinique.db")
services = ServicesPolyclinique("polyclinique.db")
rdv_manager = RendezVous("polyclinique.db")

# Configuration Email
EMAIL_EXPEDITEUR = None
MOT_DE_PASSE_EMAIL = None
comm = Communication(EMAIL_EXPEDITEUR, MOT_DE_PASSE_EMAIL)

# Décorateur pour protéger les routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_info' not in session:
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Décorateur pour super-admin uniquement
def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_info' not in session:
            flash('Veuillez vous connecter.', 'warning')
            return redirect(url_for('login'))
        
        if not auth.est_super_admin(session['admin_info']):
            flash('Accès refusé. Réservé au directeur.', 'danger')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function

# ==================== AUTHENTIFICATION ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        admin_info = auth.verifier_connexion(username, password)
        
        if admin_info:
            session['admin_info'] = admin_info
            role_fr = "Directeur" if auth.est_super_admin(admin_info) else "Responsable"
            flash(f'Bienvenue {role_fr} {username} ! 🎉', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Identifiants incorrects !', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    username = session.get('admin_info', {}).get('nom_utilisateur', 'Utilisateur')
    session.pop('admin_info', None)
    flash(f'Au revoir {username} ! 👋', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['POST'])
def register():
    if 'admin_info' not in session or not auth.est_super_admin(session['admin_info']):
        flash('Accès refusé', 'danger')
        return redirect(url_for('login'))
    
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    role = request.form.get('role', 'admin')
    service_id = request.form.get('service_id')
    
    if not username or not password:
        flash('Tous les champs sont obligatoires !', 'danger')
        return redirect(url_for('gestion_admins'))
    
    if password != confirm_password:
        flash('Les mots de passe ne correspondent pas !', 'danger')
        return redirect(url_for('gestion_admins'))
    
    if auth.creer_admin(username, password, role, service_id):
        flash(f'Compte "{username}" créé avec succès !', 'success')
    else:
        flash('Erreur lors de la création du compte.', 'danger')
    
    return redirect(url_for('gestion_admins'))

# ==================== DASHBOARD ====================

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal selon le rôle"""
    admin_info = session['admin_info']
    
    if auth.est_super_admin(admin_info):
        # Super-admin voit tout
        services_list = services.obtenir_services_actifs()
        total_rdv = sum([rdv_manager.obtenir_statistiques_service(s['id'])['total'] for s in services_list])
    else:
        # Admin voit son service
        service_id = admin_info.get('service_id')
        if service_id:
            service = services.obtenir_service_par_id(service_id)
            services_list = [service] if service else []
            total_rdv = rdv_manager.obtenir_statistiques_service(service_id)['total'] if service else 0
        else:
            services_list = []
            total_rdv = 0
    
    # RDV du jour
    today = date.today().strftime('%Y-%m-%d')
    rdv_aujourd_hui = rdv_manager.obtenir_rendez_vous_par_date(today)
    
    return render_template('dashboard.html', 
                         admin_info=admin_info,
                         services=services_list,
                         total_rdv=total_rdv,
                         rdv_aujourd_hui=rdv_aujourd_hui)

# ==================== GESTION DES CONTACTS ====================

@app.route('/contacts')
@login_required
def index():
    contacts_tries = sorted(carnet.contacts, key=lambda c: (c.categorie, c.nom.lower(), c.prenom.lower()))
    return render_template('index.html', contacts=contacts_tries, admin_info=session['admin_info'])

@app.route('/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter():
    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        email = request.form.get('email', '').strip()
        telephone = request.form.get('telephone', '').strip()
        adresse = request.form.get('adresse', '').strip()
        fonction = request.form.get('fonction', '').strip()
        entreprise = request.form.get('entreprise', '').strip()
        categorie = request.form.get('categorie', 'Personnel').strip()
        
        if not (nom and prenom and email and telephone):
            flash('Les champs obligatoires doivent être remplis !', 'danger')
            return redirect(url_for('ajouter'))
        
        if carnet.ajouter_contact(nom, prenom, email, telephone, adresse, fonction, entreprise, categorie):
            flash(f'Contact "{nom.upper()} {prenom.upper()}" ajouté ! ✓', 'success')
            return redirect(url_for('index'))
        else:
            flash('Erreur lors de l\'ajout.', 'danger')
    
    return render_template('ajouter.html', admin_info=session['admin_info'])

@app.route('/modifier/<nom>/<prenom>', methods=['GET', 'POST'])
@login_required
def modifier(nom, prenom):
    contact = carnet.rechercher_contact(nom, prenom)
    
    if not contact:
        flash('Contact introuvable !', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        nouveau_nom = request.form.get('nom', '').strip()
        nouveau_prenom = request.form.get('prenom', '').strip()
        nouveau_email = request.form.get('email', '').strip()
        nouveau_telephone = request.form.get('telephone', '').strip()
        nouvelle_adresse = request.form.get('adresse', '').strip()
        nouvelle_fonction = request.form.get('fonction', '').strip()
        nouvelle_entreprise = request.form.get('entreprise', '').strip()
        nouvelle_categorie = request.form.get('categorie', '').strip()
        
        if carnet.modifier_contact(
            nom, prenom,
            nouveau_nom if nouveau_nom != contact.nom else None,
            nouveau_prenom if nouveau_prenom != contact.prenom else None,
            nouveau_email if nouveau_email != contact.email else None,
            nouveau_telephone if nouveau_telephone != contact.telephone else None,
            nouvelle_adresse if nouvelle_adresse != contact.adresse else None,
            nouvelle_fonction if nouvelle_fonction != contact.fonction else None,
            nouvelle_entreprise if nouvelle_entreprise != contact.entreprise else None,
            nouvelle_categorie if nouvelle_categorie != contact.categorie else None
        ):
            flash(f'Contact modifié ! ✓', 'success')
            return redirect(url_for('index'))
        else:
            flash('Erreur lors de la modification.', 'danger')
    
    return render_template('modifier.html', contact=contact, admin_info=session['admin_info'])

@app.route('/supprimer/<nom>/<prenom>')
@login_required
def supprimer(nom, prenom):
    if carnet.supprimer_contact(nom, prenom):
        flash(f'Contact supprimé ! 🗑️', 'success')
    else:
        flash('Erreur lors de la suppression.', 'danger')
    
    return redirect(url_for('index'))

# ==================== AGENDA & RENDEZ-VOUS ====================

@app.route('/agenda')
@login_required
def agenda():
    """Page principale de l'agenda"""
    admin_info = session['admin_info']
    
    # Sélectionner les services accessibles
    if auth.est_super_admin(admin_info):
        services_list = services.obtenir_services_actifs()
    else:
        service_id = admin_info.get('service_id')
        if service_id:
            service = services.obtenir_service_par_id(service_id)
            services_list = [service] if service else []
        else:
            services_list = []
    
    # Date sélectionnée (par défaut aujourd'hui)
    date_str = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    service_id = request.args.get('service_id')
    
    creneaux = []
    service_selectionne = None
    
    if service_id:
        service_selectionne = services.obtenir_service_par_id(int(service_id))
        if service_selectionne:
            creneaux = rdv_manager.obtenir_creneaux_disponibles(
                int(service_id),
                date_str,
                service_selectionne['horaire_debut'],
                service_selectionne['horaire_fin']
            )
    
    return render_template('agenda.html',
                         admin_info=admin_info,
                         services=services_list,
                         service_selectionne=service_selectionne,
                         date_selectionnee=date_str,
                         creneaux=creneaux)

@app.route('/prendre_rdv', methods=['GET', 'POST'])
@login_required
def prendre_rdv():
    """Prendre un rendez-vous"""
    if request.method == 'POST':
        service_id = request.form.get('service_id')
        date_rdv = request.form.get('date_rdv')
        heure_debut = request.form.get('heure_debut')
        heure_fin = request.form.get('heure_fin')
        patient_nom = request.form.get('patient_nom', '').strip()
        patient_prenom = request.form.get('patient_prenom', '').strip()
        patient_telephone = request.form.get('patient_telephone', '').strip()
        patient_email = request.form.get('patient_email', '').strip()
        motif = request.form.get('motif', '').strip()
        
        if not (service_id and date_rdv and heure_debut and patient_nom and patient_prenom and patient_telephone):
            flash('Tous les champs obligatoires doivent être remplis !', 'danger')
            return redirect(url_for('agenda'))
        
        success, message, rdv_id = rdv_manager.prendre_rendez_vous(
            int(service_id),
            patient_nom, patient_prenom, patient_telephone,
            date_rdv, heure_debut, heure_fin,
            motif, patient_email,
            session['admin_info']['id']
        )
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'danger')
        
        return redirect(url_for('agenda', service_id=service_id, date=date_rdv))
    
    # GET
    service_id = request.args.get('service_id')
    date_rdv = request.args.get('date')
    heure_debut = request.args.get('heure_debut')
    heure_fin = request.args.get('heure_fin')
    
    service = services.obtenir_service_par_id(int(service_id)) if service_id else None
    
    return render_template('prendre_rdv.html',
                         admin_info=session['admin_info'],
                         service=service,
                         date_rdv=date_rdv,
                         heure_debut=heure_debut,
                         heure_fin=heure_fin)

@app.route('/mes_rdv')
@login_required
def mes_rdv():
    """Liste des rendez-vous"""
    admin_info = session['admin_info']
    
    if auth.est_super_admin(admin_info):
        # Super-admin voit tous les RDV
        today = date.today().strftime('%Y-%m-%d')
        rdv_list = rdv_manager.obtenir_rendez_vous_par_date(today)
    else:
        # Admin voit les RDV de son service
        service_id = admin_info.get('service_id')
        if service_id:
            rdv_list = rdv_manager.obtenir_rendez_vous_par_service(service_id)
        else:
            rdv_list = []
    
    return render_template('mes_rdv.html',
                         admin_info=admin_info,
                         rendez_vous=rdv_list)

@app.route('/annuler_rdv/<int:rdv_id>')
@login_required
def annuler_rdv(rdv_id):
    """Annuler un rendez-vous"""
    if rdv_manager.annuler_rendez_vous(rdv_id):
        flash('Rendez-vous annulé avec succès !', 'success')
    else:
        flash('Erreur lors de l\'annulation.', 'danger')
    
    return redirect(url_for('mes_rdv'))

# ==================== GESTION DES SERVICES (Super-Admin) ====================

@app.route('/gestion_services')
@super_admin_required
def gestion_services():
    """Gestion des services (Super-admin uniquement)"""
    services_list = services.services
    admins_list = auth.lister_admins()
    
    return render_template('gestion_services.html',
                         admin_info=session['admin_info'],
                         services=services_list,
                         admins=admins_list)

@app.route('/gestion_admins')
@super_admin_required
def gestion_admins():
    """Gestion des administrateurs"""
    admins_list = auth.lister_admins()
    services_list = services.obtenir_services_actifs()
    
    return render_template('gestion_admins.html',
                         admin_info=session['admin_info'],
                         admins=admins_list,
                         services=services_list)

# ==================== COMMUNICATION ====================

@app.route('/envoyer-email/<nom>/<prenom>', methods=['GET', 'POST'])
@login_required
def envoyer_email(nom, prenom):
    contact = carnet.rechercher_contact(nom, prenom)
    
    if not contact:
        flash('Contact introuvable !', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        sujet = request.form.get('sujet', '').strip()
        message = request.form.get('message', '').strip()
        
        if not sujet or not message:
            flash('Le sujet et le message sont obligatoires !', 'danger')
            return render_template('envoyer_email.html', contact=contact, admin_info=session['admin_info'])
        
        success, msg = comm.envoyer_email(contact.email, sujet, message, html=False)
        
        if success:
            flash(msg, 'success')
            return redirect(url_for('index'))
        else:
            flash(msg, 'danger')
    
    return render_template('envoyer_email.html', contact=contact, admin_info=session['admin_info'])

# ==================== LANCEMENT ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)