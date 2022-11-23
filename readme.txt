I figured that a bug I had is that if a function "x" takes in a lambda function with a parameter with the same symbol "x", it will mess up the program. Realized this with only 6 minutes left and I believe this is the reason why I wasn't able to pass the Church encoding test.

By renaming the variables in the Church encoding test such that none of the parameters have the same name as the function names, it outputs the correct output:
```
# Church encoding
# succ = \n. \f. \x. f (n f x)
func succ n5:func func
  lambda f7:func x8:int int
    funccall n5 f7 x8
    funccall f7 resulti
    return resulti
  endlambda
  return resultf
endfunc

func getnum n3:func int
  lambda x2:int int
    return + x2 1
  endlambda
  funccall n3 resultf 0
  return resulti
endfunc

func main void
  var func zero
  # zero = \f. \x. x
  lambda f1:func x1:int int
    return x1
  endlambda
  assign zero resultf
  
  funccall getnum zero
  funccall print resulti
  
  var func one
  funccall succ zero
  assign one resultf
  funccall getnum one
  funccall print resulti
endfunc
```

Outputs [0, 1] correctly.