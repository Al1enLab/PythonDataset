from Dataset import Dataset
from DatasetQuery import select, update, delete, alter, desc, UpdateElement

import unittest

shapes_dataset = Dataset([
    { 'name': 'triangle' },
    { 'name': 'square' },
    { 'name': 'octogon' },
], name='Shapes')

colors_dataset = Dataset([
    { 'name': 'red' },
    { 'name': 'blue' }
], name='Colors')

sides_dataset = Dataset([
    { 'shape': 'triangle', 'sides': 3 },
    { 'shape': 'square', 'sides': 4 },
    { 'shape': 'octogon', 'sides': 8 },
], name='Sides')

shapes_and_colors_dataset = Dataset([
    { 'shape': 'triangle', 'color': 'red' },
    { 'shape': 'triangle', 'color': 'blue' },
    { 'shape': 'square', 'color': 'red' },
    { 'shape': 'square', 'color': 'blue' },
    { 'shape': 'octogon', 'color': 'red' },
    { 'shape': 'octogon', 'color': 'blue' },
], name='Partial')

full_dataset = Dataset([
    { 'shape': 'triangle', 'color': 'red', 'sides': 3 },
    { 'shape': 'triangle', 'color': 'blue', 'sides': 3 },
    { 'shape': 'square', 'color': 'red', 'sides': 4 },
    { 'shape': 'square', 'color': 'blue', 'sides': 4 },
], name='FullDataset')

updated_dataset = Dataset([
    { 'shape': 'triangle', 'color': 'red', 'sides': 3, 'description': 'Red triangle', 'even': False },
    { 'shape': 'triangle', 'color': 'blue', 'sides': 3, 'description': 'Blue triangle', 'even': False},
    { 'shape': 'square', 'color': 'red', 'sides': 4, 'description': 'Red square', 'even': True },
    { 'shape': 'square', 'color': 'blue', 'sides': 4, 'description': 'Blue square', 'even': True },
], name='UpdatedDataset')

dropped_dataset = Dataset([
    { 'shape': 'triangle', 'color': 'red', 'sides': 3, 'description': 'Red triangle' },
    { 'shape': 'triangle', 'color': 'blue', 'sides': 3, 'description': 'Blue triangle' },
    { 'shape': 'square', 'color': 'red', 'sides': 4, 'description': 'Red square' },
    { 'shape': 'square', 'color': 'blue', 'sides': 4, 'description': 'Blue square' },
], name='DroppedDataset')

deleted_dataset = Dataset([
    { 'shape': 'square', 'color': 'red', 'sides': 4, 'description': 'Red square', 'even': True },
    { 'shape': 'square', 'color': 'blue', 'sides': 4, 'description': 'Blue square', 'even': True },
], name='DeletedDataset')

def copy_dataset(dataset: Dataset) -> Dataset:
    new_set = [ item.copy() for item in dataset.raw_dataset ]
    return Dataset(new_set)

class test_SelectQuery(unittest.TestCase):

    def test_SimpleQuery(self):
        
        query = (
            select(
                shapes_dataset.name.as_('shape'),
                colors_dataset.name.as_('color')
            )
            .from_(shapes_dataset)
            .join(colors_dataset)
        )
        print()
        print('Running query')
        print(query.explain())
        result = query.execute()
        self.assertEqual(shapes_and_colors_dataset.raw_dataset, result.raw_dataset)

    def test_QueryClauses(self):
        query = (
            select(
                shapes_dataset.name.as_('shape'),
                colors_dataset.name.as_('color'),
                sides_dataset.sides
            )
            .from_(shapes_dataset)
            .join(colors_dataset)
            .join(sides_dataset).on(shapes_dataset.name == sides_dataset.shape)
            .where((sides_dataset.sides >= 3) & (sides_dataset.sides <= 6))
        )
        print()
        print('Running query')
        print(query.explain())
        result = query.execute()
        self.assertEqual(result.raw_dataset, full_dataset.raw_dataset)
    
    def test_OrderAndLimit(self):
        query = (
            select()
            .from_(full_dataset)
            .order_by(desc(full_dataset.sides), full_dataset.color)
            .limit(2)
        )
        print()
        print('Running query')
        print(query.explain())
        result = query.execute()
        expected = [
            full_dataset.raw_dataset[3],
            full_dataset.raw_dataset[2],
        ]
        self.assertEqual(result.raw_dataset, expected)

    def test_UpdateDataset(self):

        def capitalize(string: str) -> str:
            return string.capitalize()
        
        dataset_copy = copy_dataset(full_dataset)
        query = (
            update(dataset_copy)
            .set_(
                UpdateElement(
                    dataset_copy.description,
                    dataset_copy.color.func(capitalize) + ' ' + dataset_copy.shape
                ),
                UpdateElement(
                    dataset_copy.even,
                    dataset_copy.sides % 2 == 0
                )
            )
        )
        print()
        print('Running query')
        print(query.explain())
        query.execute()
        self.assertEqual(dataset_copy.raw_dataset, updated_dataset.raw_dataset)

    def test_DropQuery(self):
        dataset_copy = copy_dataset(updated_dataset)
        query = (
            alter(dataset_copy)
            .drop(dataset_copy.even)
        )
        print()
        print('Running query')
        print(query.explain())
        result = query.execute()
        self.assertEqual(result.raw_dataset, dropped_dataset.raw_dataset)

    def test_DeleteQuery(self):
        dataset_copy = copy_dataset(updated_dataset)
        query = (
            delete()
            .from_(dataset_copy)
            .where(dataset_copy.even.is_(False))
        )
        print()
        print('Running query')
        print(query.explain())
        result = query.execute()
        self.assertEqual(result.raw_dataset, deleted_dataset.raw_dataset)

if __name__ == '__main__':
    unittest.main()
