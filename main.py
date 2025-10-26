import praw
import os
from Corpus import Corpus
from RedditDocument import RedditDocument
from ArxivDocument import ArxivDocument
from datetime import datetime

if __name__ == '__main__' : 
    reddit = praw.Reddit(client_id='CvBa0giChE03eJkVvvb_1A', client_secret='hIaWPpSE821dHejacJKpeHJwr_g3SQ', user_agent='ProjetPythonWeb')

    keywords = input("Écrivez votre recherche : ").strip()
    corpus = Corpus(keywords)
    filename = f"{keywords}_corpus.csv"

    df = corpus.loadCorpus(reddit, keywords)

    if os.path.isfile(filename):
        corpus.load(filename)
    else:
        corpus.save(filename)

    # corpus.afficherDocuments()
    # corpus.afficherAuteurs()
    # corpus.affichageDonnees(df)

    # print(corpus)

    # rechercheAuteur = input("Entrer le nom d'un auteur : ").strip()
    # corpus.statsAuteur(rechercheAuteur)

    # corpus.sortDocumentByDate(5)
    # corpus.sortDocumentByTitre(5)
    # print(corpus)

    # Test du polymorphisme
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

    corpusTest.addDocument(redditDoc.titre, redditDoc.auteur, redditDoc.date, redditDoc.url, redditDoc.texte)
    corpusTest.addDocument(arxivDoc.titre, arxivDoc.auteur, arxivDoc.date, arxivDoc.url, arxivDoc.texte)
    corpusTest.afficherDocuments()

    df = df[df["texte"].str.len() >= 20] #Supprime les documents qui ont moins de 20 caractères
    totalText = " ".join(df["texte"]) #Créer une chaine de caractères avec l'ensemble des documents séparés pour un espace