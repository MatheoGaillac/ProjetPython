import re
import scipy.sparse as sp
import numpy as np
import pandas as pd
from collections import Counter

class SearchEngine:
    def __init__(self, corpus):
        self.corpus = corpus

        self.vocab = self.buildVocabulaire()
        self.mat_TF = self.buildTFMatrice(self.vocab)
        self.vocab = self.updateStatsVocab(self.vocab, self.mat_TF)
        self.mat_TFxIDF = self.buildTFxIDFMatrice(self.vocab, self.mat_TF)
        self.doc_norms = sp.linalg.norm(self.mat_TFxIDF, axis=1)

    #Construction du dictionnaire "vocab"
    def buildVocabulaire(self):
        setVocabulaire = set()
        compteur = Counter()

        for doc in self.corpus.id2doc.values():
            textClean = self.corpus.nettoyer_texte(doc.texte)
            mots = re.split(r'[^a-zA-Z]+', textClean)
            mots = list(filter(None, mots))
            setVocabulaire.update(mots)
            compteur.update(mots)

        sortedMots = sorted(list(setVocabulaire))
        vocab = {}

        for i, mot in enumerate(sortedMots):
            vocab[mot] = {
                "id": i,
                "total": compteur[mot]
            }

        return vocab
    
    def buildTFMatrice(self, vocab):
        numDocs = self.corpus.ndoc
        numWords = len(vocab)

        data = []
        row = []
        col = []

        for idDoc, doc in self.corpus.id2doc.items():
            indexDoc = idDoc - 1
            textClean = self.corpus.nettoyer_texte(doc.texte)
            mots = re.split(r'[^a-zA-Z]+', textClean)
            mots = list(filter(None, mots))

            wordsDocCount = Counter(mots)
            for mot, tf in wordsDocCount.items():
                if mot in vocab:
                    indexCol = vocab[mot]["id"]
                    data.append(tf)
                    row.append(indexDoc)
                    col.append(indexCol)
        
        mat_TF = sp.csr_matrix((data, (row, col)), shape=(numDocs, numWords))
        return mat_TF
    
    def updateStatsVocab(self, vocab, mat_TF):
        totalOccurences = mat_TF.sum(axis = 0).A1 #Somme sur la colonne des mots
        frequencesDocs = mat_TF.getnnz(axis = 0) #Nombre de documents non nuls

        for mot, data in vocab.items():
            indexCol = data["id"]
            data["occurenceTotal"] = int(totalOccurences[indexCol])
            data["frequenceDoc"] = int(frequencesDocs[indexCol])

        return vocab
    
    def buildTFxIDFMatrice(self, vocab, mat_TF):
        N = self.corpus.ndoc
        numWords = len(vocab)

        dfVector = np.zeros(numWords)
        for mot, data in vocab.items():
            dfVector[data["id"]] = data["frequenceDoc"]
        
        idfVector = np.log(N / dfVector)
        idfMatrice = sp.diags(idfVector, offsets = 0, format="csr")
        mat_tfidf = mat_TF.dot(idfMatrice)

        return mat_tfidf
    
    def search(self, keywords, nResults = 10):
        N = self.corpus.ndoc
        numWords = len(self.vocab)

        textClean = self.corpus.nettoyer_texte(keywords)
        mots = re.split(r'[^a-zA-Z]+', textClean)
        mots = list(filter(None, mots))

        if not mots:
            return pd.DataFrame(columns=["id", "titre", "auteur", "date", "url", "score"])

        tfCounts = Counter(mots)
        tfIDFVector = np.zeros(numWords)
        tfIdfSum = 0

        idfVector = np.zeros(numWords)
        for data in self.vocab.values():
            if data["frequenceDoc"] > 0:
                idfVector[data["id"]] = np.log(N / data["frequenceDoc"])

        for mot, tf in tfCounts.items():
            if mot in self.vocab:
                indexCol = self.vocab[mot]["id"]
                idf = idfVector[indexCol]
                tfIdf_score = tf * idf
                tfIDFVector[indexCol] = tfIdf_score
                tfIdfSum += tfIdf_score ** 2
        
        norm = np.sqrt(tfIdfSum)

        if norm == 0:
            return pd.DataFrame(columns=["id", "titre", "auteur", "date", "url", "score"])

        produitScalaire = self.mat_TFxIDF.dot(tfIDFVector)
        non_zero_norms = np.where(self.doc_norms > 0, self.doc_norms, 1e-10) 
        cos_similarity = produitScalaire / (norm * non_zero_norms)
        ranked_indices = np.argsort(cos_similarity)[::-1]
        
        results = []
        for doc_index in ranked_indices:
            score = cos_similarity[doc_index]
            
            if score <= 0 or len(results) >= nResults:
                 break

            doc_id = doc_index + 1
            document = self.corpus.id2doc.get(doc_id)
            
            if document:
                results.append({
                    "score": score,
                    "titre": document.titre,
                    "auteur": document.auteur,
                    "date": document.date,
                    "url": document.url,
                })

        df_results = pd.DataFrame(results)
        df_results['score'] = df_results['score'].round(4)
        
        return df_results