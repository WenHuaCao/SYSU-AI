(define (problem prob) (:domain puzzle)
(:objects 
    num0 num1 num2 num3 num4 num5 num6 num7 num8 - num
    loc1 loc2 loc3 loc4 loc5 loc6 loc7 loc8 loc0 - loc
)

(:init
    ;todo: put the initial state's facts and numeric values here
    (at num1 loc1) (at num2 loc2) (at num3 loc3)
    (at num7 loc4) (at num8 loc5) (at num0 loc6)
    (at num6 loc7) (at num4 loc8) (at num5 loc0)
    (adjecent loc1 loc2) (adjecent loc2 loc1)
    (adjecent loc1 loc4) (adjecent loc4 loc1)
    (adjecent loc2 loc3) (adjecent loc3 loc2)
    (adjecent loc2 loc5) (adjecent loc5 loc2)
    (adjecent loc3 loc6) (adjecent loc6 loc3)
    (adjecent loc4 loc5) (adjecent loc5 loc4)
    (adjecent loc4 loc7) (adjecent loc7 loc4)
    (adjecent loc5 loc6) (adjecent loc6 loc5)
    (adjecent loc5 loc8) (adjecent loc8 loc5)
    (adjecent loc6 loc0) (adjecent loc0 loc6)
    (adjecent loc7 loc8) (adjecent loc8 loc7)
    (adjecent loc8 loc0) (adjecent loc0 loc8)
)

(:goal (and
    ;todo: put the goal condition here
    (at num1 loc1) (at num2 loc2) (at num3 loc3)
    (at num4 loc4) (at num5 loc5) (at num6 loc6)
    (at num7 loc7) (at num8 loc8) (at num0 loc0) 
))

;un-comment the following line if metric is needed
;(:metric minimize (???))
)
