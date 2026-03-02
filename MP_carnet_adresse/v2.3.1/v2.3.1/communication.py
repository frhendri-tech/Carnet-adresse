import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import webbrowser
import urllib.parse

class Communication:
    """Classe pour gérer l'envoi d'emails et de messages WhatsApp"""
    
    def __init__(self, email_expediteur=None, mot_de_passe_email=None):
        """
        Initialise le module de communication
        
        Args:
            email_expediteur (str): Adresse email de l'expéditeur
            mot_de_passe_email (str): Mot de passe de l'email (ou mot de passe d'application)
        """
        self.email_expediteur = email_expediteur
        self.mot_de_passe_email = mot_de_passe_email
    
    def envoyer_email(self, destinataire, sujet, message, html=False):
        """
        Envoie un email à un contact.
        Si les credentials SMTP ne sont pas configurés, simule un envoi (mode développement).
        
        Args:
            destinataire (str): Adresse email du destinataire
            sujet (str): Sujet de l'email
            message (str): Corps du message
            html (bool): Si True, le message est en HTML
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # Vérifie si les credentials sont configurés (non vides)
        email_ok = self.email_expediteur and str(self.email_expediteur).strip()
        pass_ok = self.mot_de_passe_email and str(self.mot_de_passe_email).strip()
        
        if not email_ok or not pass_ok:
            # Mode simulation : l'email est "fakement" envoyé
            print(f"\n[FAKE EMAIL - Mode Développement]")
            print(f"{'='*50}")
            print(f"De: noreply@polyclinique.local")
            print(f"À: {destinataire}")
            print(f"Sujet: {sujet}")
            print(f"{'='*50}")
            print(f"{message[:500]}{'...' if len(message) > 500 else ''}")
            print(f"{'='*50}\n")
            return (True, f"[SIMULATION] Email envoyé à {destinataire} (configurez SMTP pour un envoi réel)")
        
        try:
            # Créer le message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_expediteur
            msg['To'] = destinataire
            msg['Subject'] = sujet
            
            # Ajouter le corps du message
            if html:
                part = MIMEText(message, 'html')
            else:
                part = MIMEText(message, 'plain')
            msg.attach(part)
            
            # Connexion au serveur SMTP Gmail
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_expediteur, self.mot_de_passe_email)
            
            # Envoyer l'email
            server.send_message(msg)
            server.quit()
            
            return (True, f"Email envoyé avec succès à {destinataire} !")
            
        except smtplib.SMTPAuthenticationError:
            return (False, "Erreur d'authentification. Vérifiez votre email et mot de passe.")
        except smtplib.SMTPException as e:
            return (False, f"Erreur SMTP : {str(e)}")
        except Exception as e:
            return (False, f"Erreur lors de l'envoi : {str(e)}")
    
    def envoyer_whatsapp_web(self, numero, message):
        """
        Ouvre WhatsApp Web avec un message pré-rempli
        
        Args:
            numero (str): Numéro de téléphone (format international recommandé)
            message (str): Message à envoyer
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Nettoyer le numéro (enlever espaces, tirets, etc.)
            numero_clean = ''.join(filter(str.isdigit, numero))
            
            # Si le numéro commence par 0, on suppose que c'est un numéro marocain
            if numero_clean.startswith('0'):
                numero_clean = '212' + numero_clean[1:]  # +212 pour le Maroc
            elif not numero_clean.startswith('212') and not numero_clean.startswith('+'):
                numero_clean = '212' + numero_clean
            
            # Encoder le message pour l'URL
            message_encoded = urllib.parse.quote(message)
            
            # Créer l'URL WhatsApp Web
            url = f"https://web.whatsapp.com/send?phone={numero_clean}&text={message_encoded}"
            
            # Ouvrir dans le navigateur
            webbrowser.open(url)
            
            return (True, f"WhatsApp Web ouvert pour {numero}. Veuillez appuyer sur Entrée pour envoyer le message.")
            
        except Exception as e:
            return (False, f"Erreur lors de l'ouverture de WhatsApp : {str(e)}")
    
    def envoyer_whatsapp_mobile(self, numero, message):
        """
        Ouvre l'application WhatsApp mobile avec un message pré-rempli
        
        Args:
            numero (str): Numéro de téléphone
            message (str): Message à envoyer
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Nettoyer le numéro
            numero_clean = ''.join(filter(str.isdigit, numero))
            
            if numero_clean.startswith('0'):
                numero_clean = '212' + numero_clean[1:]
            elif not numero_clean.startswith('212'):
                numero_clean = '212' + numero_clean
            
            # Encoder le message
            message_encoded = urllib.parse.quote(message)
            
            # URL pour mobile
            url = f"https://api.whatsapp.com/send?phone={numero_clean}&text={message_encoded}"
            
            webbrowser.open(url)
            
            return (True, f"WhatsApp ouvert pour {numero}.")
            
        except Exception as e:
            return (False, f"Erreur : {str(e)}")
    
    def email_est_configure(self):
        """
        Vérifie si l'email est configuré pour un envoi réel
        
        Returns:
            bool: True si les credentials SMTP sont configurés
        """
        # Vérifie que les credentials existent et ne sont pas vides
        email_ok = self.email_expediteur and str(self.email_expediteur).strip()
        pass_ok = self.mot_de_passe_email and str(self.mot_de_passe_email).strip()
        return bool(email_ok and pass_ok)
    
    def envoyer_email_multiple(self, destinataires, sujet, message, html=False):
        """
        Envoie un email à plusieurs contacts.
        Si les credentials SMTP ne sont pas configurés, simule un envoi (mode développement).
        
        Args:
            destinataires (list): Liste d'adresses email
            sujet (str): Sujet de l'email
            message (str): Corps du message
            html (bool): Si True, le message est en HTML
            
        Returns:
            tuple: (nb_success: int, nb_errors: int, erreurs: list)
        """
        # Si pas configuré, simuler l'envoi pour tous
        if not self.email_est_configure():
            print(f"\n[FAKE EMAIL MULTIPLE - Mode Développement]")
            print(f"{'='*50}")
            print(f"Destinataires: {', '.join(destinataires)}")
            print(f"Sujet: {sujet}")
            print(f"Nombre d'emails simulés: {len(destinataires)}")
            print(f"{'='*50}\n")
            return (len(destinataires), 0, ["Mode simulation - aucun email réel envoyé"])
        
        success = 0
        errors = 0
        erreurs_detail = []
        
        for destinataire in destinataires:
            resultat, msg = self.envoyer_email(destinataire, sujet, message, html)
            if resultat:
                success += 1
            else:
                errors += 1
                erreurs_detail.append(f"{destinataire}: {msg}")
        
        return (success, errors, erreurs_detail)
    
    @staticmethod
    def generer_template_email(nom_contact, type_message="bienvenue"):
        """
        Génère un template d'email HTML
        
        Args:
            nom_contact (str): Nom du contact
            type_message (str): Type de template (bienvenue, rappel, invitation)
            
        Returns:
            str: Template HTML
        """
        templates = {
            "bienvenue": f"""
                <html>
                    <body style="font-family: Arial, sans-serif; padding: 20px;">
                        <h2 style="color: #667eea;">Bonjour {nom_contact} !</h2>
                        <p>Nous sommes ravis de vous compter parmi nos contacts.</p>
                        <p>N'hésitez pas à nous contacter pour toute question.</p>
                        <br>
                        <p>Cordialement,</p>
                        <p><strong>L'équipe</strong></p>
                    </body>
                </html>
            """,
            "rappel": f"""
                <html>
                    <body style="font-family: Arial, sans-serif; padding: 20px;">
                        <h2 style="color: #f39c12;">Rappel - {nom_contact}</h2>
                        <p>Ceci est un rappel concernant notre prochain rendez-vous.</p>
                        <p>Nous vous attendons avec plaisir.</p>
                        <br>
                        <p>Cordialement,</p>
                    </body>
                </html>
            """,
            "invitation": f"""
                <html>
                    <body style="font-family: Arial, sans-serif; padding: 20px;">
                        <h2 style="color: #27ae60;">Invitation - {nom_contact}</h2>
                        <p>Vous êtes cordialement invité(e) à notre événement.</p>
                        <p>Nous serions honorés de votre présence.</p>
                        <br>
                        <p>Cordialement,</p>
                    </body>
                </html>
            """
        }
        
        return templates.get(type_message, templates["bienvenue"])