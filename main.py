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
    var int capture_me
    assign capture_me 42

    if > capture_me 10
        var int capture_me
        assign capture_me 1000
        lambda a:int int
            return + a capture_me    # the captured capture_me’s value is 1000
        endlambda
    endif

    var func f
    assign f resultf
    funccall f 10
    funccall print resulti        # prints 1010
endfunc
'''

def main():
    interpreter = brewin.Interpreter(trace_output=False)
    
    if len(sys.argv) == 1:
        interpreter.run(script.split('\n'))
    else:
        file = open(sys.argv[1], 'r')
        interpreter.run([line for line in file.readlines()])
        file.close()

if __name__ == '__main__':
    main()