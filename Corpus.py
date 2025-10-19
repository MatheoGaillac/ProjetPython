import urllib.request
import xmltodict
import ssl
import certifi
import pandas as pd
import os

from datetime import datetime
from Document import Document
from Author import Author

class Corpus:
    def __init__(self, nom):
        self.nom = nom
        self.authors = {}
        self.id2doc = {}
        self.ndoc = 0
        self.naut = 0

    def afficherDocuments(self):
        print("Documents instanciés")
        for i, doc in self.id2doc.items():
            print(f"[{i}] {doc}")

    def afficherAuteurs(self):
        print("Auteurs instanciés")
        for nomAuteur, auteur in self.authors.items():
            print(auteur)

    def affichageDonnees(self, df):
        print("Taille du corpus : ", len(df))
        for document in df["texte"]:
            print("Nombre de mots : ", len(document.split(" ")))
            print("Nombre de phrases : ", len(document.split(".")))

    def statsAuteur(self, nomAuteur):
        if nomAuteur in self.authors:
            ndoc, tailleMoyenne = self.authors[nomAuteur].stats()
            print(f"Auteur : {nomAuteur}, Nombre de documents : {ndoc}, Taille moyenne (en mots) : {tailleMoyenne}")
        else:
            print("Auteur non trouvé")

    def loadReddit(self, reddit, keywords, limit = 10):
        docs = []
        origine = []

        for submission in reddit.subreddit("all").search(keywords, limit = limit) : 
            text = submission.selftext.replace('\n', ' ')
            if text:
                titre = submission.title
                auteur = submission.author
                date = datetime.fromtimestamp(submission.created_utc)
                url = submission.url
                texte = text

                self.addDocument(titre, auteur, date, url, texte)
                docs.append(text)
                origine.append("Reddit")
        return docs, origine
    
    def loadArxiv(self, keywords, limit = 10):
        docs = []
        origine = []
        encodedKeywords = urllib.parse.quote(keywords) #Encodage du mot clé pour la requête Arxiv qui passe par un url

        context = ssl.create_default_context(cafile=certifi.where()) #Gestion du certificat, sans ça il y a une erreur
        url = f"http://export.arxiv.org/api/query?search_query=all:{encodedKeywords}&start=0&max_results={limit}" 
        data = urllib.request.urlopen(url, context=context)
        data = data.read().decode('utf-8')
        data = xmltodict.parse(data)

        if (data["feed"].get("entry")): #Vérifie qu'il y a bien des documents trouvés, pour éviter les erreurs
            entries = data["feed"]["entry"]

            for entry in entries:
                titre = entry.get("title")
                auteurData = entry.get("author")
                auteur = ", ".join(a["name"] for a in (auteurData if isinstance(auteurData, list) else [auteurData]))
                date = datetime.strptime(entry.get("published"), "%Y-%m-%dT%H:%M:%SZ")
                url = entry.get("id")
                texte = entry["summary"].replace('\n', ' ')

                self.addDocument(titre, auteur, date, url, texte)

                docs.append(texte)
                origine.append("Arxiv")
        return docs, origine
    
    def loadCorpus(self, reddit, keywords):
        if os.path.isfile(f'{keywords}.csv'):
            df = pd.read_csv(f'{keywords}.csv', sep='\t')
        else:
            docsReddit, origineReddit = self.loadReddit(reddit, keywords)
            docsArxiv, origineArxiv = self.loadArxiv(keywords)

            docs = docsReddit + docsArxiv
            origine = origineReddit + origineArxiv
            df = self.createDataframe(docs, origine)
            df.to_csv(f'{keywords}.csv', index=False, sep='\t')
        return df

    def addDocument(self, titre, auteur, date, url, texte):
        self.ndoc += 1
        doc = Document(titre, auteur, date, url, texte)
        self.id2doc[self.ndoc] = doc

        if auteur not in self.authors:
            self.authors[auteur] = Author(auteur)
            self.naut += 1
        self.authors[auteur].add(self.ndoc, doc)

    def createDataframe(self, docs, origine):
        df = pd.DataFrame({
            'id': range(1, len(docs) + 1),
            'texte': docs,
            'origine': origine
        })
        return df
    
    def sortDocumentByTitre(self, n):
        docTri = sorted(self.id2doc.values(), key=lambda d: d.titre)
        print(f"{n} documents triés par titre")
        for doc in docTri[:n]:
            print(doc)

    def sortDocumentByDate(self, n):
        docTri = sorted(self.id2doc.values(), key=lambda d: d.date)
        print(f"{n} documents triés par date")
        for doc in docTri[:n]:
            print(doc)

    def save(self, filename):
        data = []
        for docId, doc in self.id2doc.items():
            data.append({
                "id": docId,
                "titre": doc.titre,
                "auteur": doc.auteur,
                "date": doc.date,
                "url": doc.url,
                "texte": doc.texte
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, sep='\t')

    def load(self, filename):
        if not os.path.isfile(filename):
            print("Erreur, fichier introuvable")
            return

        df = pd.read_csv(filename, sep="\t")
        df["date"] = pd.to_datetime(df["date"])

        for _, row in df.iterrows():
            self.addDocument(
                row["titre"],
                row["auteur"],
                row["date"],
                row["url"],
                row["texte"]
            )

    def __repr__(self):
        return (f"Corpus '{self.nom}' :\n - {self.ndoc} documents\n - {self.naut} auteurs")