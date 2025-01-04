'''
De quoi faire des requêtes du genre SQL sur des datasets
'''
from typing import NamedTuple, Self, Any

from QuerySyntax import Syntax, SelectQuerySyntax, UpdateQuerySyntax, DeleteQuerySyntax, DropQuerySyntax
from Dataset import Dataset, DatasetField, Expression
from CompositeIterator import CompositeIterator

'''
Fonctions et classes "publiques"
'''

def select(*select_fields: DatasetField | Expression) -> '_SelectQuery':
    '''Initiateur d'une requête SELECT'''
    return _SelectQuery(*select_fields)

def update(dataset: DatasetField) -> '_UpdateQuery':
    '''Initiateur d'une requête UPDATE'''
    return _UpdateQuery(dataset)

def delete() -> '_DeleteQuery':
    '''Initiateur d'une requête DELETE'''
    return _DeleteQuery()

def alter(dataset: Dataset) -> '_AlterQuery':
    '''Initiateur d'une requête ALTER'''
    return _AlterQuery(dataset)

def asc(sort_key: DatasetField | Expression) -> Expression:
    '''Inutile, permet de clarifier la syntaxe des clés de tri si utilisé'''
    return Expression(lambda x: x, sort_key, _expression_string_=f'{sort_key} ASC')

def desc(sort_key: DatasetField | Expression) -> Expression:
    '''Permet de créer une clé de tri en ordre descendant'''
    return Expression(_DescOrder, sort_key, _expression_string_=f'{sort_key} DESC')

class UpdateElement(NamedTuple):
    '''Eléments d'une requête UPDATE : champ et nouvelle valeur du champ'''
    field: DatasetField
    value: Any

    def __str__(self) -> str:
        return f'{self.field} = {self.value}'

'''
Fonctions et classes "privées"
'''

class _DescOrder:
    '''Classe permettant d'inverser l'ordre de tri'''
    def __init__(self, obj):
        self.obj = obj
    def __eq__(self, other):
        return self.obj == other.obj
    def __lt__(self, other):
        # On inverse le résultat du comparateur lt
        return self.obj > other.obj
    def __gt__(self, other):
        # On inverse le résultat du comparateur gt - Inutile en principe
        return self.obj < other.obj
    def __repr__(self):
        return f'<{__class__.__name__}: descending sort for {self.obj}>'

class _Clauses:
    '''Classe d'évaluation d'une liste de clauses'''
    def __init__(self, *clauses: Expression) -> None:
        self.__clauses = clauses
    
    @property
    def match(self) -> bool:
        '''Retourne True si toutes les clauses sont True, sinon False'''
        if self.__clauses:
            for clause in self.__clauses:
                if clause and not clause.match:
                    return False
        return True

class _Term:
    '''Classe d'évaluation d'un terme : champ, expression ou autre'''
    def __init__(self, term: Any):
        self._term = term
    
    @property
    def value(self):
        if isinstance(self._term, DatasetField):
            return self._term.value
        elif isinstance(self._term, Expression):
            return self._term.value
        else:
            return self._term

class _JoinClause(NamedTuple):
    '''Eléments d'une clause JOIN : dataset et clause (optionnelle)'''
    dataset: Dataset
    clause: Expression = None

class _DatasetQuery:
    '''Classe de base des dataset queries
    Comporte les éléments communs à plusieurs requêtes
    Les autres classes doivent définir:
    - self._syntax, la syntaxe de la requête
    - les variables de leurs requêtes'''

    # Chaîne de l'indentation des méthodes explain
    _indent: str = '    '
    # Nom du champ temporaire stockant la clé de tri d'un dataset résultant d'une requête
    _temp_sort_key: str = f'{__name__} temporary sort key'

    def __init__(self) -> None:
        self._from: Dataset = None
        self._where: Expression = None
        self._syntax: Syntax = None

    def from_(self, dataset: Dataset) -> Self:
        '''Configuration de l'expression FROM'''
        self._syntax.add_keyword('from')
        self._from = dataset
        return self
    
    def where(self, clause: Expression) -> Self:
        '''Configuration de l'expression WHERE'''
        self._syntax.add_keyword('where')
        self._where = clause
        return self

    def _explain_where(self, pretty: bool=False) -> str:
        '''Retourne la chaîne explicative  de l'expression WHERE'''
        if self._where:
            if pretty:
                return f'WHERE\n{self._indent}{self._where}'
            return f'WHERE {self._where}'
        return ''
    
    def _explain_from(self, pretty: bool=False) -> str:
        '''Retourne la chaîne explicative  de l'expression FROM'''
        if pretty:
            return f'FROM\n{self._indent}{self._from}'
        return f'FROM {self._from}'
    
class _SelectQuery(_DatasetQuery):
    '''De quoi faire une requête SELECT sur un dataset'''

    def __init__(self, *selected: DatasetField | Expression) -> None:
        super().__init__()
        self._selected: list[DatasetField|Expression] = selected
        self._join: list[_JoinClause] = [ ]
        self._where: Expression = None
        self._order_by: list[Expression] = [ ]
        self._limit: int = None
        self._syntax: SelectQuerySyntax = SelectQuerySyntax()
        self._syntax.add_keyword('select')

    def __str__(self):
        return self.explain(pretty=False)
    
    '''
    Mots-clés de la requête SELECT
    '''

    def join(self, dataset: Dataset, on_clause: Expression = None) -> Self:
        '''Configuration de l'expression JOIN'''
        self._syntax.add_keyword('join')
        self._join.append(_JoinClause(dataset=dataset, clause=on_clause))
        return self
    
    def on(self, on_clause: Expression) -> Self:
        '''Configuration de l'expression ON
        Nécessite qu'un JOIN sans clause ait été déclaré juste avant'''
        self._syntax.add_keyword('on')
        if not self._join:
            raise SyntaxError('ON clause without JOIN statement')
        if self._join[-1].clause is not None:
            raise SyntaxError('ON clause already defined for last JOIN')
        last_join = self._join.pop()
        self._join.append(_JoinClause(dataset=last_join.dataset, clause=on_clause))
        return self

    def order_by(self, *sort_keys: DatasetField | Expression) -> Self:
        '''Configuration de l'expression ORDER_BY'''
        self._syntax.add_keyword('order_by')
        self._order_by = sort_keys
        return self
    
    def limit(self, limit: int) -> Self:
        '''Configuration de l'expression LIMIT'''
        self._syntax.add_keyword('limit')
        self._limit = limit
        return self
    
    '''
    Explain
    '''

    def _explain_selected(self, pretty: bool=True) -> str:
        '''Retourne la chaîne explicative des champs mentionnés dans l'expression SELECT'''
        explanation = 'SELECT'
        if not self._selected:
            explanation += ' *'
        else:
            if pretty:
                explanation += '\n'
                selected_strings = list(map(lambda x: self._indent + str(x), self._selected))
                explanation += ',\n'.join(selected_strings)
            else:
                explanation += ' '
                selected_strings = list(map(str, self._selected))
                explanation += ', '.join(selected_strings)
        return explanation

    def _explain_join(self, pretty: bool=False) -> str:
        '''Retourne la chaîne explicative des datasets mentionnés dans l'expression JOIN[ ON]'''
        if self._join:
            joins = [ ]
            for join in self._join:
                string = ''
                if pretty:
                    string = self._indent
                string += f'JOIN {join.dataset}'
                if join.clause:
                    string += f' ON {join.clause}'
                joins.append(string)
            if pretty:
                return '\n'.join(joins)
            return ' '.join(joins)
        return ''
    
    def _explain_order_by(self, pretty: bool=False) -> str:
        '''Retourne la chaîne explicative des clés de tri mentionnées dans l'expression ORDER_BY'''
        if self._order_by:
            string = 'ORDER BY'
            if pretty:
                string += '\n'
            else: string += ' '
            sort_keys = list(map(str, self._order_by))
            if pretty:
                sort_keys = list(map(lambda x: self._indent + x, sort_keys))
                return string + ',\n'.join(sort_keys)
            return string + ', '.join(sort_keys)
        return ''
    
    def _explain_limit(self):
        '''Retourne la chaîne explicative de l'expression SELECT'''
        if self._limit:
            return f'LIMIT {self._limit}'
        return ''

    def explain(self, pretty: bool=True) -> str:
        '''Retourne l'explication de l'ensemble de la requête'''
        explanation = [ self._explain_selected(pretty=pretty) ]
        explanation.append(self._explain_from(pretty=pretty))
        explanation.append(self._explain_join(pretty=pretty))
        explanation.append(self._explain_where(pretty=pretty))
        explanation.append(self._explain_order_by(pretty=pretty))
        explanation.append(self._explain_limit())
        explanation = filter(None, explanation)
        if pretty:
            return '\n'.join(explanation)
        else:
            return ' '.join(explanation)

    '''
    Exécution de la requête
    '''
    
    def execute(self):
        if self._syntax.check():
            resultset = [ ]
            # On prend tous les datasets de la requête
            datasets = [ self._from ] + [ join.dataset for join in self._join ]
            # ... et on les itère pour créer le dataset résultant de la requête
            for results in CompositeIterator(*datasets):
                element = { }
                # Si les clauses join sont remplies
                join_clauses = [ join.clause for join in self._join if join.clause is not None ]
                if _Clauses(*join_clauses).match:
                    # ... et que les clauses where sont remplies
                    if _Clauses(self._where).match:
                        # ... on récupère les champs ou objets sélectionnés
                        if not self._selected:
                            # Aucun champ n'est sélectionné, on retourne TOUT
                            for result in results:
                                element.update(result.data)
                        else:
                            # On s'occupe de chaque champs sélectionné
                            for selected in self._selected:
                                element.update({ selected.alias: _Term(selected).value })
                        # Si on a un tri à faire, on ajoute la clé temporaire de tri
                        if self._order_by:
                            sort_keys = [ _Term(x).value for x in self._order_by ]
                            element.update({ self._temp_sort_key: tuple(sort_keys) })
                        # L'élément est créé, on ajoute SA COPIE au résultat
                        resultset.append(element.copy())
            # On a les éléments du résultat, on les trie si nécessaire...
            if self._order_by:
                resultset.sort(key=lambda x: x[self._temp_sort_key])
            # ... on applique la limite si nécessaire...
            if self._limit:
                resultset = resultset[:self._limit]
            # ... on supprime la clé temporaire de tri si nécessaire
            if self._order_by:
                for element in resultset:
                    del element[self._temp_sort_key]
            # ... et on retourne le dataset
            return Dataset(resultset)

class _UpdateQuery(_DatasetQuery):
    '''De quoi faire une requête UPDATE sur un dataset '''

    def __init__(self, dataset: Dataset) -> None:
        super().__init__()
        self._dataset: Dataset = dataset
        self._set: list[UpdateElement] = [ ]
        self._where: Expression = None
        self._syntax: UpdateQuerySyntax = UpdateQuerySyntax()
        self._syntax.add_keyword('update')
    
    def __str__(self) -> str:
        return self.explain(pretty=False)
    
    '''
    Mots clés de la requête UPDATE
    '''
    def set_(self, *set_values: UpdateElement) -> Self:
        self._syntax.add_keyword('set')
        self._set = set_values
        return self
    
    '''
    Exécution de la requête UPDATE
    '''

    def execute(self) -> Self:
        if self._syntax.check():
            for element in self._dataset:
                if _Clauses(self._where).match:
                    # On met à jour une copie, sinon les mises à jour peuvent se chevaucher
                    updated = element.data.copy()
                    for update in self._set:
                        updated.update({ update.field.name: _Term(update.value).value })
                    element.data.update(updated.copy())
            return self._dataset
    
    '''
    Explain
    '''

    def _explain_update(self, pretty: bool=False) -> str:
        return f'UPDATE {self._dataset}'

    def _explain_set(self, pretty: bool=False) -> str:
        explanation = 'SET'
        if self._set:
            set_strings = list(map(str, self._set))
            if pretty:
                explanation += '\n' + ',\n'.join(list(map(lambda x: self._indent + x, set_strings)))
            else:
                explanation += ' '+ ', '.join(set_strings)
            return explanation
        return None

    def explain(self, pretty: bool=True) -> str:
        explain_strings = filter(None, [
            self._explain_update(pretty=pretty),
            self._explain_set(pretty=pretty),
            self._explain_where(pretty=pretty)])
        if pretty:
            return '\n'.join(explain_strings)
        return ' '.join(explain_strings)

class _DeleteQuery(_DatasetQuery):
    '''De quoi supprimer des éléments du dataset'''

    def __init__(self):
        super().__init__()
        self._where = None
        self._syntax: DeleteQuerySyntax = DeleteQuerySyntax()
        self._syntax.add_keyword('delete')
    
    def __str__(self) -> str:
        return self.explain(pretty=False)
    
    '''
    Exécution de la requête DELETE
    '''

    def execute(self) -> Dataset:
        if self._syntax.check():
            # On collecte l'ensemble des index qui répondent au critère
            delete_elements = [ ]
            for element in self._from:
                if _Clauses(self._where).match:
                    delete_elements.append(element)
            # ... et on supprime les éléments dans l'ordre inverse de leur index
            delete_elements.sort(key=lambda element: element.index, reverse=True)
            for element in delete_elements:
                element.delete()
            return self._from

    '''
    Explain
    '''

    def _explain_delete(self, pretty: bool=False) -> str:
        return 'DELETE'
    
    def explain(self, pretty: bool=True) -> str:
        explain_strings = filter(None, [
            self._explain_delete(pretty=pretty),
            self._explain_from(pretty=pretty),
            self._explain_where(pretty=pretty),
        ])
        if pretty:
            return '\n'.join(explain_strings)
        return ' '.join(explain_strings)

class _AlterQuery(_DatasetQuery):
    '''De quoi altérer le dataset'''

    def __init__(self, dataset: Dataset) -> None:
        super().__init__()
        self._dataset = dataset
        self._drop_fields = [ ]
        self._syntax: DropQuerySyntax = DropQuerySyntax()
        self._syntax.add_keyword('alter')
    
    def __str__(self) -> str:
        return self.explain(pretty=False)
    
    def drop(self, *fields: DatasetField) -> Self:
        self._syntax.add_keyword('drop')
        self._drop_fields = fields
        return self
    
    def execute(self) -> Dataset:
        if self._syntax.check():
            for element in self._dataset:
                if _Clauses(self._where).match:
                    for field in self._drop_fields:
                        element.drop(field)
            return self._dataset

    '''
    Explain
    '''
    def _explain_alter(self, pretty=False) -> str:
        explanation = 'ALTER'
        if pretty:
            return explanation + f'\n{self._indent}{self._dataset}'
        return explanation + f' {self._dataset}'
    
    def _explain_drop(self, pretty=False) -> str:
        explanation = 'DROP'
        if pretty:
            explanation += '\n' + '\n'.join(list(map(lambda x: self._indent + str(x), self._drop_fields)))
        else:
            explanation += ' ' + ', '.join(list(map(str, self._drop_fields)))
        return explanation
    
    def explain(self, pretty: bool=True) -> str:
        explain_strings = filter(None, [
            self._explain_alter(pretty=pretty),
            self._explain_drop(pretty=pretty),
            self._explain_where(pretty=pretty)
        ])
        if pretty:
            return '\n'.join(explain_strings)
        return ' '.join(explain_strings)
