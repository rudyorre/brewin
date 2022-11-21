from enum import Enum

class SymbolResult(Enum):
  OK = 0     # symbol created, didn't exist in top scope
  ERROR = 1  # symbol already exists in top scope

class EnvironmentManager:
  '''
  An improved version of the EnvironmentManager that can manage a separate environment for
  each function as it executes, and has handling for nested blocks within functions
  (so variables can go out of scope once a block enters/exits).
  The internal data structure is essentially a stack (via a python list) of environments
  where each environment on the stack is a list of one or more dictionaries that map a
  variable name to a type/value. We need more than one dictionary to accomodate nested
  blocks in functions.
  If f() calls g() calls h() then while we're in function h, our stack would have
  three items on it: [[{dictionary for f}],[{dictionary for g}][{dictionary for h}]]
  '''
  def __init__(self):
    self.environment = [[{}]]

  def get(self, symbol):
    nested_envs = self.environment[-1]
    for env in reversed(nested_envs):
      if self.is_member(symbol):
        obj, mem = symbol.split('.')
        if obj in env:
          return env[obj].value()[mem]
      else:
        if symbol in env:
          return env[symbol]

    return None

  def is_variable(self, symbol):
    nested_envs = self.environment[-1]
    for env in reversed(nested_envs):
      if self.is_member(symbol):
        obj, mem = symbol.split('.')
        if obj in env and mem in env[obj].value():
          return True
      else:
        if symbol in env:
          return True
    return False

  # create a new symbol in the most nested block's environment; error if
  # the symbol already exists
  def create_new_symbol(self, symbol: str, create_in_top_block=False):
    block_index = 0 if create_in_top_block else -1
    if symbol not in self.environment[-1][block_index]:
      self.environment[-1][block_index][symbol] = None
      return SymbolResult.OK

    return SymbolResult.ERROR

  def create_new_member_symbol(self, symbol: str):
    '''
    Given a symbol s thats a member of object o, will update o's dictionary to reflect s.
    '''
    nested_envs = self.environment[-1]
    object_symbol, member_symbol = symbol.split('.')
    for env in reversed(nested_envs):
      if object_symbol in env:
        env[object_symbol].value()[member_symbol] = None
        return SymbolResult.OK
    # Object o in o.s doesn't exist within scope
    return SymbolResult.ERROR

  def is_member(self, varname: str):
    '''
    Checks if a varname is a member of an object by checking if it
    has the dot notation and if the object exists within scope.
    '''
    return len(varname.split('.')) == 2 and self.is_variable(varname.split('.')[0])

  def get_members(self, symbol: str):
    nested_envs = self.environment[-1]
    members = set()
    for env in nested_envs: # we aren't reversing because later instances of the same variable are more valid
      for key in env:
        if len(key.split('.')) == 2 and key.split('.')[0] == symbol and key not in members:
          members.add(key)
    return list(members)

  # set works with symbols that were already created
  # it won't create a new symbol, only update it
  def set(self, symbol, value):
    nested_envs = self.environment[-1]
    for env in reversed(nested_envs):
      if self.is_member(symbol):
        obj, mem = symbol.split('.')
        if obj in env:
          env[obj].value()[mem] = value
          return SymbolResult.OK
      else:
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
