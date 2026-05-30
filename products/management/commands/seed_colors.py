"""
Seed command to populate color variants and setup demo brands
"""

from django.core.management.base import BaseCommand
from products.models import Brand, ColorVariant


class Command(BaseCommand):
    help = 'Seed color variants and demo brands for Grow More'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating color variants...'))
        
        colors = [
            ('Bright Blue', '#51e2f5'),
            ('Blue Green', '#9df9ef'),
            ('Dusty White', '#edf756'),
            ('Pink Sand', '#ffa8b6'),
            ('Dark Sand', '#a28089'),
            ('Ink', '#3a2f33'),
            ('Black', '#000000'),
            ('White', '#ffffff'),
            ('Navy', '#001f3f'),
            ('Ocean Blue', '#0066cc'),
            ('Sunset Orange', '#ff6b35'),
            ('Forest Green', '#2d5016'),
            ('Cream', '#fffdd0'),
            ('Charcoal', '#36454f'),
            ('Burgundy', '#800020'),
            ('Teal', '#008080'),
            ('Olive', '#808000'),
            ('Lavender', '#e6e6fa'),
        ]
        
        created_count = 0
        for name, hex_code in colors:
            color, created = ColorVariant.objects.get_or_create(
                name=name,
                hex_code=hex_code
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Created color: {name} ({hex_code})')
            else:
                self.stdout.write(f'  - Already exists: {name}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Created {created_count} color variants'))

        # Create sample brands
        self.stdout.write(self.style.SUCCESS('\nCreating sample brands...'))
        
        brands = [
            ('Grow More Original', 'Exclusive Grow More summer collection'),
            ('Casual Line', 'Relaxed fit summer wear'),
            ('Premium Edition', 'Luxury summer menswear'),
            ('Urban Collection', 'Streetwear inspired styles'),
        ]
        
        brand_created_count = 0
        for idx, (name, description) in enumerate(brands, 1):
            brand, created = Brand.objects.get_or_create(
                name=name,
                defaults={'description': description, 'sort_order': idx}
            )
            if created:
                brand_created_count += 1
                self.stdout.write(f'  ✓ Created brand: {name}')
            else:
                self.stdout.write(f'  - Already exists: {name}')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {brand_created_count} brands'))
        self.stdout.write(self.style.SUCCESS('\n✓ Seed command completed successfully!'))
