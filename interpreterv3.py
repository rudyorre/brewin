import copy
from enum import Enum
from env import EnvironmentManager, SymbolResult
from func import FunctionManager, FuncInfo
from intbase import InterpreterBase, ErrorType
from tokenizer import Tokenizer

class Type(Enum):
    '''Enumerated type for our different language data types.'''
    INT = 1
    BOOL = 2
    STRING = 3
    VOID = 4
    FUNC = 5
    OBJECT = 6

class Value:
  '''Represents a value, which has a type and its value.'''
  def __init__(self, type: Type, value=None):
    self.t = type
    self.v = value

  def value(self):
    return self.v

  def set(self, other):
    self.t = other.t
    self.v = other.v

  def type(self):
    return self.t

class Interpreter(InterpreterBase):
  '''Main interpreter class.'''
  def __init__(self, console_output=True, input=None, trace_output=False):
    super().__init__(console_output, input)
    self._setup_operations()  # setup all valid binary operations and the types they work on
    self._setup_default_values()  # setup the default values for each type (e.g., bool->False)
    self.trace_output = trace_output

  def run(self, program):
    '''Run a program, provided in an array of strings, one string per line of source code.'''
    self.program = program
    self._compute_indentation(program)  # determine indentation of every line
    self.tokenized_program = Tokenizer.tokenize_program(program)
    self.func_manager = FunctionManager(self.tokenized_program)
    self.ip = self.func_manager.get_function_info(InterpreterBase.MAIN_FUNC).start_ip
    self.return_stack = []
    self.terminate = False
    self.env_manager = EnvironmentManager()   # used to track variables/scope

    # Set functions as top-level variables
    for func_name in self.func_manager.func_cache:
      self.env_manager.create_new_symbol(func_name, create_in_top_block=True)
      self.env_manager.set(func_name, Value(Type.FUNC, value=func_name))
    
    # print(self.env_manager.environment)
    # print(self.func_manager.func_cache)
    # main interpreter run loop
    while not self.terminate:
      # print()
      # print(self.env_manager.environment[-1])
      self._process_line()
      # if 'resultf' in self.env_manager.environment[-1][-1]:
      #   print('line:', self.env_manager.environment[-1][0]['resultf'].v.start_ip

  def _process_line(self):
    if self.trace_output:
      print(f"{self.ip:04}: {self.program[self.ip].rstrip()}")
    tokens = self.tokenized_program[self.ip]
    if not tokens:
      self._blank_line()
      return

    args = tokens[1:]

    match tokens[0]:
      case InterpreterBase.ASSIGN_DEF:
        self._assign(args)
      case InterpreterBase.FUNCCALL_DEF:
        self._funccall(args)
      case InterpreterBase.ENDFUNC_DEF:
        self._endfunc()
      case InterpreterBase.IF_DEF:
        self._if(args)
      case InterpreterBase.ELSE_DEF:
        self._else()
      case InterpreterBase.ENDIF_DEF:
        self._endif()
      case InterpreterBase.RETURN_DEF:
        self._return(args)
      case InterpreterBase.WHILE_DEF:
        self._while(args)
      case InterpreterBase.ENDWHILE_DEF:
        self._endwhile(args)
      case InterpreterBase.VAR_DEF: # v2 statements
        self._define_var(args)
      case InterpreterBase.LAMBDA_DEF:
        self._lambda(args)
      case InterpreterBase.ENDLAMBDA_DEF:
        self._endlambda()
      case default:
        raise Exception(f'Unknown command: {tokens[0]}')

  def _blank_line(self):
    self._advance_to_next_statement()

  def _assign(self, tokens):
    if len(tokens) < 2:
      super().error(ErrorType.SYNTAX_ERROR,"Invalid assignment statement")
    vname = tokens[0]
    value_type = self._eval_expression(tokens[1:])

    # Check if a member of an object
    if self._is_member(vname):
      # Create object in env_manager
      # print(self.env_manager.environment[-1][0]['o'].v)
      # quit()=
      self.env_manager.create_new_member_symbol(vname)
      self.env_manager.set(vname, value_type)

    existing_value_type = self._get_value(tokens[0])
    if existing_value_type.type() != value_type.type():
      super().error(ErrorType.TYPE_ERROR,
                    f"Trying to assign a variable of {existing_value_type.type()} to a value of {value_type.type()}",
                    self.ip)
    # If we are assigning a func type variable to another existing variable, the
    # contents of that func variable (function info) must be copied in the func_manager.
    if value_type.type() == Type.FUNC:
      # print('----', tokens[1], vname)
      # print(self.func_manager.func_cache)
      # )
      # self.func_manager.func_cache[vname] = self.func_manager.func_cache[tokens[1]]
      if self.func_manager.is_function(tokens[1]):
        value_type = Value(Type.FUNC, self.func_manager.get_function_info(tokens[1]))
      elif self.env_manager.is_variable(tokens[1]):
        value_type = self.env_manager.get(tokens[1])

    self._set_value(tokens[0], value_type)
    self._advance_to_next_statement()

  def _is_member(self, varname):
    '''
    Checks if a varname is a member of an object by checking if it
    has the dot notation and if the object exists within scope.
    '''
    return len(varname.split('.')) == 2 and self.env_manager.is_variable(varname.split('.')[0])

  def _funccall(self, args):
    if not args:
      super().error(ErrorType.SYNTAX_ERROR,"Missing function name to call", self.ip)
    if args[0] == InterpreterBase.PRINT_DEF:
      self._print(args[1:])
      self._advance_to_next_statement()
    elif args[0] == InterpreterBase.INPUT_DEF:
      self._input(args[1:])
      self._advance_to_next_statement()
    elif args[0] == InterpreterBase.STRTOINT_DEF:
      self._strtoint(args[1:])
      self._advance_to_next_statement()
    else:
      self.return_stack.append(self.ip+1)
      self._create_new_environment(args[0], args[1:])  # Create new environment, copy args into new env
      self.ip = self._find_first_instruction(args[0])

  def _create_new_environment(self, funcname, args):
    '''Create a new environment for a function call.'''
    tmp_mappings = {}

    formal_params = None
    if self.func_manager.is_function(funcname):
      formal_params = self.func_manager.get_function_info(funcname)
    elif self.env_manager.is_variable(funcname):
      env_func = self.env_manager.get(funcname)
      formal_params = env_func.value()
      tmp_mappings[funcname] = env_func
    if formal_params is None:
        super().error(ErrorType.NAME_ERROR, f"Unknown function name {funcname}", self.ip)

    if len(formal_params.params) != len(args):
      super().error(ErrorType.NAME_ERROR,f"Mismatched parameter count in call to {funcname}", self.ip)

    # if function is a method of an object
    if self._is_member(funcname):
      # Push member variables/methods (replacing object name with `this`)
      members = self.env_manager.get_members(funcname.split('.')[0])
      for member in members:
        pass # tmp_mappings[InterpreterBase.THIS_DEF + '.' + member.split('.')[1]] = self.env_manager.get(member)
      # Push object itself as `this`
      # tmp_mappings[InterpreterBase.THIS_DEF] = self.env_manager.get(funcname.split('.')[0])

      tmp_mappings[InterpreterBase.THIS_DEF] = self.env_manager.get(funcname.split('.')[0])

    # For lambdas, push captured variables into new environment
    for (var, var_type, var_name) in formal_params.captured_variables:
      if self.env_manager.is_variable(var_name):
        tmp_mappings[var_name] = copy.copy(self.env_manager.get(var_name))
      else:
        tmp_mappings[var_name] = var

    # Push the parameters (after captured variables because parameters
    # will take precedent and will overwrite the captured variables w/ same symbols).
    for formal, actual in zip(formal_params.params, args):
      formal_name = formal[0]
      formal_typename = formal[1]
      arg = self._get_value(actual)
      if arg.type() != self.compatible_types[formal_typename]:
        super().error(ErrorType.TYPE_ERROR,f"Mismatched parameter type for {formal_name} in call to {funcname}", self.ip)
      if formal_typename in self.reference_types:
        tmp_mappings[formal_name] = arg
      else:
        if arg.type() == Type.FUNC:
          if self.func_manager.is_function(actual):
            arg.v = self.func_manager.get_function_info(actual)
          else:
            arg.v = self.env_manager.get(actual).v
        tmp_mappings[formal_name] = copy.copy(arg)

    # create a new environment for the target function
    # and add our parameters to the env
    self.env_manager.push()
    self.env_manager.import_mappings(tmp_mappings)

  def _endfunc(self, return_val=None):
    if not self.return_stack:  # done with main!
      self.terminate = True
    else:
      # Find name of this function
      # print(self.env_manager.environment[-1][0])
      # print('x' in self.env_manager.environment[-2][0])
      if InterpreterBase.THIS_DEF in self.env_manager.environment[-1][0]:
        this_object = self.env_manager.environment[-1][0][InterpreterBase.THIS_DEF]
        this_name = None
        for (key, value) in self.env_manager.environment[-2][0].items():
          if value is this_object:
            this_name = key
        for (key, value) in self.env_manager.environment[-1][0].items():
          if len(key) > len(InterpreterBase.THIS_DEF) and key[:len(InterpreterBase.THIS_DEF)] == InterpreterBase.THIS_DEF:
            self.env_manager.environment[-2][0][this_name + '.' + key.split('.')[1]] = value

      # Get rid of environment for the function
      self.env_manager.pop()  
      if return_val:
        self._set_result(return_val)
      else:
        # return default value for type if no return value is specified. Last param of True enables
        # creation of result variable even if none exists, or is of a different type
        return_type = self.func_manager.get_return_type_for_enclosing_function(self.ip)
        if return_type != InterpreterBase.VOID_DEF:
          # print('hello:', return_type, self.ip)
          self._set_result(self.type_to_default[return_type])
      self.ip = self.return_stack.pop()

  def _lambda(self, args):
    # TODO: error handling
    lambda_func = FuncInfo(params=[], start_ip=self.ip + 1)
    # Get parameters
    for token in args[:-1]:
      var_name, type_name = token.split(':')
      lambda_func.params.append((var_name, type_name))
    # Get return type
    lambda_func.return_type = args[-1]

    # Dictionary of variables that are used in lambda
    # but are instantiated during the runtime of lambda function.
    new_vars = set()

    # Count how many layers deep we are with nested lambdas within this one.
    depth = 0

    for line_num in range(self.ip + 1, len(self.tokenized_program)):
      tokens = self.tokenized_program[line_num]
      if not tokens:
        continue
      if tokens[0] == InterpreterBase.ENDLAMBDA_DEF and self.indents[self.ip] == self.indents[line_num]:
        self.ip = line_num + 1
        self._set_result(Value(Type.FUNC, lambda_func))
        return
      # elif tokens[0] == InterpreterBase.VAR_DEF:
      #   for token in tokens[2:]:
      #     new_vars.add(token)
      else:
        # for loop to capture all non-parameter variables that are used
        for token in tokens:
          if self.env_manager.is_variable(token): #  and token not in new_vars:
            var = self.env_manager.get(token)
            lambda_func.captured_variables.append((copy.copy(var), var.type(), token))

  def _endlambda(self, return_val=None):
    self._endfunc()
    # self._advance_to_next_statement()

  def _if(self, args):
    if not args:
      super().error(ErrorType.SYNTAX_ERROR,"Invalid if syntax", self.ip)
    value_type = self._eval_expression(args)
    if value_type.type() != Type.BOOL:
      super().error(ErrorType.TYPE_ERROR,"Non-boolean if expression", self.ip)
    if value_type.value():
      self._advance_to_next_statement()
      self.env_manager.block_nest()  # we're in a nested block, so create new env for it
      return
    else:
      for line_num in range(self.ip+1, len(self.tokenized_program)):
        tokens = self.tokenized_program[line_num]
        if not tokens:
          continue
        if tokens[0] == InterpreterBase.ENDIF_DEF and self.indents[self.ip] == self.indents[line_num]:
          self.ip = line_num + 1
          return
        if tokens[0] == InterpreterBase.ELSE_DEF and self.indents[self.ip] == self.indents[line_num]:
          self.ip = line_num + 1
          self.env_manager.block_nest()  # we're in a nested else block, so create new env for it
          return
    super().error(ErrorType.SYNTAX_ERROR,"Missing endif", self.ip)

  def _endif(self):
    self._advance_to_next_statement()
    self.env_manager.block_unnest()

  def _else(self):
    '''
    We would only run this if we ran the successful if block, and fell into the else at the end of the block
    so we need to delete the old top environment.
    '''
    self.env_manager.block_unnest()   # Get rid of env for block above
    for line_num in range(self.ip+1, len(self.tokenized_program)):
      tokens = self.tokenized_program[line_num]
      if not tokens:
        continue
      if tokens[0] == InterpreterBase.ENDIF_DEF and self.indents[self.ip] == self.indents[line_num]:
          self.ip = line_num + 1
          return
    super().error(ErrorType.SYNTAX_ERROR,"Missing endif", self.ip)

  def _return(self,args):
    # do we want to support returns without values?
    return_type = self.func_manager.get_return_type_for_enclosing_function(self.ip)
    default_value_type = self.type_to_default[return_type]
    if default_value_type.type() == Type.VOID:
      if args:
        super().error(ErrorType.TYPE_ERROR,"Returning value from void function", self.ip)
      self._endfunc()  # no return
      return
    if not args:
      self._endfunc()  # return default value
      return

    #otherwise evaluate the expression and return its value
    value_type = self._eval_expression(args)
    if value_type.type() != default_value_type.type():
      super().error(ErrorType.TYPE_ERROR,"Non-matching return type", self.ip)
    self._endfunc(value_type)

  def _while(self, args):
    if not args:
      super().error(ErrorType.SYNTAX_ERROR,"Missing while expression", self.ip)
    value_type = self._eval_expression(args)
    if value_type.type() != Type.BOOL:
      super().error(ErrorType.TYPE_ERROR,"Non-boolean while expression", self.ip)
    if value_type.value() == False:
      self._exit_while()
      return

    # If true, we advance to the next statement
    self._advance_to_next_statement()
    # And create a new scope
    self.env_manager.block_nest()

  def _exit_while(self):
    while_indent = self.indents[self.ip]
    cur_line = self.ip + 1
    while cur_line < len(self.tokenized_program):
      if self.tokenized_program[cur_line][0] == InterpreterBase.ENDWHILE_DEF and self.indents[cur_line] == while_indent:
        self.ip = cur_line + 1
        return
      if self.tokenized_program[cur_line] and self.indents[cur_line] < self.indents[self.ip]:
        break # syntax error!
      cur_line += 1
    # didn't find endwhile
    super().error(ErrorType.SYNTAX_ERROR,"Missing endwhile", self.ip)

  def _endwhile(self, args):
    # first delete the scope
    self.env_manager.block_unnest()
    while_indent = self.indents[self.ip]
    cur_line = self.ip - 1
    while cur_line >= 0:
      if self.tokenized_program[cur_line][0] == InterpreterBase.WHILE_DEF and self.indents[cur_line] == while_indent:
        self.ip = cur_line
        return
      if self.tokenized_program[cur_line] and self.indents[cur_line] < self.indents[self.ip]:
        break # syntax error!
      cur_line -= 1
    # didn't find while
    super().error(ErrorType.SYNTAX_ERROR,"Missing while", self.ip)


  def _define_var(self, args):
    if len(args) < 2:
      super().error(ErrorType.SYNTAX_ERROR,"Invalid var definition syntax", self.ip)
    for var_name in args[1:]:
      if self.env_manager.create_new_symbol(var_name) != SymbolResult.OK:
        super().error(ErrorType.NAME_ERROR,f"Redefinition of variable {args[1]}", self.ip)
      # is the type a valid type?
      if args[0] not in self.type_to_default:
        super().error(ErrorType.TYPE_ERROR,f"Invalid type {args[0]}", self.ip)
      # Create the variable with a copy of the default value for the type
      val = self.type_to_default[args[0]]
      self.env_manager.set(var_name, Value(copy.copy(val.t), copy.copy(val.v)))

    self._advance_to_next_statement()

  def _print(self, args):
    if not args:
      super().error(ErrorType.SYNTAX_ERROR,"Invalid print call syntax", self.ip)
    out = []
    for arg in args:
      val_type = self._get_value(arg)
      out.append(str(val_type.value()))
    super().output(''.join(out))

  def _input(self, args):
    if args:
      self._print(args)
    result = super().get_input()
    self._set_result(Value(Type.STRING, result))   # return always passed back in result

  def _strtoint(self, args):
    if len(args) != 1:
      super().error(ErrorType.SYNTAX_ERROR,"Invalid strtoint call syntax", self.ip)
    value_type = self._get_value(args[0])
    if value_type.type() != Type.STRING:
      super().error(ErrorType.TYPE_ERROR,"Non-string passed to strtoint", self.ip)
    self._set_result(Value(Type.INT, int(value_type.value())))   # return always passed back in result

  def _advance_to_next_statement(self):
    # for now just increment IP, but later deal with loops, returns, end of functions, etc.
    self.ip += 1

  # Set up type-related data structures
  def _setup_default_values(self):
    # set up what value to return as the default value for each type
    self.type_to_default = {}
    self.type_to_default[InterpreterBase.INT_DEF] = Value(Type.INT, 0)
    self.type_to_default[InterpreterBase.STRING_DEF] = Value(Type.STRING, '')
    self.type_to_default[InterpreterBase.BOOL_DEF] = Value(Type.BOOL, False)
    self.type_to_default[InterpreterBase.VOID_DEF] = Value(Type.VOID, None)
    self.type_to_default[InterpreterBase.FUNC_DEF] = Value(Type.FUNC, FuncInfo([], start_ip=None))
    self.type_to_default[InterpreterBase.OBJECT_DEF] = Value(Type.OBJECT, {}) # TODO: object default value?

    # set up what types are compatible with what other types
    self.compatible_types = {}
    self.compatible_types[InterpreterBase.INT_DEF] = Type.INT
    self.compatible_types[InterpreterBase.STRING_DEF] = Type.STRING
    self.compatible_types[InterpreterBase.BOOL_DEF] = Type.BOOL
    self.compatible_types[InterpreterBase.REFINT_DEF] = Type.INT
    self.compatible_types[InterpreterBase.REFSTRING_DEF] = Type.STRING
    self.compatible_types[InterpreterBase.REFBOOL_DEF] = Type.BOOL
    self.compatible_types[InterpreterBase.FUNC_DEF] = Type.FUNC
    self.compatible_types[InterpreterBase.OBJECT_DEF] = Type.OBJECT
    self.reference_types = {InterpreterBase.REFINT_DEF, Interpreter.REFSTRING_DEF,
                            Interpreter.REFBOOL_DEF}

    # set up names of result variables: resulti, results, resultb
    self.type_to_result = {}
    self.type_to_result[Type.INT] = 'i'
    self.type_to_result[Type.STRING] = 's'
    self.type_to_result[Type.BOOL] = 'b'
    self.type_to_result[Type.FUNC] = 'f'
    self.type_to_result[Type.OBJECT] = 'o'

  # run a program, provided in an array of strings, one string per line of source code
  def _setup_operations(self):
    self.binary_op_list = ['+','-','*','/','%','==','!=', '<', '<=', '>', '>=', '&', '|']
    self.binary_ops = {}
    self.binary_ops[Type.INT] = {
     '+': lambda a,b: Value(Type.INT, a.value()+b.value()),
     '-': lambda a,b: Value(Type.INT, a.value()-b.value()),
     '*': lambda a,b: Value(Type.INT, a.value()*b.value()),
     '/': lambda a,b: Value(Type.INT, a.value()//b.value()),  # // for integer ops
     '%': lambda a,b: Value(Type.INT, a.value()%b.value()),
     '==': lambda a,b: Value(Type.BOOL, a.value()==b.value()),
     '!=': lambda a,b: Value(Type.BOOL, a.value()!=b.value()),
     '>': lambda a,b: Value(Type.BOOL, a.value()>b.value()),
     '<': lambda a,b: Value(Type.BOOL, a.value()<b.value()),
     '>=': lambda a,b: Value(Type.BOOL, a.value()>=b.value()),
     '<=': lambda a,b: Value(Type.BOOL, a.value()<=b.value()),
    }
    self.binary_ops[Type.STRING] = {
     '+': lambda a,b: Value(Type.STRING, a.value()+b.value()),
     '==': lambda a,b: Value(Type.BOOL, a.value()==b.value()),
     '!=': lambda a,b: Value(Type.BOOL, a.value()!=b.value()),
     '>': lambda a,b: Value(Type.BOOL, a.value()>b.value()),
     '<': lambda a,b: Value(Type.BOOL, a.value()<b.value()),
     '>=': lambda a,b: Value(Type.BOOL, a.value()>=b.value()),
     '<=': lambda a,b: Value(Type.BOOL, a.value()<=b.value()),
    }
    self.binary_ops[Type.BOOL] = {
     '&': lambda a,b: Value(Type.BOOL, a.value() and b.value()),
     '==': lambda a,b: Value(Type.BOOL, a.value()==b.value()),
     '!=': lambda a,b: Value(Type.BOOL, a.value()!=b.value()),
     '|': lambda a,b: Value(Type.BOOL, a.value() or b.value())
    }

  def _compute_indentation(self, program):
    self.indents = [len(line) - len(line.lstrip(' ')) for line in program]

  def _find_first_instruction(self, funcname):
    func_info = None
    if self.func_manager.is_function(funcname):
      func_info = self.func_manager.get_function_info(funcname)
    elif self.env_manager.is_variable(funcname):
      func_info = self.env_manager.get(funcname).value()
    else:
      print(f'func_info: {func_info}, funcname: {funcname}')
      print(self.env_manager.environment)
    # func_info = self.func_manager.get_function_info(funcname)
    if not func_info:
      super().error(ErrorType.NAME_ERROR,f"Unable to locate {funcname} function")

    if func_info.start_ip == None:
      self._endfunc()
      return self.ip

    return func_info.start_ip

  def _get_value(self, token):
    '''
    Given a token name (e.g., x, 17, True, "foo"), give us a Value object associated
    with it.
    '''
    if not token:
      super().error(ErrorType.NAME_ERROR,f"Empty token", self.ip)
    if token[0] == '"':
      return Value(Type.STRING, token.strip('"'))
    if token.isdigit() or token[0] == '-':
      return Value(Type.INT, int(token))
    if token == InterpreterBase.TRUE_DEF or token == Interpreter.FALSE_DEF:
      return Value(Type.BOOL, token == InterpreterBase.TRUE_DEF)

    # look in environments for variable
    val = self.env_manager.get(token)
    if val != None:
      return val

    # look in func manager for variable
    if self.func_manager.is_function(token):
        return Value(Type.FUNC, self.func_manager.get_function_info(token))
    
    # not found
    super().error(ErrorType.NAME_ERROR,f"Unknown variable {token}", self.ip)

  # given a variable name and a Value object, associate the name with the value
  def _set_value(self, varname: str, to_value_type: Value):
    if self._is_member(varname):
      # If a member variable of an object
      self.env_manager.create_new_member_symbol(varname)
      self.env_manager.set(varname, to_value_type)
    
    value_type = self.env_manager.get(varname)
    if value_type == None:
      super().error(ErrorType.NAME_ERROR,f"Assignment of unknown variable {varname}", self.ip)
    value_type.set(to_value_type)

  # bind the result[s,i,b] variable in the calling function's scope to the proper Value object
  def _set_result(self, value_type):
    # always stores result in the highest-level block scope for a function, so nested if/while blocks
    # don't each have their own version of result
    result_var = InterpreterBase.RESULT_DEF + self.type_to_result[value_type.type()]
    self.env_manager.create_new_symbol(result_var, True)  # create in top block if it doesn't exist
    self.env_manager.set(result_var, copy.copy(value_type))

  def _eval_expression(self, tokens):
    '''Evaluate expressions in prefix notation: + 5 * 6 x.'''
    stack = []

    for token in reversed(tokens):
      if token in self.binary_op_list:
        v1 = stack.pop()
        v2 = stack.pop()
        if v1.type() != v2.type():
          super().error(ErrorType.TYPE_ERROR,f"Mismatching types {v1.type()} and {v2.type()}", self.ip)
        operations = self.binary_ops[v1.type()]
        if token not in operations:
          super().error(ErrorType.TYPE_ERROR,f"Operator {token} is not compatible with {v1.type()}", self.ip)
        stack.append(operations[token](v1,v2))
      elif token == '!':
        v1 = stack.pop()
        if v1.type() != Type.BOOL:
          super().error(ErrorType.TYPE_ERROR,f"Expecting boolean for ! {v1.type()}", self.ip)
        stack.append(Value(Type.BOOL, not v1.value()))
      else:
        value_type = self._get_value(token)
        stack.append(value_type)

    if len(stack) != 1:
      super().error(ErrorType.SYNTAX_ERROR,f"Invalid expression", self.ip)

    return stack[0]
