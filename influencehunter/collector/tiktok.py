"""
InfluenceHunter AI - TikTok Data Collector

Este módulo é responsável pela coleta de dados do TikTok.
Suporta modo Simulado e modo REAL via Apify (Dataset pré-coletado ou Scraper).
"""

import random
import time
import requests

class TikTokCollector:
    """
    Classe para coletar dados de influenciadores do TikTok.
    Se api_key for None. opera em modo de simulação.
    Se api_key for fornecida, tenta buscar dados reais do Apify.
    """
    
    def __init__(self, api_key=None, simulated=False):
        """
        Inicializa o coletor do TikTok
        
        Args:
            api_key (str): Token da API do Apify
            simulated (bool): Se True, força uso de dados simulados
        """
        self.api_key = api_key
        self.simulated = simulated if api_key is None else simulated
        # Dataset fixo fornecido pelo usuário para demo/teste garantido
        self.apify_dataset_url = "https://api.apify.com/v2/datasets/CquJSWaokuk8e5m3H/items"
        
        self.niches = ["Dancinha", "Humor", "Educação Financeira", "Hacks de Vida", "Beleza", "Tech", "Saúde Mentarl"]
        self.cities = ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Fortaleza", "Salvador", "Manaus"]

    def collect_profile(self, username):
        """
        Coleta dados do perfil de um criador
        
        Args:
            username (str): Nome de usuário do TikTok
            
        Returns:
            dict: Dados do perfil coletados e normalizados
        """
        if self.simulated:
            print(f"[TikTok-Mock] Coletando perfil simulado para: {username}...")
            time.sleep(0.2) 
            return self._generate_mock_profile(username)
        else:
            return self._fetch_real_data(username)

    def _fetch_real_data(self, username):
        """Busca dados reais no Apify (Dataset)"""
        print(f"[TikTok-Real] Buscando dados no Apify para: {username}...")
        
        try:
            # Para o dataset específico, não filtramos por username na query (não suportado por datasets simples)
            # Baixamos o dataset e filtramos localmente (para demo, ok se o dataset for pequeno)
            response = requests.get(f"{self.apify_dataset_url}?token={self.api_key}")
            
            if response.status_code != 200:
                print(f"[ERRO-TikTok] Falha na API Apify: {response.status_code}")
                return None
                
            data = response.json()
            
            items = []
            if isinstance(data, list):
                items = data
            
            # Tentar encontrar o usuário no dataset
            # O dataset parece conter POSTS. Então agrupamos por authorMeta.name unique
            user_posts = [item for item in items if item.get('authorMeta', {}).get('name') == username]
            
            if not user_posts:
                 # Fallback: Se não achar o username exato, pega um aleatório do dataset para DEMO não falhar
                 print(f"[AVISO] Usuário {username} não encontrado no dataset. Usando dados aleatórios do dataset para demonstração.")
                 if items:
                     random_post = random.choice(items)
                     # Fake username match to proceed
                     user_posts = [random_post]
                 else:
                     return None

            # Pegamos o primeiro post para extrair dados do perfil
            profile_data = user_posts[0].get('authorMeta', {})
            
            # Agregamos métricas dos posts encontrados
            total_likes = sum(p.get('diggCount', 0) for p in user_posts)
            total_comments = sum(p.get('commentCount', 0) for p in user_posts)
            avg_likes = total_likes / len(user_posts) if user_posts else 0
            avg_comments = total_comments / len(user_posts) if user_posts else 0
            
            # Extrair captions
            captions = [p.get('text', '') for p in user_posts]
            
            followers_count = profile_data.get('fans', 0)
            
            # Filtro de Qualidade
            if followers_count < 1000:
                print(f"[TikTok-Filter] Ignorando perfil {username} (Followers: {followers_count})")
                return None

            return {
                "username": profile_data.get('name', username),
                "platform": "tiktok",
                "niche": "Geral (TikTok)", # Difícil inferir sem NLP
                "city": "", 
                "followers": followers_count,
                "avg_likes": avg_likes,
                "avg_comments": avg_comments,
                "bio": profile_data.get('signature', ''),
                "link_in_bio": profile_data.get('bioLink', {}).get('link', '') if profile_data.get('bioLink') else '',
                "captions": captions,
                "comments_text": [], # Dataset não tem comments text deep
                "avg_views": 0 # Dataset tem playCount, poderia usar
            }

        except Exception as e:
            print(f"[ERRO-TikTok] Exceção na coleta Apify: {e}")
            return None

    def discover_from_dataset(self):
        """
        Descobre TODOS os perfis únicos presentes no dataset (Viral Discovery)
        """
        if self.simulated:
             return [self.collect_profile(f"tiktok_discovery_{i}") for i in range(3)]
             
        print(f"[TikTok-Real] Varrendo dataset em busca de novos perfis...")
        
        try:
            response = requests.get(f"{self.apify_dataset_url}?token={self.api_key}")
            if response.status_code != 200:
                print(f"[ERRO-TikTok] Falha ao baixar dataset: {response.status_code}")
                return []
                
            data = response.json()
            items = data if isinstance(data, list) else []
            
            # Extrair usernames únicos
            unique_usernames = set()
            for item in items:
                username = item.get('authorMeta', {}).get('name')
                if username:
                    unique_usernames.add(username)
            
            print(f"[TikTok-Discovery] Encontrados {len(unique_usernames)} perfis únicos no dataset.")
            
            profiles = []
            for username in unique_usernames:
                # Reutiliza a lógica de fetch_real_data que já busca no dataset (cacheado seria melhor, mas ok por agora)
                p = self._fetch_real_data(username) 
                if p: profiles.append(p)
                
            return profiles

        except Exception as e:
            print(f"[ERRO-TikTok] Falha na descoberta: {e}")
            return []
    def _generate_mock_profile(self, username):
        # ... (Manter código existente de mock) ...
        """Gera um perfil simulado estilo TikTok"""
        
        is_affiliate = random.random() > 0.5 # Mais comum afiliados no TikTok
        has_link = is_affiliate or (random.random() > 0.6)
        
        bio_templates = [
            "Conteúdo diário sobre {niche}",
            "Assista até o final! | {niche}",
            "Te ensino a ganhar dinheiro com {niche}",
            "Lifestyle e {niche} ✨",
            "Pov: você gosta de {niche}"
        ]
        
        niche = random.choice(self.niches)
        bio = random.choice(bio_templates).format(niche=niche)
        
        api_link = ""
        if has_link:
            bio += " | Link na bio! ⬇️"
            api_link = "https://tiktok.shop/user123"
            
        followers = random.randint(5000, 2000000) # TikTok tem números maiores
        
        # Engajamento no TikTok costuma ser alto em views, menor em comments/likes proporcionalmente
        avg_views = int(followers * random.uniform(0.1, 5.0)) # Views podem explodir
        avg_likes = int(avg_views * random.uniform(0.05, 0.15))
        avg_comments = int(avg_likes * random.uniform(0.005, 0.03))
        
        captions = self._generate_mock_captions(is_affiliate)
        comments_text = self._generate_mock_comments(is_affiliate)

        return {
            "username": username,
            "platform": "tiktok",
            "niche": niche,
            "city": random.choice(self.cities),
            "followers": followers,
            "avg_likes": avg_likes,
            "avg_comments": avg_comments,
            "bio": bio,
            "link_in_bio": api_link,
            "captions": captions,
            "comments_text": comments_text,
            "avg_views": avg_views # Métrica extra do TikTok
        }

    def _generate_mock_captions(self, is_affiliate):
        """Gera legendas curtas estilo TikTok"""
        captions = []
        base = ["#fyp", "#viral", "Vocês não vão acreditar", "Dica rápida", "Pov"]
        sales = ["Link na bio", "Corre que acaba", "Promoção relâmpago", "Comenta 'EU'"]
        
        for _ in range(5):
            text = random.choice(base)
            if is_affiliate and random.random() > 0.4:
                text += " " + random.choice(sales)
            captions.append(text)
        return captions

    def _generate_mock_comments(self, is_affiliate):
        """Gera comentários, muitos emojis no TikTok"""
        comments = []
        base = ["😂😂😂", "Amei", "Faz parte 2", "Meu Deus", "First"]
        sales = ["Preço?", "Onde compra?", "Link?", "Funciona mesmo?", "Qual o site?"]
        
        for _ in range(5):
            if is_affiliate and random.random() > 0.4:
                comments.append(random.choice(sales))
            else:
                comments.append(random.choice(base))
        return comments

