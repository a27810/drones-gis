import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from core.models import Zone


class Command(BaseCommand):
    help = "Importa zonas UAS desde un fichero GeoJSON a la tabla Zone."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            help=(
                "Ruta al fichero GeoJSON. "
                "Si no se indica, se usa static/geojson/enaire_uas_zones_example.geojson"
            ),
        )

        parser.add_argument(
            "--keep-existing",
            action="store_true",
            help="No borra las zonas existentes antes de importar.",
        )

    def handle(self, *args, **options):
        # 1) Determinar ruta del fichero
        if options.get("file"):
            path = Path(options["file"])
        else:
            path = (
                Path(settings.BASE_DIR)
                / "static"
                / "geojson"
                / "enaire_uas_zones_example.geojson"
            )

        if not path.exists():
            raise CommandError(f"No se encuentra el archivo GeoJSON en: {path}")

        self.stdout.write(self.style.NOTICE(f"Usando fichero: {path}"))

        # 2) Cargar JSON
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise CommandError(f"No se pudo leer o parsear el JSON: {exc}")

        # 3) Borrar zonas previas (a menos que se use --keep-existing)
        deleted_count = 0
        if not options.get("keep_existing"):
            deleted_count, _ = Zone.objects.all().delete()
            self.stdout.write(f"Zonas anteriores eliminadas: {deleted_count}")
        else:
            self.stdout.write("Manteniendo zonas existentes (opción --keep-existing).")

        # 4) Insertar nuevas zonas
        features = data.get("features", [])
        created_count = 0

        for feat in features:
            if not isinstance(feat, dict):
                continue

            props = feat.get("properties") or {}

            name = props.get("name") or "Zona UAS"
            zone_type = props.get("zone_type") or "Zona de ejemplo"

            Zone.objects.create(
                name=name,
                zone_type=zone_type,
                geometry=feat,        # guardamos el Feature entero
                # Si prefieres solo la geometría:
                # geometry=feat.get("geometry")
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Importación completada. Creadas {created_count} zonas (eliminadas previamente: {deleted_count})."
            )
        )
