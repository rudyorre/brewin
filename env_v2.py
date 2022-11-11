from enum import Enum

class SymbolResult(Enum):
  OK = 0     # symbol created, didn't exist in top scope
  ERROR = 1  # symbol already exists in top scope

# An improved version of the EnvironmentManager that can manage a separate environment for
# each function as it executes, and has handling for nested blocks within functions
# (so variables can go out of scope once a block enters/exits).
# The internal data structure is essentially a stack (via a python list) of environments
# where each environment on the stack is a list of one or more dictionaries that map a
# variable name to a type/value. We need more than one dictionary to accomodate nested
# blocks in functions.
# If f() calls g() calls h() then while we're in function h, our stack would have
# three items on it: [[{dictionary for f}],[{dictionary for g}][{dictionary for h}]]
class EnvironmentManager:
  def __init__(self):
    self.environment = [[{}]]

  def get(self, symbol):
    nested_envs = self.environment[-1]
    for env in reversed(nested_envs):
      if symbol in env:
        return env[symbol]

    return None

  # create a new symbol in the most nested block's environment; error if
  # the symbol already exists
  def create_new_symbol(self, symbol, create_in_top_block = False):
    block_index = 0 if create_in_top_block else -1
    if symbol not in self.environment[-1][block_index]:
      self.environment[-1][block_index][symbol] = None
      return SymbolResult.OK

    return SymbolResult.ERROR

  # set works with symbols that were already created
  # it won't create a new symbol, only update it
  def set(self, symbol, value):
    nested_envs = self.environment[-1]

    for env in reversed(nested_envs):
      if symbol in env:
        env[symbol] = value
        return SymbolResult.OK

    return SymbolResult.ERROR

  # used only to populate parameters for a function call
  # and populate captured variables; use first for captured, then params
  # so params shadow captured variables
  def import_mappings(self, dict):
    cur_env = self.environment[-1][-1]
    for symbol, value in dict.items():
      cur_env[symbol] = value

  def block_nest(self):
    self.environment[-1].append({})   # [..., [{}]] -> [..., [{}, {}]]

  def block_unnest(self):
    self.environment[-1].pop()

  def push(self):
    self.environment.append([{}])       # [[...],[...]] -> [[...],[...],[]]

  def pop(self):
    self.environment.pop()
