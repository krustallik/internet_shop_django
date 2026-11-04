from decimal import Decimal
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from discounts.models import Discount, PromoCode
from main.models import Category, Product
from reviews.models import Review


CATEGORIES = [
    ("audio", "Audio", "Thoughtful sound for work and weekends."),
    ("home", "Home", "Small comforts for your everyday spaces."),
    ("carry", "Carry", "Useful things to take along."),
    ("work", "Work", "Tools for a calmer desk and a clearer mind."),
    ("travel", "Travel", "Lightweight essentials for the road."),
]

PRODUCTS = [
    {
        "slug": "studio-headphones",
        "name": "Studio wireless headphones",
        "category": "audio",
        "description": "Balanced sound, soft ear cushions, and a quiet fit for long listening sessions.",
        "detailed_description": "A comfortable over-ear design for focused work and slow weekends. Includes a USB-C charging cable and a soft carry pouch.",
        "price": "1890.00",
        "image": "demo/products/headphones.svg",
        "views": 842,
        "featured": True,
        "discount": "10",
    },
    {
        "slug": "stoneware-coffee-mug",
        "name": "Stoneware coffee mug",
        "category": "home",
        "description": "A hand-finished ceramic mug with an easy grip and a generous 340 ml capacity.",
        "detailed_description": "Made for everyday coffee and tea. The glazed finish varies slightly from piece to piece. Dishwasher safe.",
        "price": "520.00",
        "image": "demo/products/mug.svg",
        "views": 427,
        "featured": False,
    },
    {
        "slug": "everyday-canvas-tote",
        "name": "Everyday canvas tote",
        "category": "carry",
        "description": "A structured cotton tote with a roomy interior and an inside pocket for smaller items.",
        "detailed_description": "A sturdy daily bag in heavyweight cotton canvas. Fits a notebook, water bottle, and the small things you need nearby.",
        "price": "780.00",
        "image": "demo/products/tote.svg",
        "views": 391,
        "featured": False,
    },
    {
        "slug": "arc-desk-lamp",
        "name": "Arc desk lamp",
        "category": "work",
        "description": "A compact adjustable lamp with a warm, focused pool of light.",
        "detailed_description": "A stable metal base and adjustable shade make this lamp a comfortable companion for reading and desk work.",
        "price": "2450.00",
        "image": "demo/products/lamp.svg",
        "views": 715,
        "featured": True,
        "discount": "15",
    },
    {
        "slug": "insulated-travel-bottle",
        "name": "Insulated travel bottle",
        "category": "travel",
        "description": "A reusable stainless-steel bottle with a leak-resistant screw cap.",
        "detailed_description": "A lightweight 500 ml bottle for commutes and day trips. Hand wash to keep the finish looking its best.",
        "price": "690.00",
        "image": "demo/products/bottle.svg",
        "views": 566,
        "featured": False,
    },
    {
        "slug": "pocket-sketchbook",
        "name": "Pocket sketchbook",
        "category": "work",
        "description": "A cloth-bound notebook with smooth paper for lists, ideas, and quick sketches.",
        "detailed_description": "A lay-flat binding and 160 uncoated pages make it easy to keep notes wherever you are.",
        "price": "340.00",
        "image": "demo/products/notebook.svg",
        "views": 318,
        "featured": False,
    },
    {
        "slug": "pocket-bluetooth-speaker",
        "name": "Pocket Bluetooth speaker",
        "category": "audio",
        "description": "Clear, room-filling sound in a small speaker that is easy to take along.",
        "detailed_description": "A compact wireless speaker with simple controls and a fabric loop. USB-C charging cable included.",
        "price": "1490.00",
        "image": "demo/products/speaker.svg",
        "views": 604,
        "featured": True,
    },
    {
        "slug": "desktop-organizer-tray",
        "name": "Desktop organizer tray",
        "category": "home",
        "description": "A small catchall tray for keys, stationery, and the things that need a home.",
        "detailed_description": "A low-profile organizer with two compartments for everyday desk and entryway essentials.",
        "price": "950.00",
        "image": "demo/products/organizer.svg",
        "views": 289,
        "featured": False,
    },
]


REVIEWS = [
    ("demo.reader.1", "Easy to wear all day", 5, "Comfortable without feeling loose. The sound is clear and balanced, and the battery lasted through my work week."),
    ("demo.reader.2", "A lovely everyday pair", 4, "Good detail for music and calls. The case is simple, and the controls took only a little time to learn."),
    ("demo.reader.3", "A solid desk companion", 5, "The warm light is easy on the eyes and the shade adjusts without slipping. It feels sturdy on a small desk."),
    ("demo.reader.4", "Simple and useful", 5, "The mug has a comfortable handle and a nice weight. It has become my first pick in the morning."),
]


class Command(BaseCommand):
    help = "Create a repeatable English catalog with synthetic products and reviews."

    def handle(self, *args, **options):
        now = timezone.now()
        category_map = {}
        for slug, name, description in CATEGORIES:
            category_map[slug], _ = Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "description": description, "is_active": True},
            )

        product_map = {}
        for data in PRODUCTS:
            product = {
                **data,
                "category": category_map[data["category"]],
                "price": Decimal(data["price"]),
                "is_available": True,
            }
            discount_value = product.pop("discount", None)
            product["image"] = data["image"]
            product_map[data["slug"]], _ = Product.objects.update_or_create(
                slug=data["slug"], defaults=product
            )

            if discount_value:
                Discount.objects.update_or_create(
                    product=product_map[data["slug"]],
                    defaults={
                        "discount_type": Discount.DISCOUNT_TYPE_PERCENTAGE,
                        "value": Decimal(discount_value),
                        "start_date": now - timedelta(days=1),
                        "end_date": now + timedelta(days=30),
                        "is_active": True,
                        "min_quantity": 1,
                        "description": "A limited demo offer",
                    },
                )

        User = get_user_model()
        for username, product_slug, rating, content in [
            ("demo.reader.1", "studio-headphones", 5, REVIEWS[0][3]),
            ("demo.reader.2", "studio-headphones", 4, REVIEWS[1][3]),
            ("demo.reader.3", "arc-desk-lamp", 5, REVIEWS[2][3]),
            ("demo.reader.4", "stoneware-coffee-mug", 5, REVIEWS[3][3]),
        ]:
            author, created = User.objects.get_or_create(
                username=username,
                defaults={"email": f"{username}@example.test"},
            )
            if created:
                author.set_unusable_password()
                author.save(update_fields=["password"])
            review_title = content.split(".", 1)[0][:100]
            Review.objects.update_or_create(
                product=product_map[product_slug],
                author=author,
                defaults={
                    "rating": rating,
                    "title": review_title,
                    "content": content,
                    "advantages": "Comfortable, thoughtfully made, and easy to use.",
                    "disadvantages": "",
                    "is_active": True,
                    "helpful_count": rating * 2,
                },
            )

        PromoCode.objects.update_or_create(
            code="WELCOME10",
            defaults={
                "discount_type": PromoCode.TYPE_PERCENTAGE,
                "value": Decimal("10"),
                "start_date": now - timedelta(days=1),
                "end_date": now + timedelta(days=30),
                "usage_limit": None,
                "used_count": 0,
                "min_order_amount": Decimal("25"),
                "is_active": True,
                "description": "Synthetic showcase code",
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Loaded {len(PRODUCTS)} synthetic products, "
                f"{len(CATEGORIES)} categories, and demo reviews."
            )
        )
