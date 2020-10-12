(define (problem prob) (:domain blocks)
(:objects 
    A B C D E F - physob
)

(:init
    ;todo: put the initial state's facts and numeric values here
    (clear A) (on A B) (on B C) (ontable C) (ontable D)
    (ontable F) (on E D) (clear E) (clear F)
)

(:goal (and
    ;todo: put the goal condition here
    (clear F) (on F A) (on A C) (ontable C) (clear E)
    (on E B) (on B D) (ontable D)
))

;un-comment the following line if metric is needed
;(:metric minimize (???))
)
