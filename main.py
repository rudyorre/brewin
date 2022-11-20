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
    var func a b c
    funccall a
    funccall print "hello1"
    funccall print "hello2"
    funccall c
    funccall print "hello3"

    lambda x:int y:int z:int bool
        if == x y
            if == y z
                return True
            endif
        endif
        return False
    endlambda

    assign a resultf
    funccall a 1 2 3
    funccall print resultb

    assign b resultf
    funccall b 1 1 1
    funccall print resultb

    
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