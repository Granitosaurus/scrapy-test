# 0.2

- add `EMPTY_IS_MISSING` setting for considering empty values such as `"", [], {}` as missing for coverage.
- add `--save` cli flag for saving test results as json file for further manual debugging.  
- add merging of repeated error messages:

        Item.name: is bad
        Item.name: is bad
        Item.name: is bad
        
    becomes
        
        Item.name: is bad [x3]
        
- add coverage feature to `ItemSpec`.
    Allows to set minimum field coverage percentage. i.e. what % of items should have field present.
    
        class TestItem(ItemSpec):
            item_cls=ProductItem
            id_cov = 100  # 100% - should be present in every item
            twitter_cov = 1  # 10% - unlikely but there definitely should be some values
            
- add `default_test` to `ItemSpec` 
    This is a test that will be applied to every field by default
- add multiple `spider_cls`
- fixed nesting bugs and inconsistencies for heavily nested items
- some refactoring
- add tests for utils

# 0.1

- initial release