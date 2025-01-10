import os
import json
import spacy
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score

# Load SpaCy's large English model
nlp = spacy.load("en_core_web_lg")
# Load training data from JSON file
with open('classification/training-data.json', 'r') as f:
    training_data = json.load(f)
    print(training_data)

# Preprocess text: Lemmatize and remove stop words
def preprocess_text(text):
    doc = nlp(text.lower())
    return " ".join([token.lemma_ for token in doc if not token.is_stop])

# Prepare the training data
X = [preprocess_text(query['query']) for query in training_data]
y = [query['intent'] for query in training_data]

# Split the data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Convert text data into TF-IDF features
vectorizer = TfidfVectorizer()
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Train a Naive Bayes classifier
classifier = MultinomialNB()
classifier.fit(X_train_tfidf, y_train)

# Predict on the test set and evaluate accuracy
y_pred = classifier.predict(X_test_tfidf)
print("Accuracy:", accuracy_score(y_test, y_pred))

# Function to predict the intent of a given query
def predict_intent(user_query):
    # Preprocess the input query
    processed_query = preprocess_text(user_query)
    # Convert to TF-IDF features
    query_tfidf = vectorizer.transform([processed_query])
    # Predict the intent
    return classifier.predict(query_tfidf)[0]

# Example usage
# print("Predicted Intent:", predict_intent("Why was my insurance premium higher this year?"))  # Expected: 'insurance_query'
# print("Predicted Intent:", predict_intent("Can you recommend a good health insurance plan?"))  # Expected: 'recommendation'





