import os
import re
import math
import urllib.parse
import pandas as pd
import numpy as np
import requests
import tldextract
from sklearn.model_selection import train_test_split

USER_AGENT = "Faustine_TCHOROPA_Smishing_Detector_Academic_Project/1.0"
HEADERS = {'User-Agent': USER_AGENT}
DATASET_DIR = "url_dataset"

SUSPICIOUS_KEYWORDS = [
    'login', 'verify', 'update', 'account', 'banking', 'secure', 'confirm',
    'connexion', 'securite', 'compte', 'verification', 'banque', 'colissimo',
    'livraison', 'ameli', 'impot', 'pass', 'password', 'service', 'free', 'gift',
    'winner', 'gagner', 'mobilemoney', 'momo', 'orange', 'moov', 'mtn','24 h','vite',
    'bloqué','suspendu','alerte de sécurité','Blocked','mise à jour obligatoire',
    'immédiatement','dernier avis','PIN','Security alert','Refund','Payment','Prize','Free',
    'au plus vite','Immediately','confirm','validate','click here','act now','update now',
    'remboursement','paiement','transaction','gratuit','cadeau','valider','confirmer',
    'gagnant','mot de passe','mettez à jour maintenant','cliquez ici','verrouillé','urgent'
]

SUSPICIOUS_TLDS = {'xyz', 'top', 'online', 'site', 'live', 'club', 'info', 'work', 'cn', 'tk', 'ml', 'ga', 'cf', 'gq'}
SHORTENERS = {'bit.ly', 'goo.gl', 'tinyurl.com', 'ow.ly', 't.co', 'is.gd', 'buff.ly', 'adf.ly', 'bit.do'}


def calculate_entropy(text):
    if not text:
        return 0.0
    prob = [float(text.count(c)) / len(text) for c in dict.fromkeys(list(text))]
    return - sum([p * math.log(p, 2) for p in prob])


def extract_24_features(url):
    url_str = str(url).strip()
    parsed = urllib.parse.urlparse(url_str)

    ext = tldextract.extract(url_str)
    domain = ext.domain
    subdomain = ext.subdomain
    tld = ext.suffix
    hostname = parsed.netloc or parsed.path.split('/')[0]

    url_length = len(url_str)
    domain_length = len(domain)
    num_dots = url_str.count('.')
    num_hyphens = url_str.count('-')
    num_underscores = url_str.count('_')
    num_slash = url_str.count('/')
    num_question = url_str.count('?')
    num_equal = url_str.count('=')
    num_at = url_str.count('@')
    num_digits = sum(c.isdigit() for c in url_str)
    digit_ratio = num_digits / url_length if url_length > 0 else 0.0

    has_ip = 1 if re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', hostname) else 0
    is_https = 1 if parsed.scheme.lower() == 'https' else 0
    num_subdomains = len(subdomain.split('.')) if subdomain else 0
    is_punycode = 1 if 'xn--' in url_str.lower() else 0

    has_custom_port = 1 if parsed.port and parsed.port not in [80, 443] else 0
    is_shortener = 1 if any(short in hostname.lower() for short in SHORTENERS) else 0
    is_suspicious_tld = 1 if tld.lower() in SUSPICIOUS_TLDS else 0

    url_lower = url_str.lower()
    keyword_count = sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in url_lower)
    subdomain_keyword_count = sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in subdomain.lower()) if subdomain else 0

    domain_entropy = calculate_entropy(domain)
    subdomain_entropy = calculate_entropy(subdomain) if subdomain else 0.0

    return {
        'url_length': url_length,
        'domain_length': domain_length,
        'num_dots': num_dots,
        'num_hyphens': num_hyphens,
        'num_underscores': num_underscores,
        'num_slash': num_slash,
        'num_question': num_question,
        'num_equal': num_equal,
        'num_at': num_at,
        'num_digits': num_digits,
        'digit_ratio': digit_ratio,
        'has_ip': has_ip,
        'is_https': is_https,
        'num_subdomains': num_subdomains,
        'is_punycode': is_punycode,
        'has_custom_port': has_custom_port,
        'is_shortener': is_shortener,
        'is_suspicious_tld': is_suspicious_tld,
        'keyword_count': keyword_count,
        'subdomain_keyword_count': subdomain_keyword_count,
        'domain_entropy': domain_entropy,
        'subdomain_entropy': subdomain_entropy,
        'has_http_in_path': 1 if 'http' in parsed.path.lower() else 0,
        'has_double_slash': 1 if '//' in parsed.path else 0
    }


def main():
    os.makedirs(DATASET_DIR, exist_ok=True)
    print("🚀 Génération d'un dataset parfaitement équilibré...")

    # Phishing
    try:
        req = requests.get("https://data.phishtank.com/data/online-valid.csv", headers=HEADERS, timeout=15)
        with open("url_dataset/phishtank_raw.csv", 'wb') as f:
            f.write(req.content)
        df_phish = pd.read_csv("url_dataset/phishtank_raw.csv")
        phish_urls = df_phish['url'].dropna().astype(str).tolist()
    except Exception:
        phish_urls = [
                         "http://secure-login.bank-update.com/verify/account?id=123",
                         "http://claim-free-gift-card.online-service.net/login",
                         "http://192.168.1.1/update-password-now/banking",
                         "http://verify-account-paypal-security.com/confirm",
                         "http://free-prize-winner-claim.xyz/service"
                     ] * 500

    # Légitime (Base Tranco / Top sites)
    top_domains = [
        "google.com", "youtube.com", "facebook.com", "baidu.com", "wikipedia.org",
        "yahoo.com", "amazon.com", "github.com", "twitter.com", "instagram.com",
        "linkedin.com", "netflix.com", "microsoft.com", "apple.com", "bing.com",
        "orange.bj", "mtn.bj", "gouv.bj", "moov-africa.bj", "banque-atlantique.net"
    ]

    legit_urls = []
    paths = ["", "/login", "/home", "/about", "/service", "/account", "/fr/index.html"]
    for dom in top_domains * 100:
        proto = "https"
        sub = "www." if np.random.rand() > 0.3 else ""
        path = np.random.choice(paths)
        legit_urls.append(f"{proto}://{sub}{dom}{path}")

    # Équilibrage exact (2000 de chaque pour être ultra rapide et précis)
    n_samples = min(2000, len(phish_urls), len(legit_urls))

    phish_sel = list(np.random.choice(phish_urls, size=n_samples, replace=False))
    legit_sel = list(np.random.choice(legit_urls, size=n_samples, replace=False))

    df_p = pd.DataFrame({'url': phish_sel, 'label': 1})
    df_l = pd.DataFrame({'url': legit_sel, 'label': 0})

    df_all = pd.concat([df_p, df_l], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)

    print(f"📊 Dataset créé : {len(df_all)} URL au total ({n_samples} Légitimes / {n_samples} Phishing)")

    # Features
    features_list = [extract_24_features(u) for u in df_all['url']]
    df_feat = pd.DataFrame(features_list)
    df_clean = pd.concat([df_all[['url', 'label']], df_feat], axis=1)

    # Sauvegarde
    train_df, test_df = train_test_split(df_clean, test_size=0.2, random_state=42)
    train_df.to_csv(os.path.join(DATASET_DIR, "train.csv"), index=False)
    test_df.to_csv(os.path.join(DATASET_DIR, "test.csv"), index=False)

    print("✅ Fichiers train.csv et test.csv réénéquilibrés avec succès !")


if __name__ == "__main__":
    main()