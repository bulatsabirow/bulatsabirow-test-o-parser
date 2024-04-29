from django.db.models import QuerySet


class ProductQuerySet(QuerySet):
    TELEGRAM_MESSAGE_LENGTH_LIMIT = 4096

    def fetch_numerated_product_messages(self, start=1):
        qs = self.values("name", "url")
        chunk = []
        chunk_length = 0
        for num, product in enumerate(qs, start=start):
            link = f"{num}.<a href='{product.get('url')}'>{product.get('name')}</a>"
            if chunk_length + len(link) >= self.TELEGRAM_MESSAGE_LENGTH_LIMIT:
                yield "\n".join(chunk)
                chunk_length = 0
                chunk = []
            chunk.append(link)
            chunk_length += len(link)

        if len(chunk) > 0:
            yield "\n".join(chunk)
