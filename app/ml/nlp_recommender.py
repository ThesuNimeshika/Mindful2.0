import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('omw-1.4')

class NLPRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        self.item_texts = []
        self.item_ids = []
        self.item_matrix = None
        self.lemmatizer = WordNetLemmatizer()

    def _clean_text(self, text):
        text = text.lower()
        text = re.sub(r'[^a-z\s]', '', text)
        tokens = nltk.word_tokenize(text)
        lemmatized = [self.lemmatizer.lemmatize(token) for token in tokens]
        return ' '.join(lemmatized)

    def fit(self, items):
        if not items:
            return
        self.item_texts = [self._clean_text(a["text"]) for a in items]
        self.item_ids = [a["id"] for a in items]
        self.item_matrix = self.vectorizer.fit_transform(self.item_texts)

    def recommend(self, text, top_k=5):
        if self.item_matrix is None or self.item_matrix.shape[0] == 0 or not text:
            return []

        cleaned_text = self._clean_text(text)
        query_vec = self.vectorizer.transform([cleaned_text])
        sims = cosine_similarity(query_vec, self.item_matrix).flatten()

        top_indices = sims.argsort()[::-1][:top_k]
        return [
            {"id": self.item_ids[i], "score": float(sims[i])}
            for i in top_indices
        ]