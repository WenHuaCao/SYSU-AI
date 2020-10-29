(define (domain boxman)

    (:requirements :strips :typing :equality :universal-preconditions :conditional-effects)
    (:types box loc)

    (:predicates
        (clear ?l - loc) ; nothing in location
        (boxat ?b - box ?l - loc) ; box in location
        (roleat ?l - loc) ; role in location
        (access ?l1 - loc ?l2 - loc) ; loc1 to loc2 accessible
        (rowcol ?l1 - loc ?l2 - loc) ; loc1 and loc2 in the same row or col
    )

    (:action move ; blank to blank
        :parameters (?l1 - loc ?l2 - loc)
        :precondition (and (roleat ?l1) (access ?l1 ?l2) (clear ?l2))
        :effect (and (not (roleat ?l1)) (not (clear ?l2)) (clear ?l1) (roleat ?l2))
    )
    
    (:action push ; push box to blank
        :parameters (?b - box ?l1 - loc ?l2 - loc ?l3 - loc)
        :precondition (and (roleat ?l1) (boxat ?b ?l2) (clear ?l3) (access ?l1 ?l2) (access ?l2 ?l3) (rowcol ?l1 ?l3))
        :effect (and (not (roleat ?l1)) (not (boxat ?b ?l2)) (not (clear ?l3)) (roleat ?l2) (boxat ?b ?l3) (clear ?l1))
    )
    

)