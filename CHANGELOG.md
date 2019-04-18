# 0.5.1
- update how multiple spiders are scheduled 

# 0.5
- add TypeGuard type checking which supports python type annotation like matching: e.g. List\[Union\[str,int\]]
- add `-s` and `-c` flags for overriding config and settings entries respectively
- adjust various get_<config/setting> functions to take optional kwarg of root settings or config object
- change coverage output to be ordered

# 0.4
- rework how cli determines whether a test was success or not
- add `Search` Test
- add Settings optional argument to Validate object 

# 0.3
- change scrapy.cfg module config to `\[test]root=package.module`
- add notification logic
- add slack notifier
- add `required` feature to `StatsSpec`
- update example
- lots of bugifxes and refactoring

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