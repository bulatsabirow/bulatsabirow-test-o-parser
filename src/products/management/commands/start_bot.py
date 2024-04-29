from django.core.management import BaseCommand

from products.telegram.bot import bot


class Command(BaseCommand):
    def handle(self, *args, **options):
        bot.polling()
