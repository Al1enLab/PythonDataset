# Python Dataset
Une librairie pour manipuler des datasets avec des requêtes semblables à des requêtes SQL.

## TL;DR
Le repo contient un répertoire `demo` permettant de comprendre comment utiliser cette librairie par des exemples de complexité croissante.

## Concepts
Pour comprendre comment fonctionne cette librairie, il est préférable d'en connaître quelques concepts de base.

### Dataset
Un *dataset* est une **liste de dictionnaires**. Ni plus, ni moins. Généralement, tous ces dictionnaires comportent plus ou moins les mêmes clés. On les retrouve, par exemple, dans des jeux de données issus de Webservices, au format JSON.

La librairie `Dataset` est une première étape pour gérer les datasets. Elle permet de référencer de manière simple et transparente les champs du *dataset*, en tant qu'objet `DatasetField`, sans se soucier de l'itération.  
Elle permet de définir des expressions, en tant qu'objet `Expression`, de manière similaire.

### Champ
Un champ est une référence à une clé dans l'ensemble des dictionnaires (et non pas dans **un** dictionnaire). Les champs sont gérés par l'objet `DatasetField`. On n'instancie pas directement un `DatasetField`, on l'instancie de manière transparente *via* l'appel d'une propriété d'un objet `Dataset`.

Si `my_dataset` est un objet `Dataset` de cette librairie, le champ `name` peut être référencé indifféremment des deux manières suivantes :
- `my_dataset.name`
- `my_dataset['name']`

### Expression
Une expression, gérée par l'objet `Expression`, est une opération - arithmétique, de comparaison, de transtypage... - qui sera évaluée lors de l'itération du `Dataset`. Généralement, il n'est pas utile d'instancier une `Expression` : on les instancie de manière plus simple et plus intuitive qu'une déclaration.

Par exemple :
- `my_dataset.id == 1` est un objet `Expression` (plus précisément : `Expression(operator.eq, DatasetField(my_dataset, 'id'), 1)`)
- `my_dataset['amount'] * 3` est un objet `Expression` (plus précisément : `Expression(operator.mul, DatasetField(my_dataset, 'amount'), 3)`)
- `(my_dataset.id > 1) & (my_dataset.id < 5)` est aussi un objet `Expression`, composé d'objets `Expression`

La déclaration d'expressions est largement simplifiée au niveau de la syntaxe par l'emploi des opérateurs classiques (`==`, `>=`, `+`, `/`...)

## Fonctionnement
La librairie `Dataset` est utile quand il faut traiter l'ensemble des données d'un *dataset*. Dès lors, elle se concentre sur l'itération d'un *dataset* et les moyens d'accès aux éléments *via* des références et expressions applicables à chaque élément - plutôt que des références et expressions visant un seul élément.

### Usage basique
Considérons le code suivant :
```python
from Dataset import Dataset

mydataset = Dataset([
    { 'shape': 'triangle', 'sides': 3 },
    { 'shape': 'square', 'sides': 4 }
])

for _ in mydataset:
    print(f'{mydataset.shape.value} has {mydataset.sides.value} sides')
```
Le résultat de l'exécution est le suivant :
```bash
triangle has 3 sides
square has 4 sides
```

### DatasetField: instanciation, méthodes et propriétés
Les objets `DatasetField` ne sont pas instanciés directement, mais indirectement *via* un objet `Dataset` dont on demande une propriété ou un item. Dans l'exemple ci-dessus, `mydataset.shape` est une instance de `DatasetField`.

Les méthodes suivantes sont mises à disposition par l'objet de gestion des champs, `DatasetField`.

Lors d'une itération, est désigné *élément actuel* l'élément retourné par l'itération en cours.

#### DatasetField.value
Retourne la valeur du champ de l'élément actuel.

#### DatasetField.name
Retourne le nom du champ.

#### DatasetField.alias
Retourne l'alias du champ, ou son nom s'il n'a pas d'alias.

#### DatasetField.exists
Retourne un objet `Expression` qui est évalué à True si le champ (la clé) est présent dans l'élément (dictionnaire) actuel.

#### DatasetField.cast_as(new_type)
Retourne un objet `Expression` dont l'évaluation retourne la valeur du champ de l'élément actuel transtypé en `new_type`.

#### DatasetField.as_(alias)
Premet d'affecter un alias au champ.

#### DatasetField.like(regex)
Retourne un objet `Expression` qui est évalué à True si l'expression régulière `regex` match la valeur du champ de l'élément actuel.
