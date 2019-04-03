# Example Crawler

This is example scrapy crawler using scrapy-test implementation.

`/example` is just normal scrapy crawler for https://news.ycombinator.com/  
`/tests` is a scrapy-test directory with `scrapy.cfg` having config setting for the tests.

You can structure the tests any way you want - single module, multiple modules, packages - as long as all the module defined in `scrapy.cfg` has `ItemSpec`, `StatSpect` and `Spider` objects.

see [tests/README.md](./tests/README.md) for this projects tests structure.  
see [scrapy.cfg](./scrapy.cfg) for tests configuration

## Running

Run against live data:

    $ scrapy-test 
    
Run against cached data:

    $ scrapy-test --cache

see [example log](example.log)
