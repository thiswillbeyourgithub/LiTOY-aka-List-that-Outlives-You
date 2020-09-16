# LiTOY
##################################### TODO
'''

        utiliser plusieurs fichiers pour coder, antoine t'a convaincu
        poster sur github en mode privé, ca t'aidera a t'organiser
        comprendre ce que c'est que le locking d'une db, l'interet etc
        rajouter un champs type (text / video / audio / manual) 
               le time to read doit etre time to watch si il s'agit d'une video, utiliser youtube-dl pour trouver la durée si url, ou ffmpeg si c'est un fichier local
               si c'est un pdf : utiliser pdftotext puis le code pour estimer le temps pour lire une page web
        don't pick if card disabled
        prendre le temps de reflechir et repondre a ce message https://www.lesswrong.com/posts/54Bw7Yxouzdg5KxsF/how-do-you-organise-your-reading
        rajouter une syntaxe pour importer avec directement des infos : __length=37pages   __length=17minutes __catgeroy=audio etc et surtout __1/2/3/4 indique si on lui donne par défaut le score du premier 2e 3e ou 4e cinquieme du classement
        il faut qu'un raccourci permette d'ouvrir automatiquement les url dans un navigateur + que ca soit configurable
        organiser un autre fichier contenant la todo list, dont une section "long term ideas", ex :
               penser a rajouter un mode "court terme" qui permet simplement de trier des trucs selon lequel doit etre fait en premier
        rewrite the long SQL request so that it's on multiple lines
        verifier par le calcul que l'ordre dans lequel on fait les combats n'a pas d'importance, ca conditionne la maniere dont tu stockes les resultats
        champs "estimated time to read" + "title of url"
            faut que ca marche aussi si plusieurs url sont données
        verifier que chaque message important est dans le log
        si importé a partir d'un fichier : bouger le fichier dans un dossier ./imported/+date
        les tupple sont plus rapides que les listes, les priviléger
        dans l'url : au cas ou : changer ` en '
        il faut en fait rajouter genre 5 fois des fields qui soit score1/2/3/4/5, score_name et l'utiliser pour faire des trucs plus cmoplexes genre noter des films rapidement, car prendre en compte la taille de fichier video serait ouf
        il faut rajouter une valeur "average" dans les scores qui serait automatiquement transformée en la moyenne des scores correspondant, par exemple pour si tu as un dvd dans une liste de fichier films, tu auras pas la taille du dvd mais tu auras sa longueur et son importance donc ca ferait foirer la formule
        function that automatically checks fields consistency :
             estimated time to read
             title of url
             delta
             presence of importance score
             check for duplicates in url
             presence of time score
             nb of time of importance score is the same as nb of time score
             same for importance
        keep log size < 5MB or compress it
        faire des simulations avec une fausse liste d'item du genre [nombre de 1 a 100 ; nombrer random de 1 a 100]
            utiliser ca pour avoir une idée de la vitesse de convergence
                    utiliser plusieurs valeurs de K
                        tester avec un truc genre "90% de chance de donner la bonne réponse" pour voir comment les real worls data diffèrent des stats theoriques
        use different color for the prompt and the display, to make it more readable and overall nicer to read
        idée : en fait on peut avoir un score par question, et permettre de rajouter des question tout seul non ? voir a la longue si ca serait reelement utile
        if url is found : compute estimated time to read
             if url not found : use waybackmachine
        racourci qui ouvre sqlite browser
        fonction qui choppe/stocke une/plusieurs valeur de la db
          fixer les valeurs initiales de la db
            demander si on veut d'emblées rajouter une categorie lors de l'importation en affichant les categories deja existantes
        tirage au sort du plus grand differentiel
        pour corriger un field : https://stackoverflow.com/questions/2533120/show-default-value-for-editing-on-python-input-possible/2533142#2533142
        calcul de la moyenne  des differentiels
        auto backup a chaque changement de details/category/title etc
        permettre d'exporter la liste or something, eventuellement en format ical, ou format anki
        idée de flo : exporter vers maniana (en tout cas il faut jeter un oeil pour voir ce que c'est) https://f-droid.org/fr/packages/com.zapta.apps.maniana/ 
        il faut que ca affiche le nombre de truc a faire qui sont todo, et si ca croit ou decroit sur 7 jours
        pour la cli : ce truc a l'air cool pour afficher le tables des podiums : http://zetcode.com/python/prettytable/
        pour l'interface une fois que tu as verifie que ca marche bien en cli : apprendre pyqt, clairement ce sera le plus simple et ca t'ouver la porte vers completer anki
        regarder si il y a pas un moyen plus simple que de faire une backup, genre un moyen de faire des unfo a l'infini ou de garder un historique
        rajouter un champs winAgainst et loseAainst, on rajoute l'id de l'adversaire dans le field a chaque combat, ca semble utile pour "refaire" des tris" apres coups ; pas encore sur d'a quoi ca sert mais il faut compter les draws aussi
        idée d'antoine pour l'interface : permettre des command line command genre : litoy set ID --category "truc" ou litoy list --time ou litoy fight -n=50  ou litoy import file  ou   litoy backup    ou    litoy status   ou    litoy testrun 
        noter quelque part que si litoy marche bien il faudra le compatibiliser avec Polar, soit le rendre ineractif (genre qu'il recup des data de polar) soit carrement en le recodant a l'interieur

aide SQL  https://pynative.com/python-sqlite-select-from-table/
          http://www.easypythondocs.com/SQL.html
          https://cheatography.com/explore/search/?q=sqlite

field order :
        1 date added
        2 entry
        3 details
        4 category
        5 starred
        6 progress
        7 importance elo
        8 date importance elo
        9 time_elo
        10 date time elo
        11 delta importance
        12 delta time
        13 global score
        14 time spent comparing
        15 number of comparison
        16 disabled
        17 done
        18 K_value

'''


