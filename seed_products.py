"""
Seed script to populate the store with products based on images in media/products/
Run: python seed_products.py
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'ecosphere.settings'
django.setup()

from django.conf import settings
from store.models import Category, Product

BASE_DIR = settings.BASE_DIR
MEDIA_PRODUCTS = os.path.join(BASE_DIR, 'media', 'products')

# Define categories
categories = {
    'Personal Care': 'personal_care',
    'Kitchen & Dining': 'kitchen',
    'Home & Living': 'home',
    'Clothing & Accessories': 'clothing',
    'Office Supplies': 'office',
    'Outdoor & Sports': 'outdoor',
    'Cleaning Products': 'cleaning',
}

cat_objs = {}
for name, slug in categories.items():
    cat, _ = Category.objects.get_or_create(name=name)
    cat_objs[name] = cat
    print(f'  Category: {name} (id={cat.id})')

# Define products with (image_filename, name, description, price, category_name, stock, is_featured)
products_data = [
    ('bamboo_toothbrush.jpg', 'Bamboo Toothbrush',
     'Eco-friendly toothbrush made from sustainable bamboo. Biodegradable and planet-friendly alternative to plastic toothbrushes.',
     12.99, 'Personal Care', 250, True),
    ('biodegradable_container.jpg', 'Biodegradable Food Container',
     'Compostable food storage container made from plant-based materials. Perfect for takeout or meal prep.',
     24.99, 'Kitchen & Dining', 180, False),
    ('biodegradable_garbage_bag.jpg', 'Biodegradable Garbage Bags (30L, 20 pack)',
     'Heavy-duty garbage bags that fully decompose within 365 days. Made from cornstarch and PLA.',
     19.99, 'Cleaning Products', 90, False),
    ('biodegradable_sanitary_product.jpg', 'Natural Sanitary Pads (10 pack)',
     'Organic cotton sanitary pads with biodegradable backing. Gentle on skin and the environment.',
     14.99, 'Personal Care', 120, False),
    ('cloth_shopping_bag.jpg', 'Organic Cotton Shopping Bag (Set of 3)',
     'Sturdy reusable shopping bags made from certified organic cotton. Foldable and lightweight.',
     18.50, 'Clothing & Accessories', 200, False),
    ('compost_bin.jpg', 'Stainless Steel Compost Bin (10L)',
     'Odor-sealed kitchen compost bin with removable charcoal filter. Perfect for apartments.',
     49.99, 'Home & Living', 75, False),
    ('compostable_cutlery.jpg', 'Bamboo Cutlery Set (5 pcs)',
     'Reusable cutlery set made from sustainably sourced bamboo. Includes fork, knife, spoon, chopsticks, and carrying case.',
     16.99, 'Kitchen & Dining', 150, False),
    ('eco-friendly_cleaning_liquid.jpg', 'Eco-Friendly Cleaning Liquid (500ml)',
     'Plant-based cleaning liquid with natural ingredients. Biodegradable formula, safe around children and pets.',
     9.99, 'Cleaning Products', 300, False),
    ('eco-friendly_footware.jpg', 'Recycled Ocean Plastic Sneakers',
     'Stylish sneakers made entirely from recycled ocean plastic bottles. Comfortable and sustainable footwear.',
     79.99, 'Clothing & Accessories', 60, True),
    ('eco-friendly_pen.jpg', 'Seed Plantable Pen (Pack of 5)',
     'Biodegradable pens embedded with wildflower seeds. Plant the pen after use and watch flowers grow!',
     11.99, 'Office Supplies', 280, False),
    ('energy-efficient_LED_bulbs.jpg', 'LED Bulbs A19 (60W Equivalent, 8 pack)',
     'Energy-saving LED bulbs that use 85% less energy and last 25,000 hours. Warm white 2700K.',
     34.99, 'Home & Living', 100, False),
    ('glass_food_container.jpg', 'Borosilicate Glass Food Container',
     'Heat-resistant borosilicate glass container with bamboo lid. Microwave, freezer, and dishwasher safe.',
     27.99, 'Kitchen & Dining', 140, False),
    ('handmade_craft.jpg', 'Handwoven Jute Rug (5x7 ft)',
     'Artisan-crafted jute rug made by local artisans. Natural fiber that adds warmth to any room.',
     89.99, 'Home & Living', 30, True),
    ('hemp_clothing.jpg', 'Organic Hemp T-Shirt',
     'Comfortable unisex t-shirt made from 100% organic hemp. Soft, breathable, and naturally antimicrobial.',
     32.99, 'Clothing & Accessories', 90, False),
    ('metal_water_bottle.png', 'Stainless Steel Water Bottle (500ml)',
     'Double-wall vacuum-insulated stainless steel bottle. Keeps drinks cold for 24 hours or hot for 12 hours.',
     39.99, 'Outdoor & Sports', 160, True),
    ('natural_shampoo.jpg', 'Solid Shampoo Bar - Lavender',
     'Plastic-free solid shampoo bar with natural essential oils. Vegan and cruelty-free formula.',
     8.99, 'Personal Care', 220, False),
('organic_cotton_t-shirt.jpg', 'Organic Cotton Graphic Tee',
     'Soft and comfortable t-shirt made from 100% organic cotton. Ethically produced with eco-friendly dyes.',
     28.99, 'Clothing & Accessories', 110, False),
    ('organic_soap.jpg', 'Handmade Organic Soap Bar (Set of 3)',
     'Artisan soap bars made with organic ingredients and essential oils. Exfoliating and moisturizing.',
     13.99, 'Personal Care', 180, False),
    ('organic_spices.jpg', 'Organic Spice Sampler (6 flavors)',
     'Assorted organic spices sourced directly from sustainable farms. Packaged in reusable glass jars.',
     22.99, 'Kitchen & Dining', 95, False),
    ('plantable_seed_pencil.jpg', 'Plantable Seed Pencils (Set of 12)',
     'Pencils made from recycled paper with plantable seed cores. Grow herbs and flowers when done!',
     10.99, 'Office Supplies', 140, False),
    ('recycled_fabric_bags.jpg', 'Recycled Fabric Tote Bag (Large)',
     'Spacious tote bag made from recycled fabric. Perfect for groceries, books, or beach trips.',
     15.99, 'Clothing & Accessories', 170, False),
    ('recycled_jewelry.jpg', 'Recycled Silver Hoop Earrings',
     'Beautiful handcrafted earrings made from recycled silver. Ethical and sustainable jewelry.',
     44.99, 'Clothing & Accessories', 55, False),
    ('recycled_material_phone-case.jpg', 'Eco-Phone Case (iPhone/Android)',
     'Shockproof phone case made from recycled ocean plastic and plant-based bioplastic.',
     26.99, 'Office Supplies', 130, True),
    ('recycled_paper_notebooks.jpg', 'Recycled Paper Hardcover Notebook',
     'Premium notebook made from 100% recycled paper. Features a durable recycled cardboard cover.',
     7.99, 'Office Supplies', 240, False),
    ('resuable_straw.jpg', 'Reusable Stainless Steel Straws (4 pack)',
     'Set of 4 food-grade stainless steel straws with cleaning brush. Durable zero-waste alternative to plastic.',
     9.99, 'Kitchen & Dining', 300, False),
    ('reusable_cotton_pad.jpg', 'Organic Cotton Reusable Pads (8 pack)',
     'Soft and absorbent menstrual pads made from certified organic cotton. Includes laundry bag.',
     17.99, 'Personal Care', 85, False),
    ('reusable_paper_towel.jpg', 'Bamboo Fiber Reusable Paper Towels (4 pack)',
     'Ultra-absorbent reusable towels made from bamboo fiber. Machine washable and dishwasher safe.',
     21.99, 'Kitchen & Dining', 120, False),
    ('solar-powered_chargers.jpg', 'Solar Power Bank (20000mAh)',
     'Portable solar charger with high-capacity battery. Perfect for camping, hiking, or emergency use.',
     54.99, 'Outdoor & Sports', 65, False),
    ('upcycled_furniture.jpg', 'Reclaimed Wood Coffee Table',
     'Handcrafted coffee table made from reclaimed wood. Each piece is unique with natural wood variations.',
     189.99, 'Home & Living', 15, True),
]

print(f'\nCreating {len(products_data)} products...')

for img_filename, name, description, price, cat_name, stock, is_featured in products_data:
    product, created = Product.objects.get_or_create(
        name=name,
        defaults={
            'description': description,
            'price': price,
            'category': cat_objs[cat_name],
            'stock': stock,
            'is_featured': is_featured,
        }
    )
    if created:
        img_path = os.path.join(MEDIA_PRODUCTS, img_filename)
        if os.path.exists(img_path):
            # Reference the file already present in media/products/ instead of
            # copying it: deterministic name (no random "_XYZ" suffix), which
            # keeps DB -> image paths stable across Render redeploys (images
            # ship inside the git repo and land on the fresh disk each build).
            product.image.name = f'products/{img_filename}'
            product.save(update_fields=['image'])
        print(f'  Product: {name} ({cat_name}, ${price}, stock={stock})')
    else:
        if not product.image:
            img_path = os.path.join(MEDIA_PRODUCTS, img_filename)
            if os.path.exists(img_path):
                product.image.name = f'products/{img_filename}'
                product.save(update_fields=['image'])

print(f'\nProducts: {Product.objects.count()}, Categories: {Category.objects.count()}')