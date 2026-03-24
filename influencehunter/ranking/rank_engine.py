"""
InfluenceHunter AI - Ranking Engine

Este módulo é responsável pelo sistema de ranking de influenciadores.
Foca em encontrar os melhores afiliados locais para infoprodutos.

Critérios de Peso:
- Potencial de Conversão (Alto peso): Afiliado precisa vender.
- Engajamento (Médio peso): Precisa ter audiência ativa.
- Autenticidade (Médio peso): Precisa ser real.
- Crescimento (Baixo peso): Estabilidade é mais importante que viralidade momentânea para afiliados consistentes.
"""

class RankEngine:
    """
    Classe para calcular e gerar rankings de influenciadores para afiliação
    """
    
    def __init__(self, weights=None):
        """
        Inicializa o motor de ranking com pesos otimizados para vendas (Afiliados)
        
        Args:
            weights (dict): Pesos para cada métrica no cálculo do score
        """
        # Pesos padrão focados em VENDAS
        self.weights = weights or {
            'conversion_potential': 0.40, # 40% - O mais importante: Capacidade de venda
            'engagement': 0.25,           # 25% - Atenção da audiência
            'authenticity': 0.25,         # 25% - Confiança da audiência
            'growth': 0.10                # 10% - Relevância atual
        }
    
    def calculate_overall_score(self, influencer_data: dict) -> float:
        """
        Calcula o score geral de influência focado em afiliação
        
        Args:
            influencer_data (dict): Dados do influenciador incluindo métricas (0-100)
            
        Returns:
            float: Score geral (0-100)
        """
        score = (
            influencer_data.get('conversion_potential', 0) * self.weights['conversion_potential'] +
            influencer_data.get('engagement_rate', 0) * self.weights['engagement'] + # Assumindo que rate já foi normalizada ou é comparável
            influencer_data.get('authenticity_score', 0) * self.weights['authenticity'] +
            influencer_data.get('growth_rate', 0) * self.weights['growth']
        )
        return round(score, 2)
    
    def rank_influencers(self, influencers_list: list) -> list:
        """
        Gera ranking de influenciadores ordenado pelo Score Calculado
        
        Args:
            influencers_list (list): Lista de dicionários/objetos de influenciadores
            
        Returns:
            list: Lista ordenada de influenciadores
        """
        # Recalcula scores se necessário ou usa o já existente
        for infl in influencers_list:
            # Normalização básica
            eng_score = min(100.0, infl['engagement_rate'] * 10) 
            growth_score = max(0.0, min(100.0, infl['growth_rate'] * 5))
            
            data_for_calc = {
                'conversion_potential': infl.get('conversion_potential', 0),
                'engagement_rate': eng_score,
                'authenticity_score': infl.get('authenticity_score', 0),
                'growth_rate': growth_score
            }
            
            infl_score = self.calculate_overall_score(data_for_calc)
            
            # Adiciona score calculado temporariamente
            if isinstance(infl, dict):
                infl['calculated_ranking_score'] = infl_score

        # Ordena
        sorted_list = sorted(
            [dict(i) for i in influencers_list], 
            key=lambda x: x.get('calculated_ranking_score', 0), 
            reverse=True
        )
            
        return sorted_list

    def rank_influencers_for_affiliate(self, influencers_list: list, niche: str = None, city: str = None, min_followers: int = 0, max_followers: int = 10000000, min_conversion_score: float = 0.0) -> list:
        """
        Gera ranking específico para afiliados com filtros.
        
        Args:
            influencers_list (list): Lista de influenciadores
            niche (str): Nicho alvo
            city (str): Cidade alvo
            min_followers (int): Mínimo de seguidores
            max_followers (int): Máximo de seguidores
            min_conversion_score (float): Score mínimo de conversão
        
        Returns:
            list: Lista filtrada e ordenada
        """
        filtered = []
        for infl in influencers_list:
            infl_dict = dict(infl)
            
            # Filtros
            if niche and niche.lower() not in infl_dict.get('niche', '').lower():
                continue
            if city and city.lower() not in infl_dict.get('city', '').lower():
                continue
            if not (min_followers <= infl_dict.get('followers', 0) <= max_followers):
                continue
            if infl_dict.get('conversion_potential', 0) < min_conversion_score:
                continue
                
            filtered.append(infl_dict)
            
        # Usa o método padrão de rankeamento na lista filtrada
        return self.rank_influencers(filtered)

