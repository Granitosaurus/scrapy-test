This is example test directory for scrapy-test implementation

The test are separated in 4 different modules for the sake of tidiness:  

* `items.py` - `scrapytest.ItemSpec` item field specifications are defined here for testing item fields
* `stats.py` - `scrapytest.StatsSpec` scrapy sttats feld specifications are defined here for testing finished crawl stats.
* [optionl] `spiders.py` - Extended spider classes here are defined that are used for tests. i.e. crawl only specific urls for tests.  
* `scrapytest.py` - root module where above are imported and extra scrapy settings can be added

Alternatively everything could be defined in one `scrapytest.py` module only.