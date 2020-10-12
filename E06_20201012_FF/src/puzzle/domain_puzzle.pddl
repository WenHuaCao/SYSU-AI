;Header and description

(define (domain puzzle)

;remove requirements that are not needed
(:requirements :strips :typing :conditional-effects :equality)

(:types ;todo: enumerate types and their hierarchy here, e.g. car truck bus - vehicle
    num loc
)

; un-comment following line if constants are needed
;(:constants )

(:predicates ;todo: define predicates here
    (at ?x - num ?y - loc)
    (adjecent ?x - loc ?y - loc)
)


; (:functions ;todo: define numeric functions here
; )

;define actions here
(:action slide
    :parameters (?x - num ?y - loc ?z - loc)
    :precondition (and (at ?x ?y) (at num0 ?z) (adjecent ?y ?z))
    :effect (and (at ?x ?z) (at num0 ?y) (not (at ?x ?y)) (not (at num0 ?z)))
)

)