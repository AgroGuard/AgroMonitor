from django.core.management.base import BaseCommand
import time
import logging
from django.conf import settings
from Clima.services import OpenWeatherMapService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Worker que atualiza previsões periodicamente. Lê interval e enabled de settings, aceita --interval e --force.'

    def add_arguments(self, parser):
        parser.add_argument('--interval', type=int, help='Intervalo em segundos entre atualizações (sobrescreve settings)')
        parser.add_argument('--force', action='store_true', help='Força execução mesmo se CLIMA_AUTO_UPDATE_ENABLED estiver False')

    def handle(self, *args, **options):
        # Ler configurações do settings com valores padrão
        default_interval = getattr(settings, 'CLIMA_UPDATE_INTERVAL_SECONDS', 1800)
        enabled = getattr(settings, 'CLIMA_AUTO_UPDATE_ENABLED', False)

        # Permitir sobrescrever por CLI
        interval = options.get('interval') or default_interval
        force_run = options.get('force', False)

        if not enabled and not force_run:
            self.stdout.write(self.style.WARNING(
                'CLIMA_AUTO_UPDATE_ENABLED está False. Execute com --force para forçar ou habilite em settings.'
            ))
            return

        service = OpenWeatherMapService()

        self.stdout.write(self.style.SUCCESS(f'Iniciando worker de atualização de previsões (interval={interval}s)'))

        try:
            while True:
                try:
                    self.stdout.write('Iniciando atualização de todas as localidades...')
                    resultados = service.atualizar_todas_localidades()
                    successes = sum(1 for r in resultados if r['resultado']['sucesso'])
                    total = len(resultados)
                    self.stdout.write(self.style.SUCCESS(f'Atualização finalizada: {successes}/{total} com sucesso'))
                except Exception as e:
                    logger.exception('Erro durante atualização periódica de previsões')
                    self.stdout.write(self.style.ERROR(f'Erro durante atualização periódica: {e}'))

                self.stdout.write(f'Aguardando {interval} segundos para próxima execução...')
                time.sleep(interval)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Worker interrompido pelo usuário (KeyboardInterrupt)'))
