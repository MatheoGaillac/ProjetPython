from Document import Document

class RedditDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, nbCommentaires):
        super().__init__(titre, auteur, date, url, texte)
        self.nbCommentaires = nbCommentaires
        self.type = "Reddit"

    def getNbCommentaires(self):
        return self.nbCommentaires
    
    def setNbCommentaires(self, nb):
        self.nbCommentaires = nb

    def getType(self):
        return self.type

    def __str__(self):
        return f"({self.getType()}) : {self.titre} - {self.auteur} / Commentaires : {self.nbCommentaires}"