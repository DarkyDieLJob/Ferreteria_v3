from bdd.models import Item

SUFFIX_MAP = {
    "Cr": 29, "P": 27, "CyM": 25, "V": 7, "Y": 8, "C": 17,
    "Fp": 24, "Hm": 18, "Sn": 3, "Cb": 12, "A": 22, "E": 30,
    "Mf": 28, "Dx": 6, "S": 13, "M": 5, "3D": 2, "F": 19,
    "Sp": 26, "Nc": 21, "B": 4, "Pl": 35, "Ps": 16, "H": 10,
    "Eq": 14, "Px": 15, "Fd": 34, "Alf": 31, "Tn": 33,
}

qs = Item.objects.filter(proveedor__isnull=True)
total = qs.count()
print(f"Sin prov: {total}")

updated = 0
unmapped = 0
batch = []

for item in qs.iterator():
    code = item.codigo or ""
    parts = code.split("/")
    suffix = parts[-1] if len(parts) > 1 else None
    if suffix and suffix in SUFFIX_MAP:
        item.proveedor_id = SUFFIX_MAP[suffix]
        batch.append(item)
        updated += 1
    else:
        unmapped += 1
    if len(batch) >= 200:
        Item.objects.bulk_update(batch, ["proveedor"], batch_size=200)
        print(f"Update {updated}/{total}...")
        batch = []

if batch:
    Item.objects.bulk_update(batch, ["proveedor"], batch_size=200)

print(f"Asignados: {updated} | Sin mapeo: {unmapped} | Total: {total}")
