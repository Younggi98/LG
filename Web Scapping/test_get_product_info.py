import importlib.util
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("scrape_M_mediamarkt.py")


spec = importlib.util.spec_from_file_location("scrape_M_mediamarkt", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class GetProductInfoTests(unittest.TestCase):
    def test_prefers_discounted_price_and_real_title(self):
        product_text = """
        GBBS322CEV - 60 cm - Wit
        € 499,00
        Nu € 399,00
        """

        result = module.get_product_info(product_text, "GBBS322CEV")

        self.assertIsNotNone(result)
        self.assertEqual(result[0], "GBBS322CEV - 60 cm - Wit")
        self.assertEqual(result[1], "€ 399,00")

    def test_ignores_cashback_amount_when_extracting_price(self):
        product_text = """
        LG F4WX801YB TurboWash
        €50,- cashback
        € 829,–
        €829,00
        """

        result = module.get_product_info(product_text, "F4WX801YB")

        self.assertIsNotNone(result)
        self.assertEqual(result[0], "LG F4WX801YB TurboWash")
        self.assertEqual(result[1], "€ 829,–")


if __name__ == "__main__":
    unittest.main()
