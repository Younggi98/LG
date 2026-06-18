class BaseSite:
    def __init__(self, name, product_list):
        self.name = name
        self.product_list = product_list
        self.completed = set()

    def get_remaining_products(self):
        return [
            p for p in self.product_list
            if p not in self.completed
        ]

    def mark_completed(self, product):
        self.completed.add(product)

    def is_done(self):
        return len(self.completed) >= len(self.product_list)

    def search_product(self, driver, product):
        """
        MUST be implemented by each site
        Should return:
        {
            "site": str,
            "model": str,
            "price": float or str
        }
        """
        raise NotImplementedError("Each site must implement search_product()")
