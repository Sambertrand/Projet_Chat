# Projet_Chat


##todo
   ###server:
        serveur memorise la liste des ip coinnectées    //done
        connecte un pseudo à une IP                     //done
        écouter non stop +reveption des commandes       //done
        supprimer de la base de donner quand il quit    //done
        



   ###client:
        (/help)
        /join en P2P avec le pseudo fournie par le pseudo serveur (reçoit un dico avec {pseudo: adresse)
        /connect en serveur      //Done
        /quit server             //Done
        /quit p2p                //Done
        listen server /clients   //Done
        demande de pseudo        //Done


   ###README:
         expliquer le protocole de communiation
         expliquer comment notre code marche
         expliquer comment trouver le server

Projet Chat:
Auteurs:Bertrand    Sam     15027
        Degeldt     Martin  15076
Code inspiré du code Chat par Sébastien Combéfis.
Ceci est notre code pour le Projet Chat du labo 3 de Programmation avancée 2BA.
Pour le lance en mode Client - Serveur (TCP) il faut qu'une machine ai la class serveur lancé et un client ai le code
client lancé (le /help du client explique les fonction à utiliser etc).
Pour la connection client - client (UDP), une fois avoir reçu du serveur les adress ip des autres personnes connectées
au serveur il suffit de ce connecter gràce au speudo donné à la personne  souhaité.
les protocols de communication etablé sont une ecoute sur le port 4269 pour le UDP et le port 4200 pour le TCP.