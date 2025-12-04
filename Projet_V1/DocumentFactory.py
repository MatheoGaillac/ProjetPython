from Document import Document
from ArxivDocument import ArxivDocument
from RedditDocument import RedditDocument

class DocumentFactory:
    def createDocument(typeDoc, titre, auteur, date, url, texte, nbCommentaires =  None):
        if typeDoc == "Reddit":
            if nbCommentaires is None:
                print("Un document Reddit a besoin d'un nombre de commentaires !")
            else:
                return RedditDocument(titre, auteur, date, url, texte, nbCommentaires)
        elif typeDoc == "Arxiv":
            return ArxivDocument(titre, auteur, date, url, texte)
        else:
            return Document(titre, auteur, date, url, texte)