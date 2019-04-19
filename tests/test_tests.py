from scrapytest.tests import *


def test_Only():
    assert not Only('abc')('abbbcccaaa')
    assert Only('abc')('z')
    assert Only('abc')('abcz')
    assert Only(['a', 'b'])(['a', 'z'])
    assert not Only(['a', 'b'])(['a', 'b'])
    assert Map(Only('abc'))(['a', 'b', 'cd'])
    assert not Map(Only('abc'))(['a', 'b'])


def test_Any():
    assert Any(MoreThan(10), LessThan(8))(9) == ['9 !> 10', '9 !< 8']
    assert not Any(MoreThan(10), LessThan(8))(6)
    assert not Any(MoreThan(10), LessThan(8))(11)


def test_Url():
    assert Url(netloc='foobar.com')('http://foo.com')
    assert not Url(netloc='foobar.com')('http://foobar.com')

    assert Url()('/cats')
    assert not Url(is_absolute=False)('/cats')

    assert Url(path='cats')('http://foobar.com/cat')
    assert not Url(path='cats')('http://foobar.com/cats')
    assert not Url(path='cats+')('http://foobar.com/catssss')

    assert not Url(params='version=1.1')('http://foobar.com/cats;version=1.1')
    assert not Url(query='dog=woof&cat=meow')('http://foobar.com/cats?dog=woof&cat=meow')
    assert not Url(fragment='why-cats-are-delicious')('http://foobar.com/cats#why-cats-are-delicious')

    assert not Any(Url(netloc='foo.com'), Url(netloc='bar.com'))('http://foo.com')
    assert not Any(Url(netloc='foo.com'), Url(netloc='bar.com'))('http://bar.com')


def test_Pass():
    p = Pass()
    assert p() == ''


def test_Type():
    test_int = Type(int)
    assert not test_int(0)
    assert test_int('foo') == "foo is unexpected type <class 'str'>, expected <class 'int'>"
    assert test_int(0.0) == "0.0 is unexpected type <class 'float'>, expected <class 'int'>"
    test_str = Type(str)
    assert test_str(0.0) == "0.0 is unexpected type <class 'float'>, expected <class 'str'>"

    assert Type(int) == Type(int)


def test_Required():
    assert Required()('')
    assert not Required()('foo')


def test_MoreThan():
    assert not MoreThan(100)(101)
    assert MoreThan(100)(100)


def test_LessThan():
    assert LessThan(100)(101)
    assert not LessThan(100)(99)


def test_Equal():
    assert not Equal('foo')('foo')  # looks weird o.O
    assert Equal('foo')('bar')


def test_Len():
    assert Len.less_than(5)(range(100))
    assert not Len.less_than(5)(range(3))
    assert Len.more_than(5)(range(3))
    assert not Len.more_than(5)(range(100))
    assert Len.equals(5)(range(6))
    assert not Len.equals(5)(range(5))


def test_Match():
    assert not Match(r'^foo')('foobar')
    assert Match(r'^bar')('foobar')


def test_Map():
    assert not Map(LessThan(100), MoreThan(50))([55, 98])
    # failure
    assert Map(LessThan(100), MoreThan(50))([55, 999])
    # two failures
    assert len(Map(LessThan(100), MoreThan(50))([0, 150])) == 2
    # assert type errors
    assert Map(LessThan(100), MoreThan(50))(['foo'])
    # assert different errors ?

    assert str(Map(LessThan(10))) == str(LessThan(10))
    assert str(Map(LessThan(10), MoreThan(10))) == str(LessThan(10)) + ',' + str(MoreThan(10))


def test_Compose():
    assert Compose(LessThan(100), MoreThan(50))(110)
    assert not Compose(LessThan(100), MoreThan(50))(80)
    # two failures
    assert len(Compose(MoreThan(100), MoreThan(50))(1)) == 2
    # type errors
    assert Compose(LessThan(100), MoreThan(50))('foo')

    assert str(Compose(LessThan(10))) == str(LessThan(10))
    assert str(Compose(LessThan(10), MoreThan(10))) == str(LessThan(10)) + ',' + str(MoreThan(10))
