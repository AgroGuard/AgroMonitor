from django.core.management.base import BaseCommand
from Clima.models import LocalidadeClima


class Command(BaseCommand):
    help = 'Cria uma nova localidade para monitoramento climático'

    def add_arguments(self, parser):
        parser.add_argument('nome', type=str, help='Nome da localidade')
        parser.add_argument('--latitude', type=float, required=True, help='Latitude')
        parser.add_argument('--longitude', type=float, required=True, help='Longitude')
        parser.add_argument('--pais', type=str, default='Brasil', help='País (padrão: Brasil)')
        parser.add_argument('--estado', type=str, default='', help='Estado/Província')
        parser.add_argument('--fazenda-id', type=str, default='', help='ID da fazenda')

    def handle(self, *args, **options):
        try:
            localidade, created = LocalidadeClima.objects.get_or_create(
                latitude=options['latitude'],
                longitude=options['longitude'],
                defaults={
                    'nome': options['nome'],
                    'pais': options['pais'],
                    'estado': options['estado'],
                    'fazenda_id': options['fazenda_id'],
                    'ativa': True,
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Localidade '{options['nome']}' criada com sucesso\n"
                        f"  ID: {localidade.id}\n"
                        f"  Lat: {localidade.latitude}, Lon: {localidade.longitude}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠ Localidade já existe com essas coordenadas (ID: {localidade.id})"
                    )
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro ao criar localidade: {e}"))
