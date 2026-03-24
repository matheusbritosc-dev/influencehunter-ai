"""
InfluenceHunter AI - Conversion Potential Analyzer

Este módulo analisa o potencial de conversão de influenciadores para vendas de infoprodutos.
Foca em identificar comportamentos de venda e prontidão da audiência para compra.

Critérios:
- Presença de Link na Bio
- Uso de Call to Action (CTA) nos posts
- Palavras-chave de venda (cupom, desconto, oferta, clique)
- Comentários da audiência demonstrando interesse de compra (preço?, valor?, como compro?)
"""

import re

class ConversionAnalyzer:
    """
    Analisa o potencial de vendas de um influenciador.
    """

    def __init__(self):
        # Palavras-chave que indicam tentativa de venda pelo influenciador
        self.sales_keywords = [
            r"link na bio", r"clique no link", r"cupom", r"desconto", 
            r"oferta", r"promoção", r"frete grátis", r"curso", r"garanta",
            r"vagas abertas", r"inscreva-se", r"comprar", r"loja", r"site"
        ]
        
        # Palavras-chave que indicam interesse de compra pela audiência
        self.purchase_intent_keywords = [
            r"preço\?", r"valor\?", r"quanto custa", r"como compro", 
            r"onde compra", r"link\?", r"quero", r"preciso", r"tenho interesse",
            r"qual o valor"
        ]

    def calculate_conversion_potential(self, bio: str, has_link: bool, posts_captions: list, comments_text: list) -> tuple:
        """
        Calcula um score de 0 a 100 indicando o potencial de conversão e retorna metadados.
        
        Critérios (Score final somado, max 100):
        - Bio contém link → +20 pontos
        - Bio contém WhatsApp → +20 pontos
        - Bio contém palavras de venda → +20 pontos
        - Posts com CTA → +20 pontos
        - Comentários com perguntas de preço → +20 pontos
        
        Args:
            bio (str): Texto da biografia
            has_link (bool): Se existe link na bio
            posts_captions (list): Lista de textos das legendas dos posts recentes
            comments_text (list): Lista de comentários da audiência
            
        Returns:
            tuple: (conversion_score, sales_language_score, has_whatsapp)
        """
        score = 0.0
        bio_lower = bio.lower() if bio else ""
        
        # 1. Bio contém link (+20)
        # Verifica se has_link é true OU se tem string de link na bio text
        has_link_confirmed = has_link or "http" in bio_lower or "www" in bio_lower
        if has_link_confirmed:
            score += 20.0
            
        # 2. Bio contém WhatsApp (+20)
        # Procura por padrões de telefone ou keywords
        whatsapp_keywords = [r"wa\.me", r"whatsapp", r"119\d{8}", r"219\d{8}", r"zap", r"contato"]
        has_whatsapp = any(re.search(k, bio_lower) for k in whatsapp_keywords)
        if has_whatsapp:
            score += 20.0
            
        # 3. Bio contém palavras de venda (+20)
        keywords_bio = [r"mentoria", r"curso", r"aprenda", r"consultoria", r"compre", r"link na bio", r"vendas", r"oficial"]
        if any(re.search(k, bio_lower) for k in keywords_bio):
            score += 20.0
            
        # 4. Posts com CTA (+20)
        # Se pelo menos um post recente tiver CTA claro
        cta_keywords = [r"me chama", r"arrasta", r"link", r"vagas", r"clique", r"direct", r"saiba mais"]
        has_post_cta = False
        if posts_captions:
            for caption in posts_captions:
                caption_lower = caption.lower()
                if any(re.search(k, caption_lower) for k in cta_keywords):
                    has_post_cta = True
                    break
        
        if has_post_cta:
            score += 20.0
            
        # 5. Comentários com perguntas de preço (+20)
        # Se houver engajamento de compra
        price_keywords = [r"quanto custa", r"tem valor", r"preço", r"como funciona", r"quero", r"tenho interesse"]
        has_price_question = False
        if comments_text:
            for comment in comments_text:
                comment_lower = comment.lower()
                if any(re.search(k, comment_lower) for k in price_keywords):
                    has_price_question = True
                    break
                    
        if has_price_question:
            score += 20.0
            
        # Sales Language Score (separado, mas derivado do uso de termos de venda)
        # Vamos calcular baseado na presença de termos na bio e posts
        sales_language_score = 0.0
        if has_post_cta: sales_language_score += 50
        if any(re.search(k, bio_lower) for k in keywords_bio): sales_language_score += 50
            
        return min(100.0, score), min(100.0, sales_language_score), has_whatsapp
