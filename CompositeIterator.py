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
        if self.__last_result is None:
            self.__last_result = [ next(i) for i in self.__iterators ]
        else:
            try:
                self.__last_result[self.__iter_index] = next(self.__iterators[self.__iter_index])
                self.__iter_index = 0
            except StopIteration:
                if self.__iter_index == len(self.__iterators) - 1:
                    raise StopIteration
                else:
                    self.__iterators[self.__iter_index] = iter(self.__objects[self.__iter_index])
                    self.__last_result[self.__iter_index] = next(self.__iterators[self.__iter_index])
                    self.__iter_index += 1
                    self.__next_result()
        output = self.__last_result.copy()
        if self.__reverse:
            output.reverse()
        return output
    
class old_CompositeIterator:
    '''Itère plusieurs itérateurs comme un seul itérateur'''

    def __init__(self, *objects: Iterable, right_to_left: bool = True) -> None:
        '''objects : objest à itérer dans l'itérateur'''
        self.__objects = [ obj for obj in objects if obj ]
        # Commnencer l'itération "par la droite" (depuis le dernier objet)
        self.__reverse = right_to_left
        if self.__reverse:
            self.__objects.reverse()
        # Liste des résultats des itérateurs
        self.__resultset = None
        # Liste des iterables depuis les objets
        self.__iterables = [ iter(obj) for obj in self.__objects ]
        # Index du self__iterables à itérer
        self.__iter_index = 0
    
    def __iter__(self) -> None:
        # Réinitialisation des variables
        self.__resultset = None
        self.__iterables = [ iter(obj) for obj in self.__objects ]
        self.__iter_index = 0
        return self
    
    def __next__(self):
        return self.__get_next()
    
    def __get_next(self):
        '''Retourne le prochain itérateur'''
        # Si on n'a pas encore de résultat, on prend le premier élément de chaque itérateur
        if not self.__resultset:
            self.__resultset = [ next(iterator) for iterator in self.__iterables ]
        else:
            # On est en train d'itérer un de nos itérables. On essaie le prochain.
            try:
                self.__resultset[self.__iter_index] = next(self.__iterables[self.__iter_index])
                # On a le prochain de notre itérateur. On repart du premier itérateur.
                self.__iter_index = 0
            except StopIteration:
                # On a atteint la limite de l'itérateur actuel...
                if self.__iter_index == len(self.__iterables) - 1:
                    # ... et c'est le dernier itérateur. On a atteint la fin de toutes les itérations
                    raise StopIteration
                else:
                    # On remet à zéro notre itérateur...
                    self.__iterables[self.__iter_index] = iter(self.__objects[self.__iter_index])
                    # ... on met à jour notre resultset...
                    self.__resultset[self.__iter_index] = next(self.__iterables[self.__iter_index])
                    # ... et on passe à l'itérable suivant
                    self.__iter_index += 1
                    return self.__get_next()
        return self.resultset
    
    @property
    def resultset(self):
        '''Retourne une copie (!) du resultset actuel, à l'envers si besoin'''
        output = self.__resultset.copy()
        if self.__reverse:
            output.reverse()
        return output

if __name__ == '__main__':

    class BinDigit:

        def __iter__(self):
            self.digit = -1
            return self
        
        def __next__(self):
            if self.digit < 1:
                self.digit += 1
                return self.digit
            raise StopIteration

    for bits in CompositeIterator( BinDigit(), range(2), (0, 1) ):
        print(f'{bits} ({int(''.join(list(map(str, bits))), 2)})')