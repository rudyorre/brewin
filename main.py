'''
Usage:
This script will run the brewin interpreter on a provided brewin script
- With no argument provided, the brewin script used will be the variable `script`
- Providing a path to a brewin script file that will be used instead
'''
import interpreterv3 as brewin
import sys

script = '''
func main void
  # var object x

  # assign x.val 42
  # funccall x.val 52        # x.val is an integer, not a func

  var int x
  assign x 42
  funccall x 52
endfunc
'''

def main():
    interpreter = brewin.Interpreter(trace_output=False)
    
    if len(sys.argv) == 1:
        interpreter.run(script.split('\n'))
    else:
        pass
        # file = open(sys.argv[1], 'r') if len(sys.argv) > 1 else text
        # interpreter.run([line for line in file.readlines()])
        # file.close()

if __name__ == '__main__':
    main()