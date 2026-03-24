"""
InfluenceHunter AI - Instagram Data Collector

Este módulo é responsável pela coleta de dados do Instagram.
Suporta modo Simulado e modo REAL via Apify (instagram-scraper).
"""

import random
import time
import requests
import json

class InstagramCollector:
    """
    Classe para coletar dados de influenciadores do Instagram.
    Se api_key for None. opera em modo de simulação.
    Se api_key for fornecida, usa Apify.
    """
    
    def __init__(self, api_key=None, simulated=False):
        """
        Inicializa o coletor do Instagram
        
        Args:
            api_key (str): Token da API do Apify
            simulated (bool): Se True, força uso de dados simulados
        """
        self.api_key = api_key
        self.simulated = simulated if api_key is None else simulated
        self.apify_url = "https://api.apify.com/v2/acts/apify~instagram-scraper/run-sync-get-dataset-items"
        
        self.niches = ["Fitness", "Marketing Digital", "Beleza", "Finanças", "Tecnologia", "Moda", "Gastronomia"]
        self.cities = ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba", "Recife", "Porto Alegre"]

    def collect_profile(self, username):
        """
        Coleta dados do perfil de um influenciador
        
        Args:
            username (str): Nome de usuário do Instagram
            
        Returns:
            dict: Dados do perfil coletados e normalizados
        """
        if self.simulated:
            print(f"[Instagram-Mock] Coletando perfil simulado para: {username}...")
            time.sleep(0.3) 
            return self._generate_mock_profile(username)
        else:
            return self._fetch_real_data(username)

    def _fetch_real_data(self, username):
        """Busca dados reais no Apify"""
        print(f"[Instagram-Real] Buscando dados no Apify para: {username}...")
        
        try:
            # Configuração do Payload para o Apify instagram-scraper
            # Correção baseada no schema fornecido: usa 'directUrls' ou 'search' ao invés de 'usernames'
            payload = {
                "directUrls": [f"https://www.instagram.com/{username}/"],
                "resultsType": "details", # Ou "posts" se quiser posts
                "resultsLimit": 1,
                "searchType": "hashtag", # Default
                "searchLimit": 1
            }
            
            # Nota: O endpoint run-sync-get-dataset-items espera POST
            response = requests.post(
                f"{self.apify_url}?token={self.api_key}",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 201 and response.status_code != 200:
                print(f"[ERRO] Falha na API Apify: {response.status_code} - {response.text}")
                return None
                
            data = response.json()
            
            if not data or len(data) == 0:
                print(f"[AVISO] Nenhum dado encontrado para {username}")
                return None
                
            # O retorno é uma lista de itens. Pegamos o primeiro que corresponde ao username
            user_data = None
            for item in data:
                if item.get('username') == username:
                    user_data = item
                    break
            
            if not user_data:
                # Fallback: pega o primeiro item se não bater username exato (pode ser redirecionamento ou busca)
                user_data = data[0]

            return self._normalize_apify_data(user_data)

        except Exception as e:
            print(f"[ERRO] Exceção na coleta Apify: {e}")
            return None

    def discover_from_hashtags(self, hashtags):
        """
        Descobre novos influenciadores a partir de hashtags (Viral Discovery)
        """
        if self.simulated:
            print(f"[Insta-Mock] Descobrindo via hashtags: {hashtags}...")
            # Retorna alguns perfis simulados
            return [self.collect_profile(f"new_discovery_{i}") for i in range(3)]
        
        print(f"[Insta-Real] Buscando posts virais para hashtags: {hashtags}...")
        discovered_profiles = []
        
        for tag in hashtags:
            try:
                # Busca POSTS por hashtag
                payload = {
                    "search": tag,
                    "searchType": "hashtag",
                    "resultsType": "posts",
                    "searchLimit": 1, # Busca 1 hashtag
                    "resultsLimit": 5 # Pega 5 posts recentes/top
                }
                
                response = requests.post(
                    f"{self.apify_url}?token={self.api_key}",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200 or response.status_code == 201:
                    posts = response.json()
                    if isinstance(posts, list):
                        for post in posts:
                            username = post.get('ownerUsername')
                            if username:
                                print(f"[Insta-Discovery] Encontrado via #{tag}: {username}")
                                # Coleta perfil completo deste usuario
                                p = self.collect_profile(username)
                                if p: discovered_profiles.append(p)
                                
            except Exception as e:
                print(f"[ERRO-Discovery] Falha ao buscar tag {tag}: {e}")
                
        return discovered_profiles

    def _normalize_apify_data(self, data):
        """Normaliza os dados do Apify para o formato do InfluenceHunter"""
        
        # Extração segura de campos de posts (se existirem nos detalhes ou precisarem de outra chamada)
        # O scraper de detalhes as vezes traz 'latestPosts'
        latest_posts = data.get('latestPosts', [])
        captions = []
        comments_text = [] # Apify scraper de detalhes geralmente não traz comentários profundos
        
        for post in latest_posts:
            if 'caption' in post:
                captions.append(post['caption'])
            # Comentários precisariam de outra chamada ou configuração 'commentsPerPost'
        
        # Inferência de métricas se não vierem explícitas
        likes = data.get('businessDiscovery', {}).get('media_count', 0) # Exemplo falho, ajustar conforme payload real
        # Geralmente apify retorna 'followersCount'
        
        followers = data.get('followersCount', 0)
        avg_likes = 0
        if latest_posts:
            total_likes = sum(p.get('likesCount', 0) for p in latest_posts)
            avg_likes = total_likes / len(latest_posts)
        
        # Bio e Links
        bio = data.get('biography', '')
        link_in_bio = data.get('externalUrl', '')
        
        return {
            "username": data.get('username', ''),
            "platform": "instagram",
            "niche": data.get('businessCategoryName', 'Desconhecido'), # Tenta pegar categoria
            "city": "", # Difícil pegar cidade exata sem análise de texto, deixar vago
            "followers": followers,
            "avg_likes": avg_likes,
            "avg_comments": 0, # Difícil sem chamada extra
            "bio": bio,
            "link_in_bio": link_in_bio,
            "captions": captions,
            "comments_text": comments_text # Vazio por padrão na busca simples
        }

    def _generate_mock_profile(self, username):
        # ... (Manter código existente de mock) ...
        """Gera um perfil completo simulado com viés de afiliado ou não"""
        
        # Decide se é um bom afiliado (tem link, cta, etc) aleatoriamente
        is_affiliate = random.random() > 0.4
        has_link = is_affiliate or (random.random() > 0.7)
        has_whatsapp = is_affiliate and (random.random() > 0.5)
        
        bio_templates = [
            "Apaixonado por {niche}.",
            "Criando conteúdo sobre {niche} todos os dias.",
            "Ajudo você a conquistar seus objetivos em {niche}.",
            "Vida real e {niche}.",
            "Empreendedor digital | {niche}"
        ]
        
        cta_templates = [
            " | Clique no link abaixo! 👇",
            " | Mentoria aberta 🚀",
            " | Solicite seu orçamento via Direct",
            " | Cupom: INSTA10",
            ""
        ]
        
        niche = random.choice(self.niches)
        bio = random.choice(bio_templates).format(niche=niche)
        
        if has_link:
            bio += random.choice(cta_templates)
            
        if has_whatsapp:
            bio += " | Contato: (11) 99999-9999"
            
        followers = random.randint(1500, 150000)
        # Engajamento realista: menor conforme seguidores aumentam
        engagement_base = random.uniform(0.5, 5.0) 
        if followers < 5000: engagement_base += 2.0
        
        avg_likes = int(followers * (engagement_base / 100))
        avg_comments = int(avg_likes * random.uniform(0.01, 0.1))
        
        # Gerar posts e comentários
        captions = self._generate_mock_captions(is_affiliate, niche)
        comments_text = self._generate_mock_comments(is_affiliate)

        return {
            "username": username,
            "platform": "instagram",
            "niche": niche,
            "city": random.choice(self.cities),
            "followers": followers,
            "avg_likes": avg_likes,
            "avg_comments": avg_comments,
            "bio": bio,
            "link_in_bio": "https://linktr.ee/exemplo" if has_link else "",
            "captions": captions,
            "comments_text": comments_text
        }

    def _generate_mock_captions(self, is_affiliate, niche):
        """Gera legendas de posts"""
        captions = []
        base_captions = [
            f"Adorei essa novidade de {niche}!",
            "Dia incrível por aqui.",
            "O que vocês acham disso?",
            "Post de apreciação.",
            "Fiz um resumo sobre o tema de hoje."
        ]
        
        sales_captions = [
            "Link na bio para garantir sua vaga!",
            "Comente 'EU QUERO' que te mando o link.",
            "Últimas horas da promoção.",
            "Tudo o que você precisa saber está no link do perfil.",
            "Me chama no WhatsApp para fechar."
        ]
        
        for _ in range(5):
            if is_affiliate and random.random() > 0.3:
                captions.append(random.choice(sales_captions))
            else:
                captions.append(random.choice(base_captions))
        return captions

    def _generate_mock_comments(self, is_affiliate):
        """Gera comentários da audiência"""
        comments = []
        generic_comments = ["Linda!", "Amei", "Top", "Muito bom", "👏", "Show"]
        sales_comments = ["Quanto custa?", "Qual o valor?", "Tenho interesse", "Me manda o link?", "Serve para mim?"]
        
        for _ in range(5):
            if is_affiliate and random.random() > 0.4:
                comments.append(random.choice(sales_comments))
            else:
                comments.append(random.choice(generic_comments))
        return comments

