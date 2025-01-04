import operator
from typing import Self, Hashable, Iterable, Callable, Any, NamedTuple
import re

'''
Dataset
Classe de manipulation d'un jeu de données de la forme liste de dictionnaires
Terminologie :
- dataset : liste de dictionnaires
- élément : dictionnaire de la liste de dictionnaires du dataset
- champ : clé d'un élément
- élément courant : élément auqel se trouve l'itération actuelle du dataset
- expression : une expression est définie à un instant et évaluée ultérieurement durant l'exécution
'''

class ExpressionCatcher:
    '''Collection de fonctions de surcharge des opérateurs:
    - de comparaison
    - arithmétiques
    - logiques
    de sorte à les stocker pour une excécution ultérieure.
    Ainsi, si la classe A hérite de cette classe :
    myclass = A()
    myclass + 1
    retourne une expression contenant:
    - l'opérateur operator.add
    - l'instance myclass
    - l'entier 1'''

    def _objstring(self, obj: Any) -> str:
        '''Retourne l'objet obj tel quel sauf si c'est une chaîne,
        auquel cas elle est encadrée par des guillemets simples'''
        if isinstance(obj, str):
            return "'" + obj + "'"
        try:
            return str(obj)
        except:
            return obj
    
    # Surcharge des opérateurs de comparaison
    def __eq__(self, other) -> 'Expression':
        return Expression(operator.eq, self, other, _expression_string_=f'({self._objstring(self)} == {self._objstring(other)})')
    def __ne__(self, other) -> 'Expression':
        return Expression(operator.ne, self, other, _expression_string_=f'({self._objstring(self)} != {self._objstring(other)})')
    def __lt__(self, other) -> 'Expression':
        return Expression(operator.lt, self, other, _expression_string_=f'({self._objstring(self)} < {self._objstring(other)})')
    def __gt__(self, other) -> 'Expression':
        return Expression(operator.gt, self, other, _expression_string_=f'({self._objstring(self)} > {self._objstring(other)})')
    def __le__(self, other) -> 'Expression':
        return Expression(operator.le, self, other, _expression_string_=f'({self._objstring(self)} <= {self._objstring(other)})')
    def __ge__(self, other) -> 'Expression':
        return Expression(operator.ge, self, other, _expression_string_=f'({self._objstring(self)} >= {self._objstring(other)})')

    # Surcharge des opérateurs arithmétiques
    def __add__(self, amount) -> 'Expression':
        return Expression(operator.add, self, amount, _expression_string_=f'({self._objstring(self)} + {self._objstring(amount)})')
    def __radd__(self, amount) -> 'Expression':
        return Expression(operator.add, amount, self, _expression_string_=f'({self._objstring(amount)} + {self._objstring(self)})')
    def __sub__(self, amount) -> 'Expression':
        return Expression(operator.sub, self, amount, _expression_string_=f'({self._objstring(self)} - {self._objstring(amount)})')
    def __rsub__(self, amount) -> 'Expression':
        return Expression(operator.sub, amount, self, _expression_string_=f'({self._objstring(amount)} - {self._objstring(self)})')
    def __mul__(self, amount) -> 'Expression':
        return Expression(operator.mul, self, amount, _expression_string_=f'({self._objstring(self)} * {self._objstring(amount)}')
    def __rmul__(self, amount) -> 'Expression':
        return Expression(operator.mul, amount, self, _expression_string_=f'({self._objstring(amount)} * {self._objstring(self)})')
    def __truediv__(self, amount) -> 'Expression':
        return Expression(operator.truediv, self, amount, _expression_string_=f'({self._objstring(self)} / {self._objstring(amount)}')
    def __rtruediv__(self, amount) -> 'Expression':
        return Expression(operator.truediv, amount, self, _expression_string_=f'({self._objstring(amount)} / {self._objstring(self)})')
    def __floordiv__(self, amount) -> 'Expression':
        return Expression(operator.floordiv, self, amount, _expression_string_=f'({self._objstring(self)} // {self._objstring(amount)}')
    def __rfloordiv__(self, amount) -> 'Expression':
        return Expression(operator.floordiv, amount, self, _expression_string_=f'({self._objstring(amount)} // {self._objstring(self)})')
    def __mod__(self, amount) -> 'Expression':
        return Expression(operator.mod, self, amount, _expression_string_=f'({self._objstring(self)} % {self._objstring(amount)}')
    def __rmod__(self, amount) -> 'Expression':
        return Expression(operator.mod, amount, self, _expression_string_=f'({self._objstring(amount)} % {self._objstring(self)})')
    
    # Surcharge des opérateurs logiques
    def __and__(self, other: Self) -> 'Expression':
        return Expression(operator.and_, self, other, _expression_string_=f'({self._objstring(self)} AND {self._objstring(other)})')
    def __or__(self, other: Self) -> 'Expression':
        return Expression(operator.or_, self, other, _expression_string_=f'({self._objstring(self)} OR {self._objstring(other)})')
    def __invert__(self) -> 'Expression':
        return Expression(operator.not_, self, _expression_string_=f'(NOT {self._objstring(self)})')
    
    # Fonctions ne pouvant pas être surchargées
    def in_(self, items: Iterable) -> 'Expression':
        return Expression(operator.contains, items, self, _expression_string_=f'({self._objstring(self)} IN {self._objstring(items)})')
    def is_(self, objtype: type) -> 'Expression':
        return Expression(operator.is_, self, objtype, _expression_string_=f'({self._objstring(self)} IS {self._objstring(objtype)})')
    def func(self, operator: Callable, *args, **kwargs) -> 'Expression':
        return Expression(operator, self, *args, **kwargs)

class Expression(ExpressionCatcher):
    '''Permet de stocker une expression pour une exécution ultérieure'''

    def __init__(self, operator: operator, *args: Any, _expression_string_: str=None, **kwargs: any) -> None:
        '''operator: opérateur à utiliser pour calculer l'expression
        args : les arguments positionnels à passer à operator
        kwargs : les arguments nommés à passer à operator
        _expression_string_ : remplace la chaîne envoyée par défaut par __str__'''
        self.__operator = operator
        self.__args: list = args
        self.__kwargs: dict = kwargs
        self.__name: str = None
        self.__alias: str = None
        self.__string: str = _expression_string_
    
    def __repr__(self) -> str:
        output = f'<{__class__.__name__}'
        if self.__name:
            output += f'`{self.__name}`'
        else:
            output += ' unnamed'
        if self.__alias:
            output += f' alias `{self.__alias}`'
        output += '>'
        return output
    
    def __str__(self):
        if self.__string is None:
            argstring = [ ]
            if self.__args:
                argstring.append( ', '.join(map(lambda x: str(x), self.__args)))
            if self.__kwargs:
                argstring += [ f'{key}={self._objstring(value)}' for key, value in self.__kwargs.items() ]
            argstring = ', '.join(argstring)
            try:
                operator_name = self.__operator.__name__
            except:
                operator_name = self.__operator
            string = f'{operator_name}({argstring})'
        else:
            string = self.__string
        if self.__alias:
            string += f' AS `{self.__alias}`'
        return string
            
    @property
    def value(self) -> Any:
        '''Retourne la valeur de l'expression'''
        args = [ ]
        for arg in self.__args:
            if isinstance(arg, (__class__, DatasetField)):
                args.append(arg.value)
            else:
                args.append(arg)
        kwargs = { }
        for key, value in self.__kwargs.items():
            if isinstance(value, (__class__, DatasetField)):
                kwargs.update({ key: value.value })
            else:
                kwargs.update({ key: value })
        try:
            return self.__operator(*args, **kwargs)
        except Exception as E:
            # print(f'Caught Exception {E}')
            return None
    
    @property
    def match(self) -> bool:
        '''Retourne True si la valeur de l'expression est exactement True.
        Sinon retourne False'''
        if self.value == True:
            return True
        return False
    
    def set_name(self, name: str) -> Self:
        '''Nommage de l'expression'''
        self.__name = name
        return self
    
    def as_(self, alias: Hashable) -> Self:
        '''Affectation d'un alias à l'expression'''
        self.__alias = alias
        return self

    @property
    def name(self) -> str:
        return self.__name
    @property
    def alias(self) -> str:
        if self.__alias:
            return self.__alias
        return self.__name
    
    def cast_as(self, cast_type: type) -> 'Expression':
        '''Transtypage de l'expression'''
        return __class__(cast_type, self, _expression_string_=f'CAST({str(self)} AS {cast_type.__name__})')
        
class DatasetField(ExpressionCatcher):
    '''Class de manipulation des champs d'un dataset'''

    def __init__(self, dataset: 'Dataset', name: Hashable) -> None:
        '''Un champ :
        - est rattaché à son dataset
        - peut avoir un nom
        - peut avoir un alias'''
        self.__dataset: Dataset = dataset
        self.__name: str = name
        self.__alias: str = None
    
    def __repr__(self) -> str:
        string = f'<{self.__class__.__name__} {str(self.__dataset)}.`{self.__name}`'
        if self.__alias:
            string += f' alias `{self.__alias}`'
        string += '>'
        return string
    
    def __str__(self) -> str:
        string = str(self.__dataset) + f'.`{self.__name}`'
        if self.__alias:
            string += f' AS `{self.__alias}`'
        return string
    
    def __attributes(self):
        return (self.__dataset, self.__name, self.__alias)
    
    def __hash__(self) -> int:
        return hash(self.__attributes)
    
    @property
    def name(self) -> str:
        return self.__name
    @property
    def alias(self) -> str:
        if self.__alias:
            return self.__alias
        return self.__name
    
    @property
    def value(self) -> Any:
        '''Retourne la valeur associée à la clé du dictionnaire courant du dataset.
        Cette clé est le nom du champ. L'élément courant est défini dans le dataset.'''
        return self.__dataset.current_element.data.get(self.__name, None)
    
    @property
    def exists(self) -> Expression:
        '''Retourne l'expression permettant de tester la présence d'une clé dans l'élément courant'''
        return Expression(self.__exists, _expression_string_=f'EXISTS({str(self)})')
    
    def __exists(self) -> bool:
        '''True si le champs existe dans l'élément courant'''
        return self.name in self.__dataset.current_element.data
    
    def cast_as(self, datatype: type) -> Expression:
        '''Retourne l'expression de transtypage du champ de l'élément courant'''
        return Expression(datatype, self, _expression_string_=f'CAST({str(self)} AS {datatype.__name__})').set_name(self.name)
    
    def as_(self, alias: Hashable) -> Self:
        '''Définition de l'alias du champ'''
        self.__alias = alias
        return self

    def like(self, regex: str, flag: re=re.NOFLAG) -> Self:
        '''Retourne une expression permettant de comparer l'élément actuel à une regex
        On peut spécifier le flag regex Python pour modifier le comportement de la regex - https://docs.python.org/3/library/re.html#flags'''
        return Expression(bool, Expression(re.match, regex, self, flag, _expression_string_=''), _expression_string_=f"{self} LIKE '{regex}' ({flag})")
    
class DatasetElement(NamedTuple):
    '''Elément d'un dataset
    - index : index de l'élément dans la liste de dictionnaires constituant le dataset
    - dataset : la liste des dictionnaires'''
    index: int
    dataset: list[dict]

    @property
    def data(self):
        '''Retourne le dictionnaire de l'élément actuel'''
        if self.index >= 0:
            return self.dataset[self.index]
        return None

    def delete(self) -> None:
        '''Efface l'élément du dataset'''
        del self.dataset[self.index]
    
    def drop(self, field: DatasetField) -> None:
        '''Supprime le champ de l'élément s'il existe'''
        if field.name in self.data:
            del self.data[field.name]

class Dataset:
    '''Classe de gestion d'une liste de dictionnaires'''

    def __init__(self, dataset: list[dict], name=None) -> None:
        '''dataset : liste de dictionnaires
        name: nom du dataset'''
        self.__dataset = dataset
        self.__name = name
        # Elément en cours
        self.__current_element: DatasetElement = None
    
    def __len__(self) -> int:
        return len(self.__dataset)
    
    def __repr__(self) -> str:
        string = f'<{__class__.__name__} '
        if self.__name:
            string += f'`{self.__name}`'
        else:
            try:
                string += f'#{hash(self)}'
            except TypeError:
                string += '(unnamed)'
        string += '>'
        return string

    def __str__(self) -> str:
        if self.__name:
            return f'`{self.__name}`'
        else:
            try:
                auto_name = f'#{str(hash(self))}'
            except TypeError:
                auto_name = 'Unnamed'

        return f'`{self.__class__.__name__}_{auto_name}`'
    
    # Accès aux DatasetField via notation objet ou dictionnaire
    def __getattr__(self, field: Hashable) -> DatasetField:
        return DatasetField(dataset=self, name=field)
    def __getitem__(self, field: Hashable) -> DatasetField:
        return DatasetField(dataset=self, name=field)
    
    # Itération : retourne un DatasetElement composé de l'index et du dictionnaire correspondant
    def __iter__(self) -> Self:
        self.__current_element = DatasetElement(index=-1, dataset=self.__dataset)
        return self
    def __next__(self) -> DatasetElement:
        if self.__current_element.index < len(self.__dataset) - 1:
            self.__current_element = DatasetElement(index=self.__current_element.index + 1, dataset=self.__dataset)
            return self.__current_element
        raise StopIteration
    
    def __iadd__(self, other: 'Dataset') -> Self:
        if not isinstance(other, Dataset):
            raise TypeError(f'Can only add another {__class__.__name__}')
        self.__dataset += other.raw_dataset
        return self

    def __add__(self, other: 'Dataset') -> Self:
        if not isinstance(other, Dataset):
            raise TypeError(f'Can only add another {__class__.__name__}')
        joined_dataset = self.__dataset.copy()
        joined_dataset += other.raw_dataset
        return __class__(joined_dataset)

    @property
    def current_element(self) -> DatasetElement:
        return self.__current_element
    @property
    def raw_dataset(self) -> list[dict]:
        return self.__dataset
    
    def set_name(self, name: str) -> Self:
        self.__name = name
        return self

    def to_table(self, separator: str=' | ', maxwidth: int=0) -> None:
        '''Affiche le dataset sous forme d'un tableau formaté'''
        # On commence par trouver les noms des colonnes et la plus grande largeur de chacune
        def columnsize(element: Any) -> int:
            '''Retourne la longueur de str(element) ou maxwidth'''
            size = len(str(element))
            if maxwidth > 0 and size > maxwidth:
                return maxwidth
            return size
        
        def value_size(value: Any, size: int, justify: str='left') -> str:
            value = str(value)
            if len(value) > size:
                value = value[:size-3] + '...'
            match justify:
                case 'center':
                    return value.center(size)
                case 'right':
                    return value.rjust(size)
                case _:
                    return value.ljust(size)
        
        def dataline(line: str) -> str:
            return f'{separator.lstrip()}{line}{separator.rstrip()}'

        columns = { }
        for element in self.__dataset:
            # for key, value in self.current_element.data.items():
            for key, value in element.items():
                if key not in columns:
                    columns[key] = columnsize(key)
                if len(str(value)) > columns[key]:
                    columns[key] = columnsize(value)

        # On crée la ligne de séparation horizontale, elle va servir trois fois...
        table_width = sum(columns.values())
        table_width += (len(columns) - 1) * len(separator)
        table_width += len(separator.lstrip()) + len(separator.rstrip())

        horizontal_line = '-' * table_width

        # On peut afficher l'en-tête...
        header_columns = [ ]
        for column, size in columns.items():
            header_columns.append(value_size(column, size, justify='center'))
        print(horizontal_line)
        print(dataline(separator.join(header_columns)))
        print(horizontal_line)

        # ... et les lignes
        for element in self.__dataset:
            line_chunks = [ ]
            for column, size in columns.items():
                if column in element:
                    if isinstance(element[column], (int, float)):
                        value = value_size(element[column], size, justify='right')
                    else:
                        value = value_size(element[column], size)
                else:
                    value = value_size('', size)
                line_chunks.append(value)
            print(dataline(separator.join(line_chunks)))
        print(horizontal_line)
