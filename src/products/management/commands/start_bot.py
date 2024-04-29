from django.core.management import BaseCommand

from products.bot.bot import bot


class Command(BaseCommand):
    def handle(self, *args, **options):
        bot.polling()
