class Document:
    def __init__(self, titre, auteur, date, url, texte):
        self.titre = titre
        self.auteur = auteur
        self.date = date
        self.url = url
        self.texte = texte

    def afficherDoc(self):
        return f"Titre: {self.titre}, Auteur: {self.auteur}, Date: {self.date}, URL: {self.url}, Texte: {self.texte}"
    
    def __str__(self):
        return f"{self.titre} - {self.auteur} ({self.date})"
    
# doc = Document("TitreA", "AuteurA", "04/12/2025", "http://google.com", "Blablablablablabla")
# print(doc.afficherDoc())
# print(doc)