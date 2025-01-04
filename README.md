# DatasetQuery

Librairie de manipulation d'un *dataset*, à savoir une liste de dictionnaires ayant un certain nombre de clés en commun.

`DatasetQuery` permet d'interroger et d'altérer un ou plusieurs objets `Dataset` en recourant à une syntaxe proche de SQL, tant au niveau des instructions que des expressions.

# Exemple de requête

Considérons les 3 `Dataset` suivants :
```python
from Dataset import Dataset

shapes = Dataset([
    { 'name': 'triangle' },
    { 'name': 'rectangle' },
    { 'name': 'pentagon' }
], name='Shapes')

colors = Dataset([
    { 'name': 'red' },
    { 'name': 'blue' }
], name='Colors')

sides = Dataset([
    { 'name': 'triangle', 'sides': 3 },
    { 'name': 'rectangle', 'sides': 4 },
    { 'name': 'pentagon', 'sides': 5 },
    { 'name': 'hexagon', 'sides': 6 }
], name='Sides')
```

Si ces `Dataset` étaient des tables SQL et que nous souhaitions obtenir une table :

- comportant toutes les combinaisons `shapes` / `colors`
- associant le nombre correct de `sides` à chaque élément de `shapes`
- ne contenant que les éléments ayant plus de 3 côtés et moins de 6
- triés par nombre de côtés croissant et ordre alphabétique inverse de couleur

On écrirait la requête suivante:
```SQL
SELECT
    Shapes.name AS Shape,
    Colors.name AS Color,
    Sides.sides AS Sides
FROM
    Shapes
    JOIN Colors
    JOIN Sides ON Shapes.name = Sides.name
WHERE Sides.sides > 3 AND Sides.sides < 6
ORDER BY Sides ASC, Color DESC
```

Grâce à `DatasetQuery`, on peut faire de même dans une syntaxe assez proche :
```python
from DatasetQuery import select, desc

query = (
    select(
        shapes.name.as_('Shape'),
        colors.name.as_('Color'),
        sides.sides.as_('Sides')
    )
    .from_(shapes)
    .join(colors)
    .join(sides).on(shapes.name == sides.name)
    .where((sides.sides > 3) & (sides.sides < 6))
    .order_by(sides.sides, desc(colors.name))
)
```
Commnençons par voir à quoi ressemble cette requête :
```python
print(query.explain())
```
```bash
SELECT
    `Shapes`.`name` AS `Shape`,
    `Colors`.`name` AS `Color`,
    `Sides`.`sides` AS `Sides`
FROM
    `Shapes`
    JOIN `Colors`
    JOIN `Sides` ON (`Shapes`.`name` == `Sides`.`name`)
WHERE
    ((`Sides`.`sides` > 3) AND (`Sides`.`sides` < 6))
ORDER BY
    `Sides`.`sides`,
    `Colors`.`name` DESC
```
On constate de nombreuses similarités avec la requête SQL ci-dessus.

Exécutons cette requête...

```python
result = query.execute()
```

Son résultat est un `Dataset`. On peut donc voir son contenu avec la méthode `.to_table()` :

```python
result.to_table()
```

Le résultat est conforme aux attentes :
```bash
-----------------------------
|   Shape   | Color | Sides |
-----------------------------
| rectangle | red   |     4 |
| rectangle | blue  |     4 |
| pentagon  | red   |     5 |
| pentagon  | blue  |     5 |
-----------------------------
```

# Requêtes prises en charge
`DatasetQuery` propose nativement les requêtes suivantes :
- `select`
- `update`
- `delete`
- `alter... drop`

A l'heure actuelle, `DatasetQuery` ne prend **pas** en charge les fonctions d'agrégation associées à `group by`.

# Dataset
`DatasetQuery` est une librairie tirant parti de la librairie `Dataset`.

`Dataset` met à disposition :
- `Expression`, une classe de gestion d'expressions arithmétiques, logiques et de comparaison
- `DatasetField`, une classe de gestion des champs d'un dataset

Ces classes peuvent être utilisées pour étendre les capacités des requêtes de manière assez simple.

Par exemple, si l'on souhaite créer automatiquement une description à partir des `Dataset` ci-dessus, une description qui serait du genre *Red rectangle with 4 sides*, on peut utiliser la méthode `DatasetField.func()` pour créer le champ `Description` de la façon suivante :
```python
def capitalize(string: str) -> str:
    return string.capitalize()

query = (
    select(
        shapes.name.as_('Shape'),
        colors.name.as_('Color'),
        sides.sides.as_('Sides'),
        (
            colors.name.func(capitalize)
            + ' ' + shapes.name
            + ' with ' + sides.sides.cast_as(str)
            + ' sides'
        ).as_('Description')
    )
    .from_(shapes)
    .join(colors)
    .join(sides).on(shapes.name == sides.name)
    .where((sides.sides > 3) & (sides.sides < 6))
    .order_by(sides.sides, desc(colors.name))
)
```

Visualisons la requête avec `query.explain()`:
```bash
SELECT
    `Shapes`.`name` AS `Shape`,
    `Colors`.`name` AS `Color`,
    `Sides`.`sides` AS `Sides`,
    (((((capitalize(`Colors`.`name`) + ' ') + `Shapes`.`name`) + ' with ') + CAST(`Sides`.`sides` AS str)) + ' sides') AS `Description`
FROM
    `Shapes`
    JOIN `Colors`
    JOIN `Sides` ON (`Shapes`.`name` == `Sides`.`name`)
WHERE
    ((`Sides`.`sides` > 3) AND (`Sides`.`sides` < 6))
ORDER BY
    `Sides`.`sides`,
    `Colors`.`name` DESC
```

Résultat de cette requête :
```bash
-----------------------------------------------------------
|   Shape   | Color | Sides |         Description         |
-----------------------------------------------------------
| rectangle | red   |     4 | Red rectangle with 4 sides  |
| rectangle | blue  |     4 | Blue rectangle with 4 sides |
| pentagon  | red   |     5 | Red pentagon with 5 sides   |
| pentagon  | blue  |     5 | Blue pentagon with 5 sides  |
-----------------------------------------------------------
```

A noter que
```python
colors.name.func(capitalize)
```
peut être remplacé par
```python
colors.name.func(lambda x: x.capitalize())
```
mais la lisibilité du `.explain()` diminue :
```bash
(((((<lambda>(`Colors`.`name`) + ' ') + `Shapes`.`name`) + ' with ') + CAST(`Sides`.`sides` AS str)) + ' sides') AS `Description`
```

# Plus d'exemples
Voir le répertoire `demo`