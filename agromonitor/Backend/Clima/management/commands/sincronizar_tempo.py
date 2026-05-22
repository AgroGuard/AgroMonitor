from django.core.management.base import BaseCommand
from Clima.models import LocalidadeClima
from Clima.services import OpenWeatherMapService


class Command(BaseCommand):
    help = 'Sincroniza dados de previsão do tempo com OpenWeatherMap'

    def add_arguments(self, parser):
        parser.add_argument(
            '--localidade-id',
            type=int,
            help='ID da localidade específica a atualizar (omitir para todas)'
        )

    def handle(self, *args, **options):
        try:
            service = OpenWeatherMapService()
            
            if options['localidade_id']:
                # Atualizar localidade específica
                try:
                    localidade = LocalidadeClima.objects.get(id=options['localidade_id'])
                    self.stdout.write(f"Atualizando {localidade.nome}...")
                    resultado = service.atualizar_previsao_localidade(localidade)
                    
                    if resultado['sucesso']:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ {localidade.nome} atualizada com sucesso"
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f"✗ Erro ao atualizar {localidade.nome}: {resultado['erro']}"
                            )
                        )
                except LocalidadeClima.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f"Localidade com ID {options['localidade_id']} não encontrada")
                    )
            else:
                # Atualizar todas as localidades
                self.stdout.write("Atualizando todas as localidades ativas...")
                resultados = service.atualizar_todas_localidades()
                
                total_sucessos = sum(1 for r in resultados if r['resultado']['sucesso'])
                total_erros = len(resultados) - total_sucessos
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n✓ Atualização concluída:\n"
                        f"  Total: {len(resultados)}\n"
                        f"  Sucessos: {total_sucessos}\n"
                        f"  Erros: {total_erros}"
                    )
                )
                
                # Mostrar detalhes de erros
                if total_erros > 0:
                    self.stdout.write(self.style.WARNING("\nLocalidades com erro:"))
                    for resultado in resultados:
                        if not resultado['resultado']['sucesso']:
                            self.stdout.write(
                                f"  - {resultado['localidade']}: {resultado['resultado']['erro']}"
                            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro ao sincronizar: {e}"))
