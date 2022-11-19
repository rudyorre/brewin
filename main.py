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
    funccall print "Hello"
    return resultf # return lambda/closure
endfunc

func create_lambda_2 func
    lambda void
        funccall print "Hello World!"
    endlambda
    return resultf
endfunc

func main void
    lambda x:string y:int int
        funccall print "Hello " x ", you are " y " years old now?"
    endlambda

    funccall resultf "Rudy" 22
    funccall resultf "Cody" 18


    # funccall print resulti # prints 52
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