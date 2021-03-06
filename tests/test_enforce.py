import typing
import unittest
import numbers

from enforce import runtime_validation
from enforce.types import EnahncedTypeVar
from enforce.exceptions import RuntimeTypeError


class GeneralTests(unittest.TestCase):
    """
    A container for general tests
    """

    def test_argument_validation(self):
        print(self.sample_function)
        self.assertEqual(self.sample_function('11', 1), 12)

        result = 0
        with self.assertRaises(RuntimeTypeError):
            result += self.sample_function(1, 2)

        self.assertEqual(result, 0)

    def test_return_value_validation(self):
        self.assertIsNone(self.sample_function('', None))

        result = 0
        with self.assertRaises(RuntimeTypeError):
            result += self.sample_function('', 1)

        self.assertEqual(result, 0)

    @runtime_validation
    def sample_function(self, text: str, data: typing.Union[int, None]) -> typing.Optional[int]:
        try:
            return int(text) + data
        except ValueError:
            if data is None:
                return None
            # Deliberate return type error
            return str(data)


class SimpleTypesTests(unittest.TestCase):
    """
    Tests for the simple types which do not require special processing
    """

    def test_any(self):
        @runtime_validation
        def sample(data: typing.Any) -> typing.Any:
            return data

        self.assertEqual(sample(100.3), 100.3)
        self.assertIsNone(sample(None))

    def test_none(self):
        @runtime_validation
        def sample(data: None) -> None:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> None:
            return data

        self.assertIsNone(sample(None))
        with self.assertRaises(RuntimeTypeError):
            sample_bad(1)

    def test_bool(self):
        @runtime_validation
        def sample(data: bool) -> bool:
            return not data

        @runtime_validation
        def sample_bad(data: typing.Any) -> bool:
            return data

        self.assertFalse(sample(True))
        with self.assertRaises(RuntimeTypeError):
            sample(1)

        with self.assertRaises(RuntimeTypeError):
            sample_bad('string')

    def test_int(self):
        @runtime_validation
        def sample(data: int) -> int:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> int:
            return data

        self.assertEqual(sample(1), 1)
        with self.assertRaises(RuntimeTypeError):
            sample(1.0)

        with self.assertRaises(RuntimeTypeError):
            sample_bad('')

    def test_float(self):
        """
        Floats should accept both floats and integers
        """
        @runtime_validation
        def sample(data: float) -> float:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> float:
            return data

        self.assertEqual(sample(1.0), 1.0)
        self.assertEqual(sample(1), 1)
        with self.assertRaises(RuntimeTypeError):
            sample('')

        with self.assertRaises(RuntimeTypeError):
            sample_bad('')

    def test_complex(self):
        """
        Complex numbers should accept complex, integers and floats
        """
        @runtime_validation
        def sample(data: complex) -> complex:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> complex:
            return data

        self.assertEqual(sample(1+1j), 1+1j)
        self.assertEqual(sample(1), 1)
        self.assertEqual(sample(1.0), 1.0)
        with self.assertRaises(RuntimeTypeError):
            sample('')

        with self.assertRaises(RuntimeTypeError):
            sample_bad('')

    def test_string(self):
        @runtime_validation
        def sample(data: str) -> str:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> str:
            return data

        self.assertEqual(sample(''), '')
        with self.assertRaises(RuntimeTypeError):
            sample(1)

        with self.assertRaises(RuntimeTypeError):
            sample_bad(1)

    def test_bytes(self):
        """
        BYtes should accept bytes as well bytearray and memorieview
        """
        @runtime_validation
        def sample(data: bytes) -> bytes:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> bytes:
            return data

        self.assertEqual(sample(b''), b'')
        self.assertEqual(sample(bytearray(2)), bytearray(2))
        self.assertEqual(sample(memoryview(b'')), memoryview(b''))
        with self.assertRaises(RuntimeTypeError):
            sample('')

        with self.assertRaises(RuntimeTypeError):
            sample_bad(1)

    def test_bytearray(self):
        @runtime_validation
        def sample(data: bytearray) -> bytearray:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> bytearray:
            return data

        self.assertEqual(sample(bytearray(2)), bytearray(2))
        with self.assertRaises(RuntimeTypeError):
            sample(b'')

        with self.assertRaises(RuntimeTypeError):
            sample_bad(1)

    def test_memoryview(self):
        @runtime_validation
        def sample(data: memoryview) -> memoryview:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> memoryview:
            return data

        self.assertEqual(sample(memoryview(b'')), memoryview(b''))
        with self.assertRaises(RuntimeTypeError):
            sample(b'')

        with self.assertRaises(RuntimeTypeError):
            sample_bad(1)


class ComplexTypesTests(unittest.TestCase):
    """
    Tests for the simple types which require special processing
    """
    def get_type_var_func(self, configurable=False, type_var=None):
        if type_var is None:
            A = typing.TypeVar('A')
        else:
            A = type_var

        def type_var_func(data: A) -> A:
            return data

        def configurable_type_var_func(data: typing.Any, type_option: A) -> A:
            return data

        if configurable:
            return runtime_validation(configurable_type_var_func)
        else:
            return runtime_validation(type_var_func)

    def test_optional(self):
        @runtime_validation
        def sample(data: typing.Optional[int]) -> typing.Optional[int]:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> typing.Union[int]:
            return data

        self.assertEqual(sample(1), 1)
        self.assertIsNone(sample(None))
        with self.assertRaises(RuntimeTypeError):
            sample('')

        with self.assertRaises(RuntimeTypeError):
            sample_bad('')

    def test_tuple(self):
        @runtime_validation
        def sample(data: typing.Tuple[int, str]) -> typing.Tuple[int, str]:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> typing.Tuple[int, str]:
            return data

        @runtime_validation
        def sample_any_in(data: typing.Tuple) -> typing.Tuple:
            return data

        @runtime_validation
        def sample_any_out(data: typing.Any) -> typing.Tuple:
            return data

        self.assertEqual(sample((1, '')), (1, ''))
        with self.assertRaises(RuntimeTypeError):
            sample((1, 1))

        with self.assertRaises(RuntimeTypeError):
            sample(())

        with self.assertRaises(RuntimeTypeError):
            sample([])

        with self.assertRaises(RuntimeTypeError):
            sample_bad((''))

        self.assertEqual(sample_any_in((1, '')), (1, ''))
        with self.assertRaises(RuntimeTypeError):
            sample_any_in(1)

        self.assertEqual(sample_any_out((1,)), (1,))
        with self.assertRaises(RuntimeTypeError):
            sample_any_out(1)

    def test_variable_length_tuple(self):
        # TODO: What is tuple is empty?
        @runtime_validation
        def sample_in(data: typing.Tuple[int, ...]) -> typing.Any:
            return data

        @runtime_validation
        def sample_out(data: typing.Any) -> typing.Tuple[int, ...]:
            return data
        
        good = (1, 3, 4)
        bad = (1, 'a', 2)
        empty = ()

        self.assertEqual(sample_in(good), good)
        self.assertEqual(sample_out(good), good)
        self.assertEqual(sample_in(empty), empty)
        self.assertEqual(sample_out(empty), empty)

        with self.assertRaises(RuntimeTypeError):
            sample_in(bad)

        with self.assertRaises(RuntimeTypeError):
            sample_out(bad)

    def test_simple_unbounded_type_var(self):
        type_var_func = self.get_type_var_func()
        bad_type_var_func = self.get_type_var_func(configurable=True)

        self.assertEqual(type_var_func(1), 1)
        self.assertEqual(bad_type_var_func('', 'hello world'), '')

        with self.assertRaises(RuntimeTypeError):
            bad_type_var_func('', 1)

    def test_simple_bounded_type_var(self):
        # Invariant case
        A = typing.TypeVar('A', int, str)

        type_var_func = self.get_type_var_func(type_var=A)
        bad_type_var_func = self.get_type_var_func(configurable=True, type_var=A)

        self.assertEqual(type_var_func(1), 1)
        self.assertEqual(type_var_func(''), '')
        self.assertEqual(bad_type_var_func(1, 1), 1)
        self.assertEqual(bad_type_var_func('', ''), '')

        with self.assertRaises(RuntimeTypeError):
            type_var_func(1.0)

        with self.assertRaises(RuntimeTypeError):
            bad_type_var_func(1.0, 1)

    def test_covariant_type_var(self):
        A = typing.TypeVar('A', bound=numbers.Number, covariant=True)

        type_var_func = self.get_type_var_func(type_var=A)

        self.assertEqual(type_var_func(1), 1)
        self.assertEqual(type_var_func(1.0), 1.0)
        self.assertEqual(type_var_func(1+1j), 1+1j)

        with self.assertRaises(RuntimeTypeError):
            type_var_func('bad')

    def test_contravariant_type_var(self):
        class B:
            pass

        class C(B):
            pass

        class D(C):
            pass

        A = typing.TypeVar('A', bound=C, contravariant=True)

        b = B()
        c = C()
        d = D()

        type_var_func = self.get_type_var_func(type_var=A)

        self.assertIs(type_var_func(c), c)
        self.assertIs(type_var_func(b), b)

        with self.assertRaises(RuntimeTypeError):
            type_var_func(d)

    def test_bivariant_type_var(self):
        class B:
            pass

        class C(B):
            pass

        class D(C):
            pass

        A = EnahncedTypeVar('A', bound=C, covariant=True, contravariant=True)

        b = B()
        c = C()
        d = D()

        type_var_func = self.get_type_var_func(type_var=A)

        self.assertIs(type_var_func(c), c)
        self.assertIs(type_var_func(b), b)
        self.assertIs(type_var_func(d), d)

        with self.assertRaises(RuntimeTypeError):
            type_var_func('bad')


class ListTypesTests(unittest.TestCase):
    def setUp(self):
        @runtime_validation
        def str_func(x: typing.List[str]) -> str:
            return x[0]
        self.str_func = str_func

        @runtime_validation
        def int_func(x: typing.List[int]) -> int:
            return x[0]
        self.int_func = int_func

        def int_str_func(x: typing.List[typing.Union[str, int]]) -> int:
            return int(x[0])
        self.union_func = int_str_func

    def test_str_list(self):
        self.str_func(['a'])
        self.str_func(['a', 'b', 'c'])

        with self.assertRaises(RuntimeTypeError):
            self.str_func(3)

        with self.assertRaises(RuntimeTypeError):
            self.str_func('3')

        with self.assertRaises(RuntimeTypeError):
            self.str_func([1, 2, 3])

        with self.assertRaises(RuntimeTypeError):
            self.str_func([1, 'b', 5.0])

        with self.assertRaises(RuntimeTypeError):
            self.str_func(['a', 1, 'b', 5.0])

    def test_int_list(self):
        self.int_func([1])
        self.int_func([1, 2, 3])

        with self.assertRaises(RuntimeTypeError):
            self.int_func(5)

        with self.assertRaises(RuntimeTypeError):
            self.int_func('5')

        with self.assertRaises(RuntimeTypeError):
            self.int_func(['1', '2', 'a'])

        with self.assertRaises(RuntimeTypeError):
            self.int_func(['a', 1, 'b', 5.0])

    def test_union_func(self):
        self.union_func([1])
        self.union_func([1, 2, 3])
        self.union_func(['1'])
        self.union_func(['1', '2', '3'])
        self.union_func([1, '2', 3, '4'])
        self.union_func(['1', 2, '3', 4])

        with self.assertRaises(RuntimeTypeError):
            self.int_func(1)

        with self.assertRaises(RuntimeTypeError):
            self.int_func('a')

        with self.assertRaises(RuntimeTypeError):
            self.int_func([[1, 2, 3], '4'])

        with self.assertRaises(RuntimeTypeError):
            self.int_func(['a', 'b', {3, 4, 5}])


class UnionTypesTests(unittest.TestCase):
    """
    Test case for Union Types
    """

    def setUp(self):
        @runtime_validation
        def test_func(x: typing.Union[float, typing.List[str]]) -> int:
            return 5
        @runtime_validation
        def nest_func(x: typing.Union[float, typing.List[typing.Union[str, int]]]) -> int:
            return 5
        self.test_func = test_func
        self.nest_func = nest_func

    def test_basic_union(self):
        @runtime_validation
        def sample(data: typing.Union[int, str]) -> typing.Union[int, str]:
            return data

        @runtime_validation
        def sample_bad(data: typing.Any) -> typing.Union[int, str]:
            return data

        self.assertEqual(sample(1), 1)
        self.assertEqual(sample(''), '')
        with self.assertRaises(RuntimeTypeError):
            sample(b'')

        with self.assertRaises(RuntimeTypeError):
            sample_bad(1.0)

    def test_good_nested_union(self):
        self.test_func(5.0)
        self.test_func(['1', '2', 'a'])

    def test_bad_nested_union(self):
        with self.assertRaises(RuntimeTypeError):
            self.test_func('a')

        with self.assertRaises(RuntimeTypeError):
            self.test_func([1, 2, 3, 4])

        with self.assertRaises(RuntimeTypeError):
            self.test_func(['a', 4, 5])

    def test_nested_func_good(self):
        self.nest_func(5.0)
        self.nest_func(['a', 'b', 'c'])
        self.nest_func([1, 2, 3])
        self.nest_func([1, 'a', 2, 'b'])

    def test_nested_func_bad(self):
        with self.assertRaises(RuntimeTypeError):
            self.nest_func('a')
        with self.assertRaises(RuntimeTypeError):
            self.nest_func({'a': 5, 'b':6})
        with self.assertRaises(RuntimeTypeError):
            self.nest_func({1, 2, 3, 4})


class ContainerTypesTests(unittest.TestCase):
    """
    Tests for the container types - types of unbounded size
    """
    pass


class IterableTypesTests(unittest.TestCase):
    """
    Tests for iterator and generator support
    """
    pass


class CallableTypesTests(unittest.TestCase):
    """
    Tests for the callable types such as functions
    """
    def setUp(self):
        @runtime_validation
        def test(func: typing.Callable[[int, int], int], x: int) -> int:
            return func(x, x)
        @runtime_validation
        def test_list(func: typing.Callable[[typing.Union[typing.List[typing.Any], int]],
                                            int]) -> int:
            return func(5)
        @runtime_validation
        def union(func: typing.Callable[[typing.Union[float, int], typing.Optional[str]],
                                        int]) -> int:
            return func(5)

        @runtime_validation
        def any_func_args(func: typing.Callable):
            return func

        @runtime_validation
        def any_func_return(func) -> typing.Callable:
            return func

        self.test = test
        self.test_list = test_list
        self.union = union
        self.any_func_args = any_func_args
        self.any_func_return = any_func_return

    # TODO: rename this test
    def test_unrestrained_callable_arguments(self):
        """
        Verifies that a function which expects any Callable as an argument,
        would fail if an object of different type is passed
        """
        callable = lambda x: x
        self.any_func_args(callable)

        with self.assertRaises(RuntimeTypeError):
            self.any_func_args('bad_input')

    # TODO: rename this test
    def test_unrestrained_callable_returns(self):
        """
        Verifies that a function which expects any Callable as an output,
        would fail if an object of different type is returned
        """
        callable = lambda x: x
        self.any_func_return(callable), callable

        with self.assertRaises(RuntimeTypeError):
            self.any_func_return('bad_input')

    def test_good_func_arg(self):
        """ Test that good arguments pass """
        def good(x: int, y: int) -> int:
            return int(x * y)

        self.test(good, 5)

    def test_bad_func_return(self):
        """
        Test that a function being passed in with mismatching return raises
        """
        def bad_return(x: int, y: int) -> float:
            return float(x * y)

        with self.assertRaises(RuntimeTypeError):
            self.test(bad_return, 5)

    def test_bad_func_call(self):
        """
        Test that a function being passed in with mismatching callsig raises
        """
        def bad_callsig(x: str, y: str) -> int:
            return int(x + y)

        with self.assertRaises(RuntimeTypeError):
            self.test(bad_callsig, 5)

    def test_bad_func(self):
        """
        Test that passing in something that's not a function raises
        """
        with self.assertRaises(RuntimeTypeError):
            self.test(5, 5)

    def test_nested_func(self):
        """
        Test that a function with deeply nested types works
        """
        def nest_func(x: typing.Union[int, typing.List[typing.Any]]) -> int:
            return 5
        self.test_list(nest_func)

    def test_nested_bad_func(self):
        """
        Test that a function with bad deeply nested types fails
        """
        def nest_func(x: typing.List[typing.List[int]]) -> int:
            return 5
        with self.assertRaises(RuntimeTypeError):
            self.test_list(nest_func)

    def test_good_union_func(self):
        def good_union(x: typing.Union[float, int], a: typing.Optional[str]=None) -> int:
            print(a)
            return int(x)
        self.union(good_union)

    def test_bad_union_func(self):
        def bad_union(x: float, a=None) -> int:
            return int(x)
        with self.assertRaises(RuntimeTypeError):
            self.union(bad_union)

    def test_good_optional_parameter_func(self):
        def good_param(x: typing.Union[float, int], y: typing.Optional[str] = 'a') -> int:
            return x
        self.union(good_param)

    def test_bad_optional_parameter_func(self):
        def bad_param(x: typing.Union[float, int], y: str = 'b') -> int:
            return x
        with self.assertRaises(RuntimeTypeError):
            self.union(bad_param)


@unittest.skip('Will not be implemented during this release')
class GenericTypesTests(unittest.TestCase):
    """
    Tests for the generic types
    """
    
    def test_custom_generic(self):
        T = typing.TypeVar('T')
        class Sample(typing.Generic[T]):
            def get(self, data: T) -> T:
                return data

        @runtime_validation
        def return_int(data: Sample[int], arg: int) -> int:
            return data.get(arg)

        good = Sample[int]()
        bad = Sample[str]()
        other = Sample()
        strange = Sample[T]()

        print('t:', type(good))
        print('t:', type(bad))
        print('t:', type(other))
        print('t:', type(strange))

        #print(issubclass(type(good), Sample[int]))
        #print(issubclass(type(good), typing.Generic))

        #print(isinstance(type(good), Sample[int]))
        #print(isinstance(type(good), typing.Generic))

        self.assertEqual(return_int(good, 1), 1)

        with self.assertRaises(RuntimeTypeError):
            return_int(bad, 1)


class NestedTypesTests(unittest.TestCase):
    """
    Tests for special and corner cases when types are deeply nested
    """
    pass


if __name__ == '__main__':
    unittest.main()
