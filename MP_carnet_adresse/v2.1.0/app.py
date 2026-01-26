from flask import Flask, render_template, request, redirect, url_for, flash, session
from address_book import AddressBook
from authentification import Authentification
from communication import Communication
from functools import wraps

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_super_securisee_123'

# Initialiser les modules
carnet = AddressBook()
auth = Authentification()

# Configuration Email (à personnaliser)
# IMPORTANT : Pour Gmail, utilisez un "Mot de passe d'application" 
# https://myaccount.google.com/apppasswords
EMAIL_EXPEDITEUR = None  # Ex: "votre.email@gmail.com"
MOT_DE_PASSE_EMAIL = None  # Ex: "votre_mot_de_passe_application"

comm = Communication(EMAIL_EXPEDITEUR, MOT_DE_PASSE_EMAIL)

# Décorateur pour protéger les routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES D'AUTHENTIFICATION ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if auth.verifier_connexion(username, password):
            session['username'] = username
            flash(f'Bienvenue {username} ! 🎉', 'success')
            return redirect(url_for('index'))
        else:
            flash('Identifiants incorrects !', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Déconnexion"""
    username = session.get('username', 'Utilisateur')
    session.pop('username', None)
    flash(f'Au revoir {username} ! 👋', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['POST'])
def register():
    """Création d'un nouveau compte admin"""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    
    if not username or not password:
        flash('Tous les champs sont obligatoires !', 'danger')
        return redirect(url_for('login'))
    
    if password != confirm_password:
        flash('Les mots de passe ne correspondent pas !', 'danger')
        return redirect(url_for('login'))
    
    if auth.creer_admin(username, password):
        flash(f'Compte "{username}" créé avec succès !', 'success')
    else:
        flash('Erreur lors de la création du compte.', 'danger')
    
    return redirect(url_for('login'))

# ==================== ROUTES PRINCIPALES ====================

@app.route('/')
@login_required
def index():
    """Page d'accueil - Liste des contacts"""
    contacts_tries = sorted(carnet.contacts, key=lambda c: (c.nom.lower(), c.prenom.lower()))
    return render_template('index.html', contacts=contacts_tries, username=session['username'])

@app.route('/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter():
    """Page d'ajout de contact"""
    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        email = request.form.get('email', '').strip()
        telephone = request.form.get('telephone', '').strip()
        
        if not (nom and prenom and email and telephone):
            flash('Tous les champs sont obligatoires !', 'danger')
            return redirect(url_for('ajouter'))
        
        if carnet.ajouter_contact(nom, prenom, email, telephone):
            flash(f'Contact "{nom} {prenom}" ajouté avec succès ! ✓', 'success')
            return redirect(url_for('index'))
        else:
            flash('Erreur lors de l\'ajout du contact.', 'danger')
    
    return render_template('ajouter.html', username=session['username'])

@app.route('/modifier/<nom>/<prenom>', methods=['GET', 'POST'])
@login_required
def modifier(nom, prenom):
    """Page de modification de contact"""
    contact = carnet.rechercher_contact(nom, prenom)
    
    if not contact:
        flash('Contact introuvable !', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        nouveau_nom = request.form.get('nom', '').strip()
        nouveau_prenom = request.form.get('prenom', '').strip()
        nouveau_email = request.form.get('email', '').strip()
        nouveau_telephone = request.form.get('telephone', '').strip()
        
        if carnet.modifier_contact(
            nom, prenom,
            nouveau_nom if nouveau_nom != contact.nom else None,
            nouveau_prenom if nouveau_prenom != contact.prenom else None,
            nouveau_email if nouveau_email != contact.email else None,
            nouveau_telephone if nouveau_telephone != contact.telephone else None
        ):
            flash(f'Contact modifié avec succès ! ✓', 'success')
            return redirect(url_for('index'))
        else:
            flash('Erreur lors de la modification.', 'danger')
    
    return render_template('modifier.html', contact=contact, username=session['username'])

@app.route('/supprimer/<nom>/<prenom>')
@login_required
def supprimer(nom, prenom):
    """Suppression d'un contact"""
    if carnet.supprimer_contact(nom, prenom):
        flash(f'Contact supprimé avec succès ! 🗑️', 'success')
    else:
        flash('Erreur lors de la suppression.', 'danger')
    
    return redirect(url_for('index'))

@app.route('/rechercher', methods=['GET'])
@login_required
def rechercher():
    """Recherche de contacts"""
    query = request.args.get('q', '').strip().lower()
    
    if not query:
        return redirect(url_for('index'))
    
    resultats = [
        c for c in carnet.contacts
        if query in c.nom.lower() or 
           query in c.prenom.lower() or 
           query in c.email.lower() or 
           query in c.telephone
    ]
    
    resultats_tries = sorted(resultats, key=lambda c: (c.nom.lower(), c.prenom.lower()))
    
    return render_template('index.html', contacts=resultats_tries, 
                         username=session['username'], recherche=query)

@app.route('/exporter')
@login_required
def exporter():
    """Exporter les contacts en CSV"""
    if carnet.exporter_vers_csv('contacts_export.csv'):
        flash('Contacts exportés vers contacts_export.csv ! 📊', 'success')
    else:
        flash('Erreur lors de l\'exportation.', 'danger')
    
    return redirect(url_for('index'))

# ==================== ROUTES DE COMMUNICATION ====================

@app.route('/envoyer-email/<nom>/<prenom>', methods=['GET', 'POST'])
@login_required
def envoyer_email(nom, prenom):
    """Page d'envoi d'email à un contact"""
    contact = carnet.rechercher_contact(nom, prenom)
    
    if not contact:
        flash('Contact introuvable !', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        sujet = request.form.get('sujet', '').strip()
        message = request.form.get('message', '').strip()
        template_type = request.form.get('template', 'personnalise')
        
        if not sujet or not message:
            flash('Le sujet et le message sont obligatoires !', 'danger')
            return render_template('envoyer_email.html', contact=contact, username=session['username'])
        
        # Envoyer l'email
        if template_type != 'personnalise':
            message_html = Communication.generer_template_email(contact.get_nom_complet(), template_type)
            success, msg = comm.envoyer_email(contact.email, sujet, message_html, html=True)
        else:
            success, msg = comm.envoyer_email(contact.email, sujet, message, html=False)
        
        if success:
            flash(msg, 'success')
            return redirect(url_for('index'))
        else:
            flash(msg, 'danger')
    
    return render_template('envoyer_email.html', contact=contact, username=session['username'])

@app.route('/whatsapp/<nom>/<prenom>')
@login_required
def whatsapp(nom, prenom):
    """Ouvre WhatsApp pour un contact"""
    contact = carnet.rechercher_contact(nom, prenom)
    
    if not contact:
        flash('Contact introuvable !', 'danger')
        return redirect(url_for('index'))
    
    message = f"Bonjour {contact.prenom}, "
    success, msg = comm.envoyer_whatsapp_web(contact.telephone, message)
    
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')
    
    return redirect(url_for('index'))

@app.route('/configuration-email', methods=['GET', 'POST'])
@login_required
def configuration_email():
    """Page de configuration de l'email"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if email and password:
            global comm
            comm = Communication(email, password)
            session['email_config'] = True
            flash('Configuration email enregistrée ! ✓', 'success')
            return redirect(url_for('index'))
        else:
            flash('Veuillez remplir tous les champs !', 'danger')
    
    return render_template('configuration_email.html', username=session['username'])

# ==================== GESTION DES ERREURS ====================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

# ==================== LANCEMENT ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)