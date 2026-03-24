"""
InfluenceHunter AI - CSV Export Module

Este módulo é responsável pela exportação de dados em formato CSV.
Funcionalidades:
- Exportar rankings de influenciadores
- Exportar métricas detalhadas
- Gerar relatórios customizados
- Formatar dados para exportação
- Gerenciar arquivos de saída
"""

import csv
from datetime import datetime


class CSVExporter:
    """
    Classe para exportar dados em formato CSV
    """
    
    def __init__(self, output_path="exports/"):
        """
        Inicializa o exportador CSV
        
        Args:
            output_path (str): Caminho para salvar arquivos exportados
        """
        self.output_path = output_path
    
    def export_ranking(self, ranking_data, filename=None):
        """
        Exporta ranking de influenciadores para CSV com foco em Radar de Afiliados
        
        Args:
            ranking_data (list): Lista de influenciadores ranqueados (dicts ou Rows)
            filename (str): Nome do arquivo (opcional)
            
        Returns:
            str: Caminho do arquivo exportado
        """
        if not filename:
            filename = self._generate_filename("ranking_afiliados")
            
        filepath = f"{self.output_path}{filename}"
        
        # Garante que o diretório existe
        import os
        os.makedirs(self.output_path, exist_ok=True)
        
        # Colunas definidas para o Radar de Afiliados
        fieldnames = [
            'username', 'platform', 'niche', 'city', 
            'followers', 'engagement_rate', 'conversion_potential', 
            'influence_score', 'bio', 'link_in_bio'
        ]
        
        try:
            with open(filepath, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for influencer in ranking_data:
                    # Filtra apenas os campos desejados do dicionário/objeto
                    row = {field: influencer.get(field, '') for field in fieldnames}
                    writer.writerow(row)
                    
            print(f"[OK] Ranking exportado com sucesso: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"[ERRO] Erro ao exportar CSV: {e}")
            return None
    
    def _generate_filename(self, prefix="export"):
        """
        Gera nome de arquivo com timestamp
        
        Args:
            prefix (str): Prefixo do nome do arquivo
            
        Returns:
            str: Nome do arquivo gerado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.csv"
