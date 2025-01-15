from typing import Iterable, Self, Any
'''
Itérateur d'itérateurs - itérateur composite

Itère au travers des objets passés en paramètre
'''

class CompositeIterator:
    '''Itère parmi les itérateurs passés en paramètre.
    Par exemple, fournit toutes les combinaisons possibles entre n listes.'''
    def __init__(self, *objects: Iterable, right_to_left: bool = True) -> None:
        # Les objets à itérer
        self.__objects = objects
        self.__reverse = right_to_left
        if self.__reverse:
            self.__objects = list(self.__objects)
            self.__objects.reverse()
            self.__objects = tuple(self.__objects)

    def __iter__(self) -> Self:
        self.__iterators = [ iter(obj) for obj in self.__objects ]
        self.__iter_index = 0
        self.__last_result = None
        return self
    
    def __next__(self) -> list[Any]:
        return self.__next_result()

    def __next_result(self) -> list[Any]:
        # Si on n'a pas encore donné de résultat, il est temps d'initialiser tous les itérateurs
        if self.__last_result is None:
            self.__last_result = [ next(i) for i in self.__iterators ]
        else:
            # On essaie d'itérer l'itérateur en cours...
            try:
                self.__last_result[self.__iter_index] = next(self.__iterators[self.__iter_index])
                self.__iter_index = 0
            # ... et si c'est impossible...
            except StopIteration:
                # ... soit on est à la dernière itération du dernier itérateur, auquel cas on arrête les itérations...
                if self.__iter_index == len(self.__iterators) - 1:
                    raise StopIteration
                # ... soit on passe à l'itérateur suivant, en prenant soin de réinitialiser l'itérateur en cours
                else:
                    self.__iterators[self.__iter_index] = iter(self.__objects[self.__iter_index])
                    self.__last_result[self.__iter_index] = next(self.__iterators[self.__iter_index])
                    self.__iter_index += 1
                    self.__next_result()
        # On a un résultat, on en retourne une copie dans l'ordre souhaité
        output = self.__last_result.copy()
        if self.__reverse:
            output.reverse()
        return output
