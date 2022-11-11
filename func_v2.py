from intbase import InterpreterBase

class FuncInfo:
  def __init__(self, params, start_ip):
    self.params = params  # format is [[varname1,typename1],[varname2,typename2],...]
    self.start_ip = start_ip    # line number, zero-based

class FunctionManager:
  def __init__(self, tokenized_program):
    self.func_cache = {}
    self.return_types = []  # of each line in the program
    self._cache_function_parameters_and_return_type(tokenized_program)

  # Returns a FuncInfo for the named function or lambda
  # which contains a list of params/types and the start IP of the
  # function's first instruction
  def get_function_info(self, func_name):
    if func_name not in self.func_cache:
      return None
    return self.func_cache[func_name]

  # returns true if the function name is a known function in the program
  def is_function(self, func_name):
    return func_name in self.func_cache

  # generate a synthetic function name for the lambda function, based on
  # the line number where the lambda starts
  def create_lambda_name(line_num):
    return InterpreterBase.LAMBDA_DEF + ':' + str(line_num)

  # returns the return type for the function in question
  def get_return_type_for_enclosing_function(self, line_num):
    return self.return_types[line_num]

  def _to_tuple(self, formal):
    var_type = formal.split(':')
    return (var_type[0], var_type[1])

  def _cache_function_parameters_and_return_type(self, tokenized_program):
    cur_return_type = None
    reset_after_this_line = False
    return_type_stack = [None]  # v3

    for line_num, line in enumerate(tokenized_program):
      if line and line[0] == InterpreterBase.FUNC_DEF:
        # format:  func funcname self.p1:t1 p2:t2 p3:t3 ...
        func_name = line[1]
        params = [self._to_tuple(formal) for formal in line[2:-1]]
        func_info = FuncInfo(params, line_num + 1)  # function starts executing on line after funcdef
        self.func_cache[func_name] = func_info
        return_type_stack.append(line[-1])

      if line and line[0] == InterpreterBase.ENDFUNC_DEF:
        reset_after_this_line = True

      self.return_types.append(return_type_stack[-1])  # each line in the program is assigned a return type based on
                                                 # the function it's associated with; use this to look up valid type
                                                 # for each return
      if reset_after_this_line:                  # for each line with a funcend, make sure we know the return type
        return_type_stack.pop()
        reset_after_this_line = False
