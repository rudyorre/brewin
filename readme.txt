Some weirdness with this code too:
```
# func foo i:int void
    # assign this.val i
    funccall print i
# endfunc

func f func
    var int x
    assign x 3
    lambda void
        funccall print x
    endlambda
    return resultf
endfunc

func main void
    var int x
    assign x 69

    lambda func
        var int y
        assign y 2
        lambda int
            var int x
            assign x 2
            return + x y
        endlambda
        # funccall print x
        return resultf
    endlambda

    funccall f
    var func g
    assign g resultf
    funccall g
    # funccall print resulti
endfunc
```

Make the error here valid:
```
func print_list void

endfunc

func main void
    var object l1 l2 l3
    var object test
    assign l1.val 13
    funccall print l3.val

    # var object l4
    # funccall print l4.val
endfunc
```