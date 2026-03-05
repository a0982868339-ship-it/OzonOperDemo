# Initial selectors for Ozon and Wildberries
# These are basic guesses and likely need self-healing immediately.
# But they provide a starting point.

PLATFORM_CONFIGS = {
    "ozon": {
        "url_template": "https://www.ozon.ru/search/?text={keyword}&from_global=true",
        "selectors": {
            "title": "span.tsBody500Medium",  # Example Ozon title class (often changes)
            "price": "span.c3018-a1",        # Example price class
            "rating": "div.b389-a0",         # Example rating
            "reviews": "a.b389-a4",          # Example reviews count
        },
        "goal": "Extract product title, price, rating, and reviews from search results."
    },
    "wildberries": {
        "url_template": "https://www.wildberries.ru/catalog/0/search.aspx?search={keyword}",
        "selectors": {
            "title": ".product-card__name",
            "price": ".price__lower-price",
            "rating": ".product-card__rating",
            "reviews": ".product-card__count",
        },
        "goal": "Extract product title, price, rating, and reviews from search results."
    }
}
