male(george).
male(philip).
male(spencer).
male(charles).
male(mark).
male(andrew).
male(edward).
male(william).
male(harry).
male(peter).
male(james).

female(mum).
female(kydd).
female(elizabeth).
female(margaret).
female(diana).
female(anne).
female(sarah).
female(sophie).
female(zara).
female(beatrice).
female(eugenie).
female(louise).
female(charlotte).

child(elizabeth, george).
child(elizabeth, mum).
child(diana, spencer).
child(diana, kydd).
child(charles, elizabeth).
child(charles, philip).
child(anne, elizabeth).
child(anne, philip).
child(andrew, elizabeth).
child(andrew, philip).
child(edward, elizabeth).
child(edward, philip).
child(william, diana).
child(william, charles).
child(harry, diana).
child(harry, charles).
child(peter, anne).
child(peter, mark).
child(zara, anne).
child(zara, mark).
child(beatrice, andrew).
child(beatrice, sarah).
child(eugenie, andrew).
child(eugenie, sarah).
child(louise, edward).
child(louise, sophie).
child(james, edward).
child(james, sophie).
child(charlotte, william).

spouse(george, mum).
spouse(spencer, kydd).
spouse(elizabeth, philip).
spouse(diana, charles).
spouse(anne, mark).
spouse(andrew, sarah).
spouse(edward, sophie).
spouse(mum, george).
spouse(kydd, spencer).
spouse(philip, elizabeth).
spouse(charles, diana).
spouse(mark, anne).
spouse(sarah, andrew).
spouse(sophie, edward).

grandchild(X, Y) :- child(X, Z), child(Z, Y), male(Z).
greatgrandparent(X, Y) :- grandchild(Y, Z), child(Z, X), male(Z).
ancestor(X, Y) :- child(Y, X); grandchild(Y, X); greatgrandparent(X, Y).
sibling(X, Y) :- male(Z), child(X, Z), child(Y, Z) , \+ (X = Y).
brother(X, Y) :- sibling(X, Y), male(X).
sister(X, Y) :- sibling(X, Y), female(X).
daughter(X, Y) :- child(X, Y), female(X).
son(X, Y) :- child(X, Y), male(X).
firstCousin(X, Y) :- grandchild(X, Z), grandchild(Y, Z), male(Z), \+ (X = Y).
brotherInLaw(X, Y) :- spouse(Y, Z), brother(X, Z).
sisterInLaw(X, Y) :- spouse(Y, Z), sister(X, Z).

mthCousinNremoved(X, Y, 0, 0) :- sibling(X, Y).
mthCousinNremoved(X, Y, M, 0) :- M1 is M-1, child(X, U), child(Y, V), mthCousinNremoved(U, V, M1, 0).
mthCousinNremoved(X, Y, M, N) :- N1 is N-1, child(Y, Z), mthCousinNremoved(X, Z, M, N1).

aunt(X, Y) :- female(X),mthCousinNremoved(X, Y, 0, 1).
uncle(X, Y) :- male(X),mthCousinNremoved(X, Y, 0, 1).