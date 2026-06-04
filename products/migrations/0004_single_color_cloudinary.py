from django.db import migrations, models

import products.models


def copy_first_legacy_color(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    through_model = Product.colors.through
    for product in Product.objects.all():
        relation = (
            through_model.objects.filter(product_id=product.id)
            .select_related("colorvariant")
            .order_by("id")
            .first()
        )
        if relation and relation.colorvariant.hex_code:
            product.color_hex = relation.colorvariant.hex_code.upper()
            product.save(update_fields=["color_hex"])


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0003_wishlist"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="cloudinary_public_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="color_hex",
            field=models.CharField(default="#51E2F5", max_length=7, validators=[products.models.validate_hex_color]),
        ),
        migrations.RunPython(copy_first_legacy_color, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="product",
            name="colors",
        ),
    ]
