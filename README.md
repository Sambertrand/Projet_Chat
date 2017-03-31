# Projet Chat:

**Auteurs:**  
Bertrand    Sam     15027 et 
Degeldt     Martin  15076   
*Code inspiré du code Chat par Sébastien Combéfis.*

Ceci est notre code pour le Projet Chat du labo 3 de Programmation avancée 2BA.  
Pour lancer le programme, tapez soit 'server', soit 'client' en lançant le programme dans votre invite de commande.

* Les protocoles de communication établis sont en écoute sur le port 4269 pour le UDP et le port 4200 pour le TCP.

* Pour établir une connexion Client - Serveur (TCP) il faut qu'une machine lance l'application en mode serveur et une
 autre en mode client  (le /help du client explique les fonctions à utiliser etc).

* Pour la connexion client - client (UDP), une fois avoir reçu du serveur les adresses ip des autres personnes
 connectées au serveur, il suffit de se connecter grâce au pseudo donné à la personne souhaitée.  
L'application en mode client peut fonctionner sans serveur, pour ceci, il suffit de se connecter via l'ip et le port
établi.

* Des commandes racourcies sont disponible.

* Amélioration possible:  
-Se connecter à plusieurs clients  
-Supprimer la commande apres l'avoir écrite (afficher le message envoyé)  
-Créer un 'mode send' qui permet d'envoyer sans taper la commande  