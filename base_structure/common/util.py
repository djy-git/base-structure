"""**Utility module**

1. 하위 module들을 사용하는 utility 함수 혹은 class를 정의
2. ``common`` package 내부의 모든 module들을 import 하는 상위 module
"""

from base_structure.common.env import *
from base_structure.common.LoggerFactory import *
from base_structure.common.Timer import *
from base_structure.common.SignalHandler import *
from base_structure.common.DBHandler import *
from base_structure.common.config import *


### Register SIGINT
SignalHandler.register_signal(signal.SIGINT)


class Level:
    """Code의 level(깊이)을 저장하는 class

    :cvar int val: Code의 깊이
    :cvar defaultdict vals: 각 code의 깊이마다 진행도를 저장하는 dict
    """
    val  = 1
    vals = defaultdict(lambda: 1)

    @classmethod
    def step_into(cls):
        """Code의 깊이를 증가
        """
        cls.val += 1
    @classmethod
    def step_out(cls):
        """Code의 깊이를 감소
        """
        cls.val           -= 1
        cls.vals[cls.val] += 1
def L(fn):
    """Code의 level을 관리하는 decorator
    
    사용법
    ::

        @L
        def f():
            ## Level: 1
            g()

        @L
        def g():
            ## Level: 2
            # do something

    :param function fn: 함수
    :return: decorator
    """
    def print_fn(name, args, fn):
        """Code의 level을 출력
        
        :param str name: Code level에 해당하는 이름
        :param tuple args: 함수의 arguments
        :param function fn: 함수
        """
        logs = f"> {name} "
        if len(args) > 0 and isinstance(args[0], object):
            logs = f"{logs}{fn.__module__.split('.')[-1]}."
        logs = f"{logs}{fn.__name__}()"
        LOGGER.info(logs)

    @wraps(fn)
    def log(*args, **kwargs):
        """Code의 level을 출력
        
        :param tuple args: 함수의 arguments
        :param dict kwargs: 함수의 keyword arguments
        :return: 함수의 return value
        """
        name = f"{'.'.join([str(Level.vals[l]) for l in range(1, Level.val+1)]):<15}"

        print_fn(name, args, fn)
        Level.step_into()

        with Timer(name):
            rst = fn(*args, **kwargs)

        Level.step_out()
        return rst
    return log



def tprint(data):
    """Dictionary 혹은 DataFrame을 :func:`tabulate.tabulate` 를 이용하여 출력

    :param data: 출력할 data
    :type data: `dict` | :class:`pandas.DataFrame`
    """
    if isinstance(data, dict):
        data = pd.DataFrame(data, index=['value']).T
    LOGGER.info(tabulate(data, headers='keys', tablefmt='psql'))  # print DataFrame with fancy 'psql' format
