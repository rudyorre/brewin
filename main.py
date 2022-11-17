'''
Usage:
This script will run the brewin interpreter on a provided brewin script
- With no argument provided, the brewin script used will be the variable `script`
- Providing a path to a brewin script file that will be used instead
'''
import interpreterv3 as brewin
import sys

script = '''
func create_lambda x:int func
    lambda y:int int # defines a lambda/closure and stores in resultf
        var int z
        assign z + x y
        return z
    endlambda

    return resultf # return lambda/closure
endfunc

func main void
    var func f
    funccall create_lambda 10
    # assign f resultf

    # funccall f 42
    # funccall print resulti # prints 52
endfunc
'''

def main():
    interpreter = brewin.Interpreter()
    
    if len(sys.argv) == 1:
        interpreter.run(script.split('\n'))
    else:
        pass
        # file = open(sys.argv[1], 'r') if len(sys.argv) > 1 else text
        # interpreter.run([line for line in file.readlines()])
        # file.close()

if __name__ == '__main__':
    main()