import os
import pandas as pd
import kagglehub

# Localiser le dataset téléchargé
path = kagglehub.dataset_download("sid321axn/malicious-urls-dataset")
csv_file = [f for f in os.listdir(path) if f.endswith('.csv')][0]
df = pd.read_csv(os.path.join(path, csv_file))

print("=== 🔗 5 URL DE PHISHING RÉELLES ===")
phish_samples = df[df['type'] == 'phishing']['url'].head(5).tolist()
for url in phish_samples:
    print(url)

print("\n=== 🔒 5 URL LÉGITIMES RÉELLES ===")
benign_samples = df[df['type'] == 'benign']['url'].head(5).tolist()
for url in benign_samples:
    print(url)