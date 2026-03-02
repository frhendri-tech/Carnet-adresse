from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from address_book import AddressBook
from authentification import Authentification
from communication import Communication
from services import ServicesPolyclinique
from rendez_vous import RendezVous
from functools import wraps
from datetime import datetime, timedelta, date
import sqlite3
import json

app = Flask(__name__)
app.secret_key = 'polyclinique_secret_key_super_securisee_2026'

# Initialiser les modules
carnet = AddressBook(db_name="polyclinique.db")
auth = Authentification("polyclinique.db")
services = ServicesPolyclinique("polyclinique.db")
rdv_manager = RendezVous("polyclinique.db")

# Configuration Email - Chargée depuis la base de données
def get_email_config():
    """Récupère la configuration email depuis la base de données"""
    conn = sqlite3.connect("polyclinique.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)")
    cursor.execute("SELECT value FROM config WHERE key = 'email_expediteur'")
    email_row = cursor.fetchone()
    cursor.execute("SELECT value FROM config WHERE key = 'email_password'")
    pass_row = conn.cursor().execute("SELECT value FROM config WHERE key = 'email_password'")
    pass_row = pass_row.fetchone()
    conn.close()
    
    email = email_row[0] if email_row else None
    password = pass_row[0] if pass_row else None
    return email, password

def save_email_config(email, password):
    """Sauvegarde la configuration email dans la base de données"""
    conn = sqlite3.connect("polyclinique.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)")
    cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", 
                   ("email_expediteur", email))
    cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", 
                   ("email_password", password))
    conn.commit()
    conn.close()

# Initialiser la communication avec la config stockée
EMAIL_EXPEDITEUR, MOT_DE_PASSE_EMAIL = get_email_config()
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

# Décorateur pour admin et super-admin (pas pour user simple)
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_info' not in session:
            flash('Veuillez vous connecter.', 'warning')
            return redirect(url_for('login'))
        
        user_role = session['admin_info'].get('role')
        if user_role not in [auth.ROLE_SUPER_ADMIN, auth.ROLE_ADMIN]:
            flash('Accès refusé. Réservé aux administrateurs.', 'danger')
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
            role_fr = auth.get_role_display(admin_info['role'])
            flash(f'Bienvenue {role_fr} {username} ! 🎉', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Identifiants incorrects !', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Inscription pour les patients (vérification par email dans contacts)"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        email = request.form.get('email', '').strip()
        
        # Validations
        if not (username and password and email):
            flash('Tous les champs sont obligatoires !', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas !', 'danger')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères !', 'danger')
            return redirect(url_for('register'))
        
        # Créer le compte patient (vérifie automatiquement si l'email existe dans contacts)
        success, message = auth.creer_compte_patient(username, password, email)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    username = session.get('admin_info', {}).get('nom_utilisateur', 'Utilisateur')
    session.pop('admin_info', None)
    flash(f'Au revoir {username} ! 👋', 'info')
    return redirect(url_for('login'))

# ==================== GESTION DES COMPTES UTILISATEURS ====================

@app.route('/gestion_utilisateurs')
@admin_required
def gestion_utilisateurs():
    """Gestion des utilisateurs - accessible par Admin et Super-Admin"""
    admin_info = session['admin_info']
    
    # Récupérer les utilisateurs selon les permissions
    if auth.est_super_admin(admin_info):
        # Super-admin voit tout
        users_list = [u for u in auth.lister_admins() if u['role'] != auth.ROLE_SUPER_ADMIN]
        peut_creer_admin = True
    else:
        # Admin normal ne voit que les users
        users_list = [u for u in auth.lister_admins() if u['role'] == auth.ROLE_USER]
        peut_creer_admin = False
    
    services_list = services.obtenir_services_actifs()
    
    return render_template('gestion_utilisateurs.html',
                         admin_info=admin_info,
                         users=users_list,
                         services=services_list,
                         peut_creer_admin=peut_creer_admin,
                         auth=auth)

@app.route('/ajouter_utilisateur', methods=['POST'])
@admin_required
def ajouter_utilisateur():
    """Ajouter un utilisateur - Admin peut créer User, Super-Admin peut créer Admin et User"""
    createur_info = session['admin_info']
    
    nom_utilisateur = request.form.get('nom_utilisateur', '').strip()
    mot_de_passe = request.form.get('mot_de_passe', '').strip()
    role = request.form.get('role', auth.ROLE_USER)
    service_id = request.form.get('service_id') or None
    email = request.form.get('email', '').strip()
    
    if not nom_utilisateur or not mot_de_passe:
        flash('Le nom d\'utilisateur et le mot de passe sont obligatoires !', 'danger')
        return redirect(url_for('gestion_utilisateurs'))
    
    # Vérifier les permissions
    if not auth.peut_creer_compte(createur_info, role):
        flash('Vous n\'avez pas les permissions pour créer ce type de compte.', 'danger')
        return redirect(url_for('gestion_utilisateurs'))
    
    if auth.creer_admin(nom_utilisateur, mot_de_passe, role, service_id, email):
        flash(f'Utilisateur "{nom_utilisateur}" créé avec succès !', 'success')
    else:
        flash('Erreur lors de la création de l\'utilisateur.', 'danger')
    
    return redirect(url_for('gestion_utilisateurs'))

@app.route('/modifier_utilisateur/<int:id>', methods=['POST'])
@admin_required
def modifier_utilisateur(id):
    """Modifier un utilisateur"""
    createur_info = session['admin_info']
    user_cible = auth.obtenir_admin_par_id(id)
    
    if not user_cible:
        flash('Utilisateur introuvable.', 'danger')
        return redirect(url_for('gestion_utilisateurs'))
    
    # Vérifier les permissions
    if auth.est_admin(createur_info):
        # Un admin ne peut modifier que les users
        if user_cible['role'] != auth.ROLE_USER:
            flash('Vous ne pouvez modifier que les comptes utilisateurs.', 'danger')
            return redirect(url_for('gestion_utilisateurs'))
    
    role = request.form.get('role')
    service_id = request.form.get('service_id') or None
    email = request.form.get('email', '').strip()
    nouveau_mdp = request.form.get('nouveau_mdp', '').strip()
    
    # Un admin ne peut pas changer le rôle vers admin
    if auth.est_admin(createur_info) and role == auth.ROLE_ADMIN:
        flash('Vous ne pouvez pas attribuer le rôle d\'administrateur.', 'danger')
        return redirect(url_for('gestion_utilisateurs'))
    
    if auth.modifier_admin(id, role=role, service_id=service_id, email=email, 
                           nouveau_mdp=nouveau_mdp if nouveau_mdp else None):
        flash('Utilisateur modifié avec succès !', 'success')
    else:
        flash('Erreur lors de la modification.', 'danger')
    
    return redirect(url_for('gestion_utilisateurs'))

@app.route('/supprimer_utilisateur/<int:id>')
@admin_required
def supprimer_utilisateur(id):
    """Supprimer un utilisateur"""
    createur_info = session['admin_info']
    user_cible = auth.obtenir_admin_par_id(id)
    
    if not user_cible:
        flash('Utilisateur introuvable.', 'danger')
        return redirect(url_for('gestion_utilisateurs'))
    
    # Vérifier les permissions
    if auth.est_admin(createur_info):
        # Un admin ne peut supprimer que les users
        if user_cible['role'] != auth.ROLE_USER:
            flash('Vous ne pouvez supprimer que les comptes utilisateurs.', 'danger')
            return redirect(url_for('gestion_utilisateurs'))
    
    # Empêcher la suppression de soi-même
    if id == createur_info['id']:
        flash('Vous ne pouvez pas supprimer votre propre compte.', 'danger')
        return redirect(url_for('gestion_utilisateurs'))
    
    if auth.supprimer_admin(id):
        flash('Utilisateur supprimé avec succès !', 'success')
    else:
        flash('Erreur lors de la suppression.', 'danger')
    
    return redirect(url_for('gestion_utilisateurs'))

# ==================== GESTION DES ADMINS (Super-Admin uniquement) ====================

@app.route('/gestion_admins')
@super_admin_required
def gestion_admins():
    """Gestion des administrateurs - Super-admin uniquement"""
    admins_list = [a for a in auth.lister_admins() if a['role'] in [auth.ROLE_SUPER_ADMIN, auth.ROLE_ADMIN]]
    services_list = services.obtenir_services_actifs()
    
    # Calculer les statistiques
    stats = {
        'nb_directeurs': len([a for a in admins_list if a['role'] == auth.ROLE_SUPER_ADMIN]),
        'nb_responsables': len([a for a in admins_list if a['role'] == auth.ROLE_ADMIN]),
        'nb_utilisateurs': len([a for a in auth.lister_admins() if a['role'] == auth.ROLE_USER])
    }
    
    return render_template('gestion_admins.html',
                         admin_info=session['admin_info'],
                         admins=admins_list,
                         services=services_list,
                         stats=stats,
                         auth=auth)

@app.route('/ajouter_admin', methods=['POST'])
@super_admin_required
def ajouter_admin():
    """Ajouter un administrateur - Super-admin uniquement"""
    nom_utilisateur = request.form.get('nom_utilisateur', '').strip()
    mot_de_passe = request.form.get('mot_de_passe', '').strip()
    role = request.form.get('role', auth.ROLE_ADMIN)
    service_id = request.form.get('service_id') or None
    email = request.form.get('email', '').strip()

    if not nom_utilisateur or not mot_de_passe:
        flash('Le nom d\'utilisateur et le mot de passe sont obligatoires !', 'danger')
        return redirect(url_for('gestion_admins'))

    # Super-admin peut créer uniquement des admins (pas des users)
    if role not in [auth.ROLE_SUPER_ADMIN, auth.ROLE_ADMIN]:
        flash('Rôle invalide. Utilisez gestion_utilisateurs pour créer des utilisateurs.', 'danger')
        return redirect(url_for('gestion_admins'))

    if auth.creer_admin(nom_utilisateur, mot_de_passe, role, service_id, email):
        flash(f'Administrateur "{nom_utilisateur}" créé avec succès !', 'success')
    else:
        flash('Erreur lors de la création de l\'administrateur.', 'danger')

    return redirect(url_for('gestion_admins'))

@app.route('/modifier_admin/<int:id>', methods=['POST'])
@super_admin_required
def modifier_admin(id):
    """Modifier un administrateur"""
    role = request.form.get('role')
    service_id = request.form.get('service_id') or None
    email = request.form.get('email', '').strip()
    nouveau_mdp = request.form.get('nouveau_mdp', '').strip()
    
    if auth.modifier_admin(id, role=role, service_id=service_id, email=email,
                           nouveau_mdp=nouveau_mdp if nouveau_mdp else None):
        flash('Administrateur modifié avec succès !', 'success')
    else:
        flash('Erreur lors de la modification.', 'danger')
    
    return redirect(url_for('gestion_admins'))

@app.route('/supprimer_admin/<int:id>')
@super_admin_required
def supprimer_admin(id):
    """Supprimer un administrateur"""
    # Empêcher la suppression de soi-même
    if id == session['admin_info']['id']:
        flash('Vous ne pouvez pas supprimer votre propre compte.', 'danger')
        return redirect(url_for('gestion_admins'))
    
    if auth.supprimer_admin(id):
        flash('Administrateur supprimé avec succès !', 'success')
    else:
        flash('Erreur lors de la suppression.', 'danger')
    
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
        # RDV en attente pour tous les services
        rdv_en_attente = rdv_manager.obtenir_rendez_vous_en_attente()
        today = date.today().strftime('%Y-%m-%d')
        rdv_aujourd_hui = rdv_manager.obtenir_rendez_vous_par_date(today)
        
        return render_template('dashboard.html', 
                             admin_info=admin_info,
                             services=services_list,
                             total_rdv=total_rdv,
                             rdv_aujourd_hui=rdv_aujourd_hui,
                             rdv_en_attente=rdv_en_attente,
                             auth=auth)
        
    elif auth.est_admin(admin_info):
        # Admin voit son service
        service_id = admin_info.get('service_id')
        if service_id:
            service = services.obtenir_service_par_id(service_id)
            services_list = [service] if service else []
            stats = rdv_manager.obtenir_statistiques_service(service_id) if service else {'total': 0, 'en_attente': 0, 'confirmes': 0}
            total_rdv = stats['total']
            # RDV en attente pour ce service
            rdv_en_attente = rdv_manager.obtenir_rendez_vous_en_attente(service_id)
        else:
            services_list = []
            total_rdv = 0
            rdv_en_attente = []
        today = date.today().strftime('%Y-%m-%d')
        rdv_aujourd_hui = rdv_manager.obtenir_rendez_vous_par_date(today)
        
        return render_template('dashboard.html', 
                             admin_info=admin_info,
                             services=services_list,
                             total_rdv=total_rdv,
                             rdv_aujourd_hui=rdv_aujourd_hui,
                             rdv_en_attente=rdv_en_attente,
                             auth=auth)
    else:
        # Patient (user) - Dashboard spécifique
        user_email = admin_info.get('email')
        
        # Récupérer les rendez-vous du patient
        if user_email:
            rdv_list = rdv_manager.obtenir_rendez_vous_par_patient(user_email)
            rdv_prochains = rdv_manager.obtenir_prochains_rendez_vous(user_email, 5)
        else:
            rdv_list = []
            rdv_prochains = []
        
        # Statistiques
        stats = {
            'total': len(rdv_list),
            'en_attente': len([r for r in rdv_list if r.get('statut') == 'en_attente']),
            'confirmes': len([r for r in rdv_list if r.get('statut') == 'confirmé']),
            'rejetes': len([r for r in rdv_list if r.get('statut') == 'rejeté'])
        }
        
        # Récupérer les infos du contact
        contact_info = None
        if admin_info.get('contact_id'):
            conn = sqlite3.connect("polyclinique.db")
            cursor = conn.cursor()
            cursor.execute("SELECT nom, prenom, email, telephone, adresse, fonction, entreprise FROM contacts WHERE id = ?", 
                          (admin_info['contact_id'],))
            row = cursor.fetchone()
            conn.close()
            if row:
                contact_info = {
                    'nom': row[0], 'prenom': row[1], 'email': row[2],
                    'telephone': row[3], 'adresse': row[4], 'fonction': row[5], 'entreprise': row[6]
                }
        
        return render_template('dashboard_user.html',
                             admin_info=admin_info,
                             contact_info=contact_info,
                             total_rdv=stats['total'],
                             rdv_prochains=rdv_prochains,
                             stats=stats,
                             auth=auth)

# ==================== GESTION DES CONTACTS ====================

@app.route('/contacts')
@login_required
def index():
    contacts_tries = sorted(carnet.contacts, key=lambda c: (c.categorie, c.nom.lower(), c.prenom.lower()))
    return render_template('index.html', contacts=contacts_tries, admin_info=session['admin_info'], auth=auth)

@app.route('/rechercher')
@login_required
def rechercher():
    """Rechercher des contacts"""
    query = request.args.get('q', '').strip().lower()

    if query:
        # Rechercher dans nom, prénom, email, téléphone
        resultats = [c for c in carnet.contacts if
                     query in c.nom.lower() or
                     query in c.prenom.lower() or
                     query in c.email.lower() or
                     query in c.telephone.lower()]
    else:
        resultats = carnet.contacts

    contacts_tries = sorted(resultats, key=lambda c: (c.categorie, c.nom.lower(), c.prenom.lower()))
    return render_template('index.html', contacts=contacts_tries, admin_info=session['admin_info'], 
                          recherche=query, auth=auth)

@app.route('/filtrer/<categorie>')
@login_required
def filtrer_categorie(categorie):
    """Filtrer les contacts par catégorie"""
    contacts_filtres = [c for c in carnet.contacts if c.categorie == categorie]
    contacts_tries = sorted(contacts_filtres, key=lambda c: (c.nom.lower(), c.prenom.lower()))
    return render_template('index.html', contacts=contacts_tries, admin_info=session['admin_info'], 
                          categorie_filtree=categorie, auth=auth)

@app.route('/ajouter', methods=['GET', 'POST'])
@admin_required
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
        
        result = carnet.ajouter_contact(nom, prenom, email, telephone, adresse, fonction, entreprise, categorie)
        if isinstance(result, tuple):
            success, message = result
        else:
            success = result
            message = 'Contact ajouté avec succès !' if success else 'Erreur lors de l\'ajout.'
        
        if success:
            flash(message, 'success')
            return redirect(url_for('index'))
        else:
            flash(message, 'danger')
    
    return render_template('ajouter.html', admin_info=session['admin_info'], auth=auth)

@app.route('/modifier/<nom>/<prenom>', methods=['GET', 'POST'])
@admin_required
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
        
        result = carnet.modifier_contact(
            nom, prenom,
            nouveau_nom if nouveau_nom != contact.nom else None,
            nouveau_prenom if nouveau_prenom != contact.prenom else None,
            nouveau_email if nouveau_email != contact.email else None,
            nouveau_telephone if nouveau_telephone != contact.telephone else None,
            nouvelle_adresse,  # Toujours passer pour permettre la suppression
            nouvelle_fonction,  # Toujours passer pour permettre la suppression
            nouvelle_entreprise,  # Toujours passer pour permettre la suppression
            nouvelle_categorie if nouvelle_categorie != contact.categorie else None
        )
        
        if isinstance(result, tuple):
            success, message = result
        else:
            success = result
            message = 'Contact modifié avec succès !' if success else 'Erreur lors de la modification.'
        
        if success:
            flash(message, 'success')
            return redirect(url_for('index'))
        else:
            flash(message, 'danger')
    
    return render_template('modifier.html', contact=contact, admin_info=session['admin_info'], auth=auth)

@app.route('/supprimer/<nom>/<prenom>')
@admin_required
def supprimer(nom, prenom):
    result = carnet.supprimer_contact(nom, prenom)
    if isinstance(result, tuple):
        success, message = result
    else:
        success = result
        message = 'Contact supprimé ! 🗑️' if success else 'Erreur lors de la suppression.'
    
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('index'))

@app.route('/whatsapp/<nom>/<prenom>')
@login_required
def whatsapp(nom, prenom):
    """Ouvrir WhatsApp avec le contact"""
    contact = carnet.rechercher_contact(nom, prenom)

    if not contact:
        flash('Contact introuvable !', 'danger')
        return redirect(url_for('index'))

    # Formater le numéro de téléphone pour WhatsApp (supprimer espaces et caractères spéciaux)
    telephone = contact.telephone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

    # Rediriger vers WhatsApp Web
    whatsapp_url = f'https://wa.me/{telephone}'
    return redirect(whatsapp_url)

# ==================== AGENDA & RENDEZ-VOUS ====================

@app.route('/agenda')
@login_required
def agenda():
    """Page principale de l'agenda"""
    admin_info = session['admin_info']
    
    # Tous les utilisateurs (y compris patients) peuvent voir l'agenda
    services_list = services.obtenir_services_actifs()
    
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
                         creneaux=creneaux,
                         auth=auth)

@app.route('/prendre_rdv', methods=['GET', 'POST'])
@login_required
def prendre_rdv():
    """Prendre un rendez-vous - Accessible aux utilisateurs et admins"""
    admin_info = session['admin_info']
    
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
        
        # Calculer heure_fin si non fournie (30 min par défaut)
        if not heure_fin:
            from datetime import datetime, timedelta
            heure_dt = datetime.strptime(heure_debut, "%H:%M")
            heure_fin_dt = heure_dt + timedelta(minutes=30)
            heure_fin = heure_fin_dt.strftime("%H:%M")
        
        # Pour les utilisateurs (patients), utiliser leur email si non fourni
        if auth.est_user(admin_info) and not patient_email:
            patient_email = admin_info.get('email', '')
        
        success, message, rdv_id = rdv_manager.prendre_rendez_vous(
            int(service_id),
            patient_nom, patient_prenom, patient_telephone,
            date_rdv, heure_debut, heure_fin,
            motif, patient_email,
            admin_info['id']
        )
        
        if success:
            if auth.est_user(admin_info):
                flash('Votre demande de rendez-vous a été soumise et est en attente de validation par un administrateur.', 'info')
            else:
                flash(message, 'success')
        else:
            flash(message, 'danger')
        
        return redirect(url_for('mes_rdv'))
    
    # GET
    service_id = request.args.get('service_id')
    date_rdv = request.args.get('date')
    heure_debut = request.args.get('heure_debut')
    heure_fin = request.args.get('heure_fin')
    
    service = services.obtenir_service_par_id(int(service_id)) if service_id else None
    
    # Récupérer tous les services pour la sélection
    services_list = services.obtenir_services_actifs()
    
    # Date minimale (aujourd'hui)
    from datetime import date
    date_min = date.today().strftime('%Y-%m-%d')
    
    # Pré-remplir les infos pour les patients
    prefill_nom = ''
    prefill_prenom = ''
    prefill_email = ''
    prefill_telephone = ''
    
    if auth.est_user(admin_info) and admin_info.get('contact_id'):
        # Récupérer les infos du contact
        conn = sqlite3.connect("polyclinique.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nom, prenom, email, telephone FROM contacts WHERE id = ?", 
                      (admin_info['contact_id'],))
        contact = cursor.fetchone()
        conn.close()
        if contact:
            prefill_nom = contact[0]
            prefill_prenom = contact[1]
            prefill_email = contact[2]
            prefill_telephone = contact[3]
    
    return render_template('prendre_rdv.html',
                         admin_info=admin_info,
                         service=service,
                         services=services_list,
                         date_rdv=date_rdv,
                         heure_debut=heure_debut,
                         heure_fin=heure_fin,
                         date_min=date_min,
                         prefill_nom=prefill_nom,
                         prefill_prenom=prefill_prenom,
                         prefill_email=prefill_email,
                         prefill_telephone=prefill_telephone,
                         auth=auth)

@app.route('/api/creneaux')
@admin_required
def api_creneaux():
    """API pour récupérer les créneaux disponibles (AJAX)"""
    date_str = request.args.get('date')
    service_id = request.args.get('service')
    
    if not date_str or not service_id:
        return jsonify({'error': 'Paramètres manquants'}), 400
    
    service = services.obtenir_service_par_id(int(service_id))
    if not service:
        return jsonify({'error': 'Service non trouvé'}), 404
    
    creneaux = rdv_manager.generer_creneaux(date_str, service['horaire_debut'], service['horaire_fin'])
    
    # Récupérer les créneaux occupés
    creneaux_occupes = []
    for debut, fin in creneaux:
        if not rdv_manager.verifier_disponibilite(int(service_id), date_str, debut):
            creneaux_occupes.append(debut)
    
    # Formater les créneaux pour l'affichage
    creneaux_formates = [f"{debut}" for debut, fin in creneaux]
    
    return jsonify({
        'creneaux': creneaux_formates,
        'creneaux_occupes': creneaux_occupes
    })

@app.route('/mes_rdv')
@login_required
def mes_rdv():
    """Liste des rendez-vous - Affiche selon le rôle de l'utilisateur"""
    admin_info = session['admin_info']

    if auth.est_super_admin(admin_info):
        # Super-admin voit tous les RDV
        rdv_list = []
        for s in services.obtenir_services_actifs():
            rdv_list.extend(rdv_manager.obtenir_rendez_vous_par_service(s['id']))
    elif auth.est_admin(admin_info):
        # Admin voit les RDV de son service
        service_id = admin_info.get('service_id')
        if service_id:
            rdv_list = rdv_manager.obtenir_rendez_vous_par_service(service_id)
        else:
            rdv_list = []
    else:
        # Patient (user) voit uniquement SES rendez-vous (par email)
        user_email = admin_info.get('email')
        if user_email:
            rdv_list = rdv_manager.obtenir_rendez_vous_par_patient(user_email)
        else:
            rdv_list = []

    # Calculer les statistiques
    stats = {
        'a_venir': len([rdv for rdv in rdv_list if rdv.get('statut') in ['confirmé', 'en_attente']]),
        'en_attente': len([rdv for rdv in rdv_list if rdv.get('statut') == 'en_attente']),
        'confirmes': len([rdv for rdv in rdv_list if rdv.get('statut') == 'confirmé']),
        'rejetes': len([rdv for rdv in rdv_list if rdv.get('statut') == 'rejeté']),
        'passes': len([rdv for rdv in rdv_list if rdv.get('statut') == 'passé'])
    }
    
    # Récupérer les RDV en attente de validation (pour les admins)
    rdv_en_attente = []
    if auth.est_super_admin(admin_info):
        rdv_en_attente = rdv_manager.obtenir_rendez_vous_en_attente()
    elif auth.est_admin(admin_info):
        service_id = admin_info.get('service_id')
        if service_id:
            rdv_en_attente = rdv_manager.obtenir_rendez_vous_en_attente(service_id)

    return render_template('mes_rdv.html',
                         admin_info=admin_info,
                         rendez_vous=rdv_list,
                         stats=stats,
                         rdv_en_attente=rdv_en_attente,
                         auth=auth)

@app.route('/annuler_rdv/<int:rdv_id>')
@login_required
def annuler_rdv(rdv_id):
    """Annuler un rendez-vous"""
    # Vérifier que l'utilisateur peut annuler ce RDV
    admin_info = session['admin_info']
    
    # Récupérer le RDV
    conn = sqlite3.connect("polyclinique.db")
    cursor = conn.cursor()
    cursor.execute("SELECT patient_email, cree_par FROM rendez_vous WHERE id = ?", (rdv_id,))
    rdv = cursor.fetchone()
    conn.close()
    
    if not rdv:
        flash('Rendez-vous introuvable.', 'danger')
        return redirect(url_for('mes_rdv'))
    
    patient_email, cree_par = rdv
    
    # Vérifier les permissions
    can_cancel = False
    if auth.est_super_admin(admin_info) or auth.est_admin(admin_info):
        can_cancel = True
    elif auth.est_user(admin_info) and admin_info.get('email') == patient_email:
        # Un patient peut annuler son propre RDV en attente
        can_cancel = True
    
    if not can_cancel:
        flash('Vous n\'avez pas la permission d\'annuler ce rendez-vous.', 'danger')
        return redirect(url_for('mes_rdv'))
    
    if rdv_manager.annuler_rendez_vous(rdv_id):
        flash('Rendez-vous annulé avec succès !', 'success')
    else:
        flash('Erreur lors de l\'annulation.', 'danger')

    return redirect(url_for('mes_rdv'))

@app.route('/valider_rdv/<int:rdv_id>', methods=['POST'])
@admin_required
def valider_rdv(rdv_id):
    """Valider un rendez-vous (Admin uniquement)"""
    commentaire = request.form.get('commentaire', '').strip()
    admin_id = session['admin_info']['id']
    
    success, message = rdv_manager.valider_rendez_vous(rdv_id, admin_id, commentaire)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('mes_rdv'))

@app.route('/rejeter_rdv/<int:rdv_id>', methods=['POST'])
@admin_required
def rejeter_rdv(rdv_id):
    """Rejeter un rendez-vous (Admin uniquement)"""
    commentaire = request.form.get('commentaire', '').strip()
    admin_id = session['admin_info']['id']
    
    if not commentaire:
        flash('Veuillez indiquer un motif de rejet.', 'danger')
        return redirect(url_for('mes_rdv'))
    
    if rdv_manager.rejeter_rendez_vous(rdv_id, admin_id, commentaire):
        flash('Rendez-vous rejeté.', 'warning')
    else:
        flash('Erreur lors du rejet. Le rendez-vous a peut-être déjà été traité.', 'danger')
    
    return redirect(url_for('mes_rdv'))

@app.route('/validation_rdv')
@admin_required
def validation_rdv():
    """Page de validation des rendez-vous en attente"""
    admin_info = session['admin_info']
    
    if auth.est_super_admin(admin_info):
        # Super admin voit tous les RDV en attente
        rdv_en_attente = rdv_manager.obtenir_rendez_vous_en_attente()
    else:
        # Admin voit les RDV en attente de son service
        service_id = admin_info.get('service_id')
        if service_id:
            rdv_en_attente = rdv_manager.obtenir_rendez_vous_en_attente(service_id)
        else:
            rdv_en_attente = []
    
    return render_template('validation_rdv.html',
                         admin_info=admin_info,
                         rdv_en_attente=rdv_en_attente,
                         auth=auth)

@app.route('/modifier_rdv/<int:id>', methods=['GET', 'POST'])
@admin_required
def modifier_rdv(id):
    """Modifier un rendez-vous"""
    if request.method == 'POST':
        # Implémenter la logique de modification
        flash('Fonctionnalité de modification en cours de développement', 'info')
        return redirect(url_for('mes_rdv'))

    # GET - afficher le formulaire
    flash('Fonctionnalité de modification en cours de développement', 'info')
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
                         admins=admins_list,
                         auth=auth)

@app.route('/modifier_service/<int:id>', methods=['POST'])
@super_admin_required
def modifier_service(id):
    """Modifier un service"""
    nom = request.form.get('nom', '').strip()
    description = request.form.get('description', '').strip()
    horaire_debut = request.form.get('horaire_debut', '08:00').strip()
    horaire_fin = request.form.get('horaire_fin', '18:00').strip()
    responsable_id = request.form.get('responsable_id') or None
    
    conn = sqlite3.connect("polyclinique.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE services 
        SET nom = ?, description = ?, horaire_debut = ?, horaire_fin = ?, responsable_id = ?
        WHERE id = ?
    """, (nom, description, horaire_debut, horaire_fin, responsable_id, id))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    if success:
        services.charger_services()
        flash('Service modifié avec succès !', 'success')
    else:
        flash('Erreur lors de la modification.', 'danger')
    
    return redirect(url_for('gestion_services'))

@app.route('/ajouter_service', methods=['POST'])
@super_admin_required
def ajouter_service():
    """Ajouter un service"""
    nom = request.form.get('nom', '').strip()
    description = request.form.get('description', '').strip()
    horaire_debut = request.form.get('horaire_debut', '08:00').strip()
    horaire_fin = request.form.get('horaire_fin', '18:00').strip()
    
    if not nom:
        flash('Le nom du service est obligatoire.', 'danger')
        return redirect(url_for('gestion_services'))
    
    if services.ajouter_service(nom, description, horaire_debut, horaire_fin):
        flash(f'Service "{nom}" ajouté avec succès !', 'success')
    else:
        flash('Erreur lors de l\'ajout du service.', 'danger')
    
    return redirect(url_for('gestion_services'))

@app.route('/supprimer_service/<int:id>')
@super_admin_required
def supprimer_service(id):
    """Supprimer un service"""
    conn = sqlite3.connect("polyclinique.db")
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM services WHERE id = ?", (id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    if success:
        services.charger_services()
        flash('Service supprimé avec succès !', 'success')
    else:
        flash('Erreur lors de la suppression.', 'danger')
    
    return redirect(url_for('gestion_services'))

# ==================== CONFIGURATION ====================

@app.route('/configuration', methods=['GET', 'POST'])
@super_admin_required
def configuration():
    """Page de configuration du système"""
    global EMAIL_EXPEDITEUR, MOT_DE_PASSE_EMAIL, comm
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'email':
            email = request.form.get('email_expediteur', '').strip()
            password = request.form.get('email_password', '').strip()
            
            if email and password:
                save_email_config(email, password)
                EMAIL_EXPEDITEUR = email
                MOT_DE_PASSE_EMAIL = password
                comm = Communication(EMAIL_EXPEDITEUR, MOT_DE_PASSE_EMAIL)
                flash('Configuration email sauvegardée avec succès !', 'success')
            else:
                flash('Veuillez remplir tous les champs.', 'danger')
        
        return redirect(url_for('configuration'))
    
    # GET
    email_config, _ = get_email_config()
    config = {
        'email': email_config,
        'email_configured': bool(email_config)
    }
    
    return render_template('configuration.html', 
                         admin_info=session['admin_info'],
                         config=config,
                         auth=auth)

# ==================== COMMUNICATION ====================

@app.route('/mon_profil', methods=['GET', 'POST'])
@login_required
def mon_profil():
    """Page de profil pour les utilisateurs (patients)"""
    admin_info = session['admin_info']
    
    # Vérifier que c'est un user (patient)
    if not auth.est_user(admin_info):
        flash('Cette page est réservée aux patients.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Récupérer les infos du contact
    contact_info = None
    if admin_info.get('contact_id'):
        conn = sqlite3.connect("polyclinique.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom, prenom, email, telephone, adresse, fonction, entreprise FROM contacts WHERE id = ?", 
                      (admin_info['contact_id'],))
        row = cursor.fetchone()
        conn.close()
        if row:
            contact_info = {
                'id': row[0], 'nom': row[1], 'prenom': row[2], 'email': row[3],
                'telephone': row[4], 'adresse': row[5], 'fonction': row[6], 'entreprise': row[7]
            }
    
    if request.method == 'POST':
        # Mise à jour du mot de passe si fourni
        nouveau_mdp = request.form.get('nouveau_mdp', '').strip()
        confirmer_mdp = request.form.get('confirmer_mdp', '').strip()
        
        if nouveau_mdp:
            if len(nouveau_mdp) < 6:
                flash('Le mot de passe doit contenir au moins 6 caractères !', 'danger')
                return redirect(url_for('mon_profil'))
            if nouveau_mdp != confirmer_mdp:
                flash('Les mots de passe ne correspondent pas !', 'danger')
                return redirect(url_for('mon_profil'))
            
            # Mettre à jour le mot de passe
            auth.modifier_mot_de_passe(admin_info['nom_utilisateur'], '', nouveau_mdp)
            flash('Mot de passe mis à jour avec succès !', 'success')
        
        # Mise à jour des infos de contact
        if contact_info:
            nom = request.form.get('nom', '').strip().upper()
            prenom = request.form.get('prenom', '').strip()
            telephone = request.form.get('telephone', '').strip()
            email = request.form.get('email_contact', '').strip()
            adresse = request.form.get('adresse', '').strip()
            fonction = request.form.get('fonction', '').strip()
            entreprise = request.form.get('entreprise', '').strip()
            
            # Mettre à jour le contact
            conn = sqlite3.connect("polyclinique.db")
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    UPDATE contacts 
                    SET nom = ?, prenom = ?, telephone = ?, email = ?, 
                        adresse = ?, fonction = ?, entreprise = ?,
                        date_modification = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (nom, prenom, telephone, email, adresse, fonction, entreprise, contact_info['id']))
                conn.commit()
                flash('Informations personnelles mises à jour avec succès !', 'success')
            except sqlite3.IntegrityError as e:
                error_msg = str(e).lower()
                if 'email' in error_msg:
                    flash('Cet email est déjà utilisé par un autre patient.', 'danger')
                elif 'telephone' in error_msg:
                    flash('Ce numéro de téléphone est déjà utilisé.', 'danger')
                else:
                    flash('Erreur lors de la mise à jour.', 'danger')
            finally:
                conn.close()
        
        return redirect(url_for('mon_profil'))
    
    # GET
    return render_template('mon_profil.html',
                         admin_info=admin_info,
                         contact_info=contact_info,
                         auth=auth)

@app.route('/envoyer-email/<nom>/<prenom>', methods=['GET', 'POST'])
@login_required
def envoyer_email(nom, prenom):
    contact = carnet.rechercher_contact(nom, prenom)
    
    if not contact:
        flash('Contact introuvable !', 'danger')
        return redirect(url_for('index'))
    
    # Recharger la config email au cas où elle a changé
    global EMAIL_EXPEDITEUR, MOT_DE_PASSE_EMAIL, comm
    EMAIL_EXPEDITEUR, MOT_DE_PASSE_EMAIL = get_email_config()
    comm = Communication(EMAIL_EXPEDITEUR, MOT_DE_PASSE_EMAIL)
    
    if request.method == 'POST':
        sujet = request.form.get('sujet', '').strip()
        message = request.form.get('message', '').strip()
        
        if not sujet or not message:
            flash('Le sujet et le message sont obligatoires !', 'danger')
            return render_template('envoyer_email.html', contact=contact, admin_info=session['admin_info'], 
                                  config_email=bool(EMAIL_EXPEDITEUR), auth=auth)
        
        success, msg = comm.envoyer_email(contact.email, sujet, message, html=False)
        
        if success:
            flash(msg, 'success')
            return redirect(url_for('index'))
        else:
            flash(msg, 'danger')
    
    return render_template('envoyer_email.html', contact=contact, admin_info=session['admin_info'],
                          config_email=bool(EMAIL_EXPEDITEUR), auth=auth)

# ==================== LANCEMENT ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
