import unittest
from Dataset import Dataset, DatasetField, Expression
import operator

dataset_name = 'TestDataset'
altered_name = 'AlteredDatasetName'
data_range = range(0, 5)
test_data = [
    { 'element': f'Element {index}', 'amount': index, 'even': index % 2 == 0 } for index in data_range
]
test_dataset = Dataset(test_data, name=dataset_name)

class TestExpression(unittest.TestCase):

    data = test_data.copy()
    dataset = Dataset(data, name=dataset_name)

    def test_Expression(self):
        # Test Expression catching

        # Comparaison
        eq_expression = (self.dataset.amount == 1)
        neq_expression = (self.dataset.amount != 1)
        lt_expression = (self.dataset.amount < 1)
        gt_expression = (self.dataset.amount > 1)
        lte_expression = (self.dataset.amount <= 1)
        gte_expression = (self.dataset.amount >= 1)

        # Arithmétique
        add_expression = (self.dataset.amount + 1)
        radd_expression = (1 + self.dataset.amount)
        sub_expression = (self.dataset.amount - 1)
        rsub_expression = (1 - self.dataset.amount)
        mul_expression = (self.dataset.amount * 2)
        rmul_expression = (2 * self.dataset.amount)
        div_expression = (self.dataset.amount / 2)
        rdiv_expression = (2 / self.dataset.amount)
        floordiv_expression = (self.dataset.amount // 2)
        rfloordiv_expression = (2 // self.dataset.amount)
        mod_expression = (self.dataset.amount % 2)
        rmod_expression = (2 % self.dataset.amount)

        # Logique
        and_expression = (self.dataset.even & True)
        or_expression = (self.dataset.even | False)
        not_expression = (~ self.dataset.even)

        # Test extended properties
        in_expression = self.dataset.amount.in_(data_range)
        is_expression = self.dataset.even.is_(True)
        func_expression = self.dataset.amount.func(lambda x: x * 2)

        # Test Expression value
        for element in self.dataset:
            # Comparaison
            self.assertEqual(eq_expression.match, element.index == 1)
            self.assertEqual(neq_expression.match, element.index != 1)
            self.assertEqual(lt_expression.match, element.index < 1)
            self.assertEqual(gt_expression.match, element.index > 1)
            self.assertEqual(lte_expression.match, element.index <= 1)
            self.assertEqual(gte_expression.match, element.index >= 1)

            # Arithmétique
            self.assertEqual(add_expression.value, element.index + 1)
            self.assertEqual(sub_expression.value, element.index - 1)
            self.assertEqual(radd_expression.value, 1 + element.index)
            self.assertEqual(rsub_expression.value, 1 - element.index)
            self.assertEqual(mul_expression.value, element.index * 2)
            self.assertEqual(rmul_expression.value, element.index * 2)
            self.assertEqual(div_expression.value, element.index / 2)
            if element.index != 0:
                self.assertEqual(rdiv_expression.value, 2 / element.index)
            self.assertEqual(floordiv_expression.value, element.index // 2)
            if element.index != 0:
                self.assertEqual(rfloordiv_expression.value, 2 // element.index)
            self.assertEqual(mod_expression.value, element.index % 2)
            if element.index != 0:
                self.assertEqual(rmod_expression.value, 2 % element.index)
            
            # Logique
            self.assertEqual(and_expression.value, element.index % 2 == 0)
            self.assertEqual(or_expression.value, element.index % 2 == 0)
            self.assertEqual(not_expression.value, element.index % 2 != 0)

            # Extended
            self.assertTrue(in_expression.value)
            self.assertEqual(is_expression.value, element.index % 2 == 0)
            self.assertEqual(func_expression.value, element.index * 2)
            

class TestDataset(unittest.TestCase):

    data = test_data.copy()
    dataset = Dataset(data, name=dataset_name)

    def test_length(self):
        self.assertEqual(len(self.dataset), len(self.data))

    def test_iteration(self):
        counter = 0
        for element in self.dataset:
            self.assertEqual(element.index, counter)
            self.assertEqual(element.data, self.data[counter])
            counter += 1

    def test_Dataset_name(self):
        self.assertEqual(str(self.dataset), f'`{dataset_name}`')
        self.dataset.set_name(altered_name)
        self.assertEqual(str(self.dataset), f'`{altered_name}`')

    def test_DatasetField(self):
        # __getattr__ & __getitem__
        for field in ('name', 'value'):
            expected_field = DatasetField(self.dataset, name=field)
            attr_field = getattr(self.dataset, field)
            item_field = self.dataset[field]
            self.assertEqual(attr_field, expected_field)
            self.assertEqual(item_field, expected_field)
        
        # Value, exists, cast_as, like
        for element in self.dataset:
            self.assertEqual(self.dataset.element.value, f'Element {element.index}')
            self.assertEqual(self.dataset.amount.value, element.index)
            self.assertTrue(self.dataset.element.exists.value)
            self.assertFalse(self.dataset.unknown_key.exists.value)
            self.assertEqual(self.dataset.amount.cast_as(str).value, str(element.index))
            self.assertTrue(self.dataset.element.like(r'^Element [0-9]+$').value)
            self.assertFalse(self.dataset.element.like(r'^Unmatched$').value)
        
        # Name & Alias
        field = self.dataset.element
        self.assertEqual(field.name, 'element')
        self.assertEqual(field.alias, 'element')
        field.as_('AliasedField')
        self.assertEqual(field.name, 'element')
        self.assertEqual(field.alias, 'AliasedField')

if __name__ == '__main__':
    unittest.main()
