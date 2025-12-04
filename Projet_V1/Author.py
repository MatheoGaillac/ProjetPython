class Author:
    def __init__(self, name):
        self.name = name
        self.ndoc = 0
        self.production = {}

    def add(self, idDoc, document):
        if idDoc not in self.production:
            self.production[idDoc] = document
            self.ndoc += 1

    def stats(self):
        if self.ndoc == 0:
            return self.ndoc
        totalMot = sum(len(doc.texte.split()) for doc in self.production.values())
        tailleMoyenne = totalMot/self.ndoc
        return self.ndoc, tailleMoyenne
    
    def __str__(self):
        return f"- {self.name} ({self.ndoc} documents)"