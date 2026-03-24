"""
InfluenceHunter AI - Engagement Analyzer

Este módulo analisa o engajamento dos influenciadores.
Funcionalidades:
- Calcular taxa de engajamento baseada em likes, comentários e seguidores
"""

def calculate_engagement(avg_likes: float, avg_comments: float, followers: int) -> float:
    """
    Calcula a taxa de engajamento (Engagement Rate) usando a fórmula ponderada:
    ((Likes + Comentários * 2) / Seguidores) * 100
    
    Args:
        avg_likes (float): Média de curtidas por post
        avg_comments (float): Média de comentários por post
        followers (int): Número total de seguidores
        
    Returns:
        float: Taxa de engajamento em porcentagem (ex: 3.5 para 3.5%)
               Retorna 0.0 se followers for 0 ou negativo.
    """
    if followers <= 0:
        return 0.0
        
    engagement_score = (avg_likes + (avg_comments * 2)) / followers * 100
    
    # Arredonda para 2 casas decimais para melhor legibilidade
    return round(engagement_score, 2)

