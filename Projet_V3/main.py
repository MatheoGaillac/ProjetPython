import praw
import os
from Corpus import Corpus
from SearchEngine import SearchEngine
from RedditDocument import RedditDocument
from ArxivDocument import ArxivDocument
from datetime import datetime

if __name__ == '__main__' : 
    reddit = praw.Reddit(client_id='CvBa0giChE03eJkVvvb_1A', client_secret='hIaWPpSE821dHejacJKpeHJwr_g3SQ', user_agent='ProjetPythonWeb')

    keywords = input("====== Écrivez votre recherche : ").strip()
    corpus = Corpus(keywords)

    df = corpus.loadCorpus(reddit, keywords)

    #Si un document existe, on le charge, sinon on le sauvegarde
    csv_dir = "csv"
    os.makedirs(csv_dir, exist_ok=True)
    filename = os.path.join(csv_dir, f"{keywords}_corpus.csv")

    if os.path.isfile(filename):
        corpus.load(filename)
    else:
        corpus.save(filename)

    corpus.afficherDocuments()
    # corpus.afficherAuteurs()
    # corpus.affichageDonnees(df)

    # print(corpus)

    # rechercheAuteur = input("======Entrer le nom d'un auteur : ").strip()
    # corpus.statsAuteur(rechercheAuteur)

    # corpus.sortDocumentByDate(5)
    # corpus.sortDocumentByTitre(5)
    # print(corpus)

    #Test du polymorphisme en créant des objets à la main pour le test
    corpusTest = Corpus("TestCorpus")

    redditDoc = RedditDocument(
        titre = "TitreTest",
        auteur = "AuteurTest",
        date = datetime(2025, 12, 4, 12, 00),
        url = "http://googl.com",
        texte = "BlablablaTest",
        nbCommentaires = 3,
    )

    arxivDoc = ArxivDocument(
        titre = "TitreTest",
        auteur = "AuteurTest, AuteurB, Machin",
        date = datetime(2025, 12, 4, 12, 00),
        url = "http://googl.com",
        texte = "BlablablaTest",
    )

    #Test d'affichage des classes enfants
    # print(f"====== Document Reddit: {redditDoc}")
    # print(f"====== Document Arxiv: {arxivDoc}")

    #Ajout de document selon le constructeur de Documents pour vérifier que les classes enfants le prennent bien en compte
    corpusTest.addDocument(redditDoc)
    corpusTest.addDocument(arxivDoc)
    # corpusTest.afficherDocuments()

    #Test du Singleton
    corpusSingleton1 = Corpus("PremierCorpus")
    # print(corpusSingleton1)
    corpusSingleton2 = Corpus("DeuxièmeCorpus")
    # print(corpusSingleton2)

    # print(corpusSingleton1 is corpusSingleton2)

    # Test de la fonction search - TD6
    # searchKeywords = input("--- Entrez un mot-clé à rechercher dans les documents: ").strip()
    # resultats = corpus.search(df, searchKeywords)

    # if not resultats:
    #     print("Aucun passage trouvé pour ce mot-clé !")
    # else: 
    #     print("Passage trouvé avec ce mot clé dans les documents: ")
    #     for i, passage in enumerate(resultats, 1):
    #         print(f"[{i}] {passage[3]}")

    # Test de la fonction concorde - TD6
    # concordeKeywords = input("--- (Concordancier) Entrez un mot-clé à rechercher dans les documents: ").strip()
    # df_concorde = corpus.concorde(df, concordeKeywords)

    # if df_concorde.empty:
    #     print("(Concordancier) Aucun passage trouvé pour ce mot-clé !")
    # else:
    #     print("(Concordancier) Passage trouvé avec ce mot clé dans les documents: ")
    #     for i, row in df_concorde.iterrows():
    #         print(f"[{i}] {row['contexteGauche']}- {row['mot']} -{row['contexteDroit']}")

    # Test d'affichages des stats - TD6
    # n = int(input("Combien de mots fréquents voulez-vous afficher ? ").strip())
    # vocabulaire, freq = corpus.stats(n)


    # Utilisation du moteur de recherche - TD7

    engine = SearchEngine(corpus)

    searchKeywords = input("(Moteur de recherche) Veuillez entrer une requete : ").strip()

    if searchKeywords:
        while True:
            nResult = input("Combien de document à retourner ?").strip()
            nResult = int(nResult)
            if nResult <= 0:
                print("Le nombre doit être positif :!")
            else:
                break
        
        resultats = engine.search(searchKeywords, nResults=nResult)
        if resultats.empty:
            print("Aucun documents trouvé")
        else:
            print(resultats[["score", "titre", "auteur", "date"]].to_string())

