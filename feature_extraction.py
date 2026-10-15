import re
import urllib.parse
import tldextract

# Liste de mots-clés souvent utilisés dans les attaques de phishing/smishing
SUSPICIOUS_KEYWORDS = [
    'login', 'verify', 'update', 'account', 'banking', 'secure',
    'confirm', 'password', 'validation', 'service', 'free', 'claim'
]

def extract_features(url):
    """
    Analyse une URL et extrait des indicateurs de risque numériques.
    """
    features = {}

    # 1. Longueur de l'URL (les URL frauduleuses sont souvent plus longues)
    features['url_length'] = len(url)

    # 2. Présence d'une adresse IP à la place d'un nom de domaine
    ip_pattern = r'(([01]?\d\d?|2[0-4]\d|25[0-5])\.){3}([01]?\d\d?|2[0-4]\d|25[0-5])'
    features['has_ip'] = 1 if re.search(ip_pattern, url) else 0

    # 3. Compte du nombre de caractéristiques/caractères fréquents dans le phishing
    features['count_at'] = url.count('@')
    features['count_hyphen'] = url.count('-')
    features['count_slash'] = url.count('/')
    features['count_question'] = url.count('?')
    features['count_equal'] = url.count('=')
    features['count_dot'] = url.count('.')

    # 4. Analyse du nom de domaine avec tldextract
    extracted = tldextract.extract(url)
    domain = extracted.domain
    subdomain = extracted.subdomain

    features['domain_length'] = len(domain)
    features['count_subdomains'] = len(subdomain.split('.')) if subdomain else 0

    # 5. Utilisation du protocole HTTPS
    features['is_https'] = 1 if url.startswith('https://') else 0

    # 6. Présence de mots-clés suspects dans l'URL
    url_lower = url.lower()
    features['keyword_count'] = sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in url_lower)

    return features

# Petit test rapide si vous exécutez ce fichier directement
if __name__ == "__main__":
    test_url = "http://secure-login.bank-update.com/verify/account?id=123"
    result = extract_features(test_url)
    print("Indicateurs calculés pour l'URL de test :")
    for key, value in result.items():
        print(f"  {key}: {value}")