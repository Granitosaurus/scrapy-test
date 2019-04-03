from scrapy.settings import Settings
from scrapytest.validate import Validator
from scrapytest.spec import ItemSpec, StatsSpec
from scrapytest import default_settings


def test_Validator():
    settings = Settings()
    settings.setmodule(default_settings)
    validator = Validator([ItemSpec(), StatsSpec()], settings)
    assert validator
    # test default stats
    assert validator.skip_items_without_spec == settings.getbool('SKIP_ITEMS_WITHOUT_SPEC')
    assert validator.skip_stats_without_spec == settings.getbool('SKIP_STATS_WITHOUT_SPEC')
    assert validator.empty_is_missing == settings.getbool('EMPTY_IS_MISSING')
