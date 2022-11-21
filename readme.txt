Running resultf twice in a function doesn't work for some reason: 
```
func f func
    var int x
    assign x 3
    lambda void
        funccall print x
    endlambda
    
    funccall resultf
    funccall resultf

    return resultf
endfunc

func main void
    funccall f
endfunc
```

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