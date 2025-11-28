import urllib.request
import xmltodict
import ssl
import certifi
import pandas as pd
import os
import re

from collections import Counter
from datetime import datetime
from Document import Document
from Author import Author
from DocumentFactory import DocumentFactory

class Corpus:

    _instance = None #Permet de stocker si l'instance est unique ou non (Singleton)

    #Appelé à la création d'une instance de la classe
    def __new__(cls, nom):
        if cls._instance is None:
            cls._instance = super(Corpus, cls).__new__(cls) #Créer une nouvelle instance
            cls._instance._initialised = False #Change la valeur pour préciser qu'une instance existe désormais
        return cls._instance

    def __init__(self, nom):
        if not self._initialised: #Vérifie qu'aucune instance n'existe
            self.nom = nom
            self.authors = {}
            self.id2doc = {}
            self.ndoc = 0
            self.naut = 0
            self._initialised = True #Prouve que la classe a bien été initialisée une fois

    #Fonction d'affichage des documents récupérés
    def afficherDocuments(self):
        print("======Documents instanciés======")
        for i, doc in self.id2doc.items():
            print(f"[{i}] {doc}")

    #Affichage des auteurs d'un documents
    def afficherAuteurs(self):
        print("======Auteurs instanciés======")
        for nomAuteur, auteur in self.authors.items():
            print(auteur)

    #Affichage des données spécifiques demandées dans une question
    def affichageDonnees(self, df):
        print("====== Taille du corpus : ", len(df))
        print(df)
        for document in df["texte"]:
            print(f"- Nombre de mots : {len(document.split(' '))}")
            print(f"- Nombre de phrases : {len(document.split(' '))}")

    #Affichage des statistiques par auteurs
    def statsAuteur(self, nomAuteur):
        if nomAuteur in self.authors:
            ndoc, tailleMoyenne = self.authors[nomAuteur].stats()
            print(f"====== Auteur : {nomAuteur}, Nombre de documents : {ndoc}, Taille moyenne (en mots) : {tailleMoyenne} ======")
        else:
            print("====== Auteur non trouvé ======")

    #Scrapping des données Reddit
    def loadReddit(self, reddit, keywords, limit = 100):
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
                nbCommentaires = submission.num_comments

                doc = DocumentFactory.createDocument("Reddit", titre, auteur, date, url, texte, nbCommentaires)

                self.addDocument(doc)

                docs.append(text)
                origine.append("Reddit")
        return docs, origine
    
    #Scrapping des données Arxiv
    def loadArxiv(self, keywords, limit = 100):
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
                auteur = ", ".join(a["name"] for a in (auteurData if isinstance(auteurData, list) else [auteurData])) #Amélioration de l'affichage des auteurs
                date = datetime.strptime(entry.get("published"), "%Y-%m-%dT%H:%M:%SZ")
                url = entry.get("id")
                texte = entry["summary"].replace('\n', ' ')

                doc = DocumentFactory.createDocument("Arxiv", titre, auteur, date, url, texte)

                self.addDocument(doc)

                docs.append(texte)
                origine.append("Arxiv")
        return docs, origine
    
    #Chargement d'un fichier .csv selon un mot clé
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

    def addDocument(self, doc):
        self.ndoc += 1
        self.id2doc[self.ndoc] = doc
        auteur = doc.auteur

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
    
    #Tri des documents par titre
    def sortDocumentByTitre(self, n):
        docTri = sorted(self.id2doc.values(), key=lambda d: d.titre)
        print(f"====== {n} documents triés par titre ======")
        for doc in docTri[:n]:
            print(doc)

    #Tri des documents par date
    def sortDocumentByDate(self, n):
        docTri = sorted(self.id2doc.values(), key=lambda d: d.date)
        print(f"====== {n} documents triés par date ======")
        for doc in docTri[:n]:
            print(doc)

    #Sauvegarde des données dans un .csv
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

    #Récupération des données d'un .csv
    def load(self, filename):
        if not os.path.isfile(filename):
            print("Erreur, fichier introuvable")
            return

        df = pd.read_csv(filename, sep="\t")
        df["date"] = pd.to_datetime(df["date"])

        for _, row in df.iterrows():
            doc = Document(
                row["titre"],
                row["auteur"],
                row["date"],
                row["url"],
                row["texte"]
            )
            
            self.addDocument(doc)

    # Fonction de recherche à partir d'un mot, cela retourne le mot et son contexte
    def search(self, df, keyword):
        df = df[df["texte"].str.len() >= 20] #Supprime les documents qui ont moins de 20 caractères
        if not hasattr(self, "_totalText"):
            self._totalText = " ".join(df["texte"]) #Créer une chaine de caractères avec l'ensemble des documents séparés pour un espace
        
        motif = re.compile(keyword, re.IGNORECASE)
        matches = motif.finditer(self._totalText)
        resultat = []

        for m in matches:
            start = max(m.start() - 20, 0) #Prendre les 20 premiers caractères
            end = min(m.end() + 20, len(self._totalText))
            passage = self._totalText[start:end]
            resultat.append((m.group(), start, end, passage))
        
        return resultat
    
    # Fonction de création d'un concordancier et retourne le contexte
    def concorde(self, df, keyword):
        if not hasattr(self, "_totalText"):
            df = df[df["texte"].str.len() >= 20]
            self._totalText = " ".join(df["texte"])

        motif = re.compile(keyword, re.IGNORECASE)
        matches = motif.finditer(self._totalText)
        resultat = []
        for m in matches:
            start = max(m.start() - 20, 0)
            end = min(m.end() + 20, len(self._totalText))
            contexteGauche = self._totalText[start:m.start()]
            motTrouve = m.group()
            contexteDroit = self._totalText[m.end():end]
            resultat.append({
                "contexteGauche": contexteGauche,
                "mot": motTrouve,
                "contexteDroit": contexteDroit
            })
        
        df_concorde = pd.DataFrame(resultat)
        return df_concorde
    
    # Nettoyage du texte à l'aide de regex
    def nettoyer_texte(self, texte):
        texte = texte.lower()
        texte = texte.replace('\n', ' ')
        texte = re.sub(r'[^\w\s]', '', texte)
        texte = re.sub(r'\d+', '', texte)
        return texte.strip()
    
    # Récupération de chaque mot individuellement, en splittant sur des caractères spécifiques
    def stats(self, n):
        setVocabulaire = set()
        compteurMot = Counter()
        compteurDoc = Counter()

        for doc in self.id2doc.values():
            textClean = self.nettoyer_texte(doc.texte)
            mots = re.split(r'[^a-zA-Z]+', textClean)
            mots = list(filter(None, mots))
            setVocabulaire.update(mots)
            compteurMot.update(mots)
            motUniquesDoc = set(mots)
            compteurDoc.update(motUniquesDoc)

        print(f"Nombre de mots différents dans le corpus: {len(setVocabulaire)}")

        freq = pd.DataFrame(compteurMot.items(), columns=['mot', 'frequence'])
        freq['doc_frequency'] = freq['mot'].apply(lambda m: compteurDoc[m])
        freq = freq.sort_values(by='frequence', ascending=False)

        print(f"Top {n} des mots les plus présents:\n {freq.head(n)}")

        return setVocabulaire, freq
    
    #Amélioration de l'affichage du print d'un objet de classe Corpus
    def __repr__(self):
        return (f"Corpus '{self.nom}' :\n - {self.ndoc} documents\n - {self.naut} auteurs")