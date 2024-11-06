# ml_models/scripts/train_model.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import pickle
import os

def load_processed_data():
    """Load preprocessed training data."""
    X = pd.read_csv('ml_models/data/processed/X_train.csv')
    y = pd.read_csv('ml_models/data/processed/y_train.csv')
    return X, y

def train_logistic_regression(X_train, y_train):
    """Train a Logistic Regression model."""
    lr = LogisticRegression()
    lr.fit(X_train, y_train)
    return lr

def train_random_forest(X_train, y_train):
    """Train a Random Forest model."""
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    return rf

def save_model(model, model_name):
    """Save the trained model to a file."""
    os.makedirs('ml_models/models', exist_ok=True)
    with open(f'ml_models/models/{model_name}.pkl', 'wb') as f:
        pickle.dump(model, f)
    print(f"{model_name} model saved successfully.")

def main():
    # Load data
    X, y = load_processed_data()

    # Split data into training and validation sets
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train Logistic Regression
    lr_model = train_logistic_regression(X_train, y_train)
    save_model(lr_model, 'logistic_regression')

    # Train Random Forest
    rf_model = train_random_forest(X_train, y_train)
    save_model(rf_model, 'random_forest')

    # Evaluate models
    models = {
        'Logistic Regression': lr_model,
        'Random Forest': rf_model
    }

    performance_metrics = []

    for name, model in models.items():
        y_val_pred = model.predict(X_val)
        report = classification_report(y_val, y_val_pred, output_dict=True)
        accuracy = report['accuracy'] * 100
        print(f"\n{name} Validation Report:")
        print(classification_report(y_val, y_val_pred))

        # Save performance metrics
        performance_metrics.append({
            'model': name,
            'accuracy': round(accuracy, 2)
        })

    # Save performance metrics to a CSV file
    performance_df = pd.DataFrame(performance_metrics)
    performance_df.to_csv('ml_models/data/processed/performance_metrics.csv', index=False)
    print("Model training and evaluation completed.")

if __name__ == "__main__":
    main()
