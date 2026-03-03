from django.core.management.base import BaseCommand
from django.db import transaction
from bdd.models import Item
from utils.rounding import round_price


class Command(BaseCommand):
    help = "Aplica el redondeo unificado a campos de precio en Item. Usa --dry-run para simular."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            help="No guarda cambios, solo reporta cuántos items cambiarían",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            dest="batch_size",
            help="Tamaño de lote para procesar items",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        batch_size = max(1, int(options["batch_size"]))

        qs = Item.objects.all()
        total = qs.count()
        self.stdout.write(
            self.style.NOTICE(
                f"Items a procesar: {total} | batch={batch_size} | dry_run={dry_run}"
            )
        )

        offset = 0
        changed_total = 0
        while offset < total:
            batch = list(qs[offset : offset + batch_size])
            offset += len(batch)

            items_to_update = []
            for item in batch:
                is_cartel = bool(getattr(item, "tiene_cartel", False))

                orig_final = item.final
                orig_final_ef = item.final_efectivo
                orig_rollo = getattr(item, "final_rollo", 0.0)
                orig_rollo_ef = getattr(item, "final_rollo_efectivo", 0.0)

                item.final = round_price(orig_final, is_cartel=is_cartel)
                item.final_efectivo = round_price(orig_final_ef, is_cartel=is_cartel)
                if hasattr(item, "final_rollo"):
                    item.final_rollo = round_price(orig_rollo, is_cartel=is_cartel)
                if hasattr(item, "final_rollo_efectivo"):
                    item.final_rollo_efectivo = round_price(
                        orig_rollo_ef, is_cartel=is_cartel
                    )

                if (
                    item.final != orig_final
                    or item.final_efectivo != orig_final_ef
                    or (hasattr(item, "final_rollo") and item.final_rollo != orig_rollo)
                    or (
                        hasattr(item, "final_rollo_efectivo")
                        and item.final_rollo_efectivo != orig_rollo_ef
                    )
                ):
                    items_to_update.append(item)

            changed_total += len(items_to_update)

            if not dry_run and items_to_update:
                fields = ["final", "final_efectivo"]
                if hasattr(items_to_update[0], "final_rollo"):
                    fields.append("final_rollo")
                if hasattr(items_to_update[0], "final_rollo_efectivo"):
                    fields.append("final_rollo_efectivo")
                with transaction.atomic():
                    Item.objects.bulk_update(
                        items_to_update, fields, batch_size=batch_size
                    )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"Dry-run: {changed_total} items cambiarían.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Completado: {changed_total} items actualizados.")
            )
