'''
Usage:
This script will run the brewin interpreter on a provided brewin script
- With no argument provided, the brewin script used will be the variable `script`
- Providing a path to a brewin script file that will be used instead
'''
import interpreterv3 as brewin
import sys

script = '''
func print_list o:object void
    if == o.val 30
        funccall print 30
        return
    endif
    funccall print o.val
    funccall print_list o.next
endfunc

func main void
    var object l1 l2 l3
    assign l1.val 10
    assign l2.val 20
    assign l3.val 30
    assign l1.next l2
    assign l2.next l3
    funccall print_list l1
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