;Header and description

(define (domain blocks)

;remove requirements that are not needed
(:requirements :strips :typing :conditional-effects :equality :universal-preconditions :negative-preconditions)

(:types ;todo: enumerate types and their hierarchy here, e.g. car truck bus - vehicle
    physob
)

; un-comment following line if constants are needed
;(:constants )

(:predicates ;todo: define predicates here
    (ontable ?x - physob)
    (clear ?x - physob)
    (on ?x ?y - physob)
)


; (:functions ;todo: define numeric functions here
; )

;define actions here
(:action move
    :parameters (?x ?y - physob)
    :precondition (and (clear ?x) (clear ?y) )
    :effect (and (on ?x ?y) (not (clear ?y))
        (when (ontable ?x) (not (ontable ?x)))
        (forall (?z - physob) (when (on ?x ?z) (and (not (on ?x ?z)) (clear ?z))))
    )
)

(:action moveToTable
    :parameters (?x - physob)
    :precondition (and (clear ?x) (not (ontable ?x)))
    :effect (and (not (clear ?x)) (ontable ?x)
        (forall (?z - physob) (when (on ?x ?z) (and (not (on ?x ?z)) (clear ?z))))
    )
)


)