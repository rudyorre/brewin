from os import makedirs
from os.path import exists
import json
from abc import ABC, abstractmethod
import threading
import _thread as thread

# Test harness; this file is platform agnostic

# TODO:
# - document required structure for test cases: srcfile, name
# - document score output
# - document individual functions :)

class AbstractTestScaffold(ABC):
  @abstractmethod
  def setup(self, test_case):
    pass

  @abstractmethod
  def run_validation(self, test_case, environment):
    pass

  @abstractmethod
  def run_test_case(self, test_case, environment):
    pass

def run_test(scaffold, test_case):
  environment = scaffold.setup(test_case)
  try:
    scaffold.run_validation(test_case, environment)
  except Exception as e:
    print(f'Exception during validation: {e}')
    return 0
  except KeyboardInterrupt:
    print(f'Timeout during validation')
    return 0
  try:
    return scaffold.run_test_case(test_case, environment)
  except Exception as e:
    print(f'Exception during test: {e}')
    return 0
  except KeyboardInterrupt:
    return 0

def run_test_wrapper(interpreter, test_case):
  try:
    print(f'Running {test_case["srcfile"]}... ', end = '')
    result = run_test(interpreter, test_case)
    print(f' {"PASSED" if result else "FAILED"}')
    return result
  except Exception as e:
    print(f'Exception: {e}')
    return 0

def run_all_tests(interpreter, tests):
  print(f'Running {len(tests)} tests...')
  results = list(map(lambda test: {
    'name': test['name'],
    'score': run_test_wrapper(interpreter, test),
    'max_score': 1,
    'visibility': 'visible' if test.get('visible', False) else 'after_published',
  }, tests))
  print(f'{get_score(results)}/{len(tests)} tests passed.')
  return results

def format_gradescope_output(results):
  if type(results) == int or type(results) == float:
    return {
      'score': results
    }
  return {
    'tests': results
  }

def write_gradescope_output(score, is_prod):
  # uses CWD for results.json path if dev; on prod, requires root access
  path = '/autograder/results' if is_prod else '.'
  data = format_gradescope_output(score)
  if not exists(path):
    print(f'{path} does not exist, creating...')
    makedirs(path)
  with open(f'{path}/results.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

def get_score(results):
  return len(list(filter(lambda result: result["score"], results)))


# decorator for timeout, forces a keyboard interrupt after s seconds
# see: https://stackoverflow.com/a/31667005
def exit_after(s):
    '''
    use as decorator to exit process if
    function takes longer than s seconds
    '''
    def outer(fn):
        def inner(*args, **kwargs):
            timer = threading.Timer(s, quit_function, args=[fn.__name__])
            timer.start()
            try:
                result = fn(*args, **kwargs)
            finally:
                timer.cancel()
            return result
        return inner
    return outer


def quit_function(fn_name):
  print('{0} took too long'.format(fn_name), end = '')
  thread.interrupt_main() # raises KeyboardInterrupt
