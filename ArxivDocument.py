from Document import Document

class ArxivDocument(Document):
    def __init__(self, titre, auteur, date, url, texte):
        auteurs = auteur.split(', ')
        auteurPrincipal = auteurs[0]
        coAuteur = auteurs[1:] if len(auteurs) > 1 else []
        super().__init__(titre, auteurPrincipal, date, url, texte)
        self.coAuteur = coAuteur
        self.type = "Arxiv"

    def getCoAuteur(self):
        return self.coAuteur
    
    def setCoAuteur(self, coAuteur):
        self.coAuteur = coAuteur

    def getType(self):
        return self.type

    def __str__(self):
        return f"({self.getType()}) :{self.titre} - {self.auteur} / Co-auteurs : {self.coAuteur}"