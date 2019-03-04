from scrapytest.tests import *


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
