from Dataset import Dataset
from .demo_data import *

import ipaddress

dataset = Dataset(dns_records)

# A quoi ressemble notre dataset
print()
print(f'Demo dataset initialized : {dataset}')

# Le nom par défaut n'est pas franchement explicite...
print()
dataset.set_name('DNS records')
print(f'Dataset {dataset} contains {len(dataset)} elements.')

# Voyons une itération...
print()
print('=== Elements list')
print()
for element in dataset:
    print(f'Element data is {element.data}')

# Bien, maintenant prenons uniquement un champ du dataset
print()
print('=== A records')
print()
for element in dataset:
    print(f'{dataset.A_record} #{element.index}: {dataset.A_record.value}')

# On a vu les bases, attaquons les fonctionnalités sympathiques
# Déclarons une fonction qui transforme une adresse IP en entier...
def inet_aton(ip_string: str) -> int:
    '''Cast an IP address as integer'''
    return int(ipaddress.IPv4Address(ip_string))
# ... et celle qui fait l'opération inverse
def inet_ntoa(integer: int) -> str:
    return str(ipaddress.IPv4Address(integer))

print()
intip_field = dataset.A_record.func(inet_aton)
intip_field.set_name('IP (int)')

print('=== Cast as int')
print()
for _ in dataset:
    print(f'{dataset.A_record} {dataset.A_record.value} cast as int: {intip_field.value}')

print()
print('=== Readdressing')
print()

# Du coup, on peut déplacer les adresses de quelques classes C, par exemple, grâce à cette fonction
def move_up(ipaddr: str, class_C_amount: int=1) -> str:
    intip = inet_aton(ipaddr)
    intip += 256 * class_C_amount
    return inet_ntoa(intip)

def ipdigits(ipaddr: str) -> list:
    return list(map(int, ipaddr.split('.')))

# Version détaillée
upped_field = intip_field + 512
upped_field.set_name('Upped field')

newip_field_step = upped_field.func(inet_ntoa)
newip_field_step.set_name('New IP (step)')

# Version objet
newip_field_object = (dataset.A_record.func(inet_aton) + 512).func(inet_ntoa)
#                    ^^^^^^^^^^^ Expression Object ^^^^^^^^^^
newip_field_object.set_name('New IP (object)')

# Version fonction
newip_field_move_up = dataset.A_record.func(move_up, 2)
newip_field_move_up.set_name('New IP (move_up)')

# Digits de l'adresse
ipdigits_field_lambda = dataset.A_record.func(lambda ip: list(map(int, ip.split('.'))))
ipdigits_field_lambda.set_name('IP digits (lambda)')

ipdigits_field_func = dataset.A_record.func(ipdigits)
ipdigits_field_func.set_name('IP digits (ipdigits)')

# Noter la forme str d'un champ
print('New fields :')
for field in [
    intip_field,
    upped_field,
    newip_field_step,
    newip_field_object,
    newip_field_move_up,
    ipdigits_field_lambda,
    ipdigits_field_func ]:
    print(f'    {field.name}'.ljust(25) + f' : {field}')

print()
new_data = [ ]
for _ in dataset:
    new_data.append({
        dataset.A_record.name: dataset.A_record.value,
        intip_field.name: intip_field.value,
        upped_field.name: upped_field.value,
        newip_field_step.name: newip_field_step.value,
        newip_field_move_up.name: newip_field_move_up.value,
        newip_field_object.name: newip_field_object.value,
        ipdigits_field_lambda.name: ipdigits_field_lambda.value,
        ipdigits_field_func.name: ipdigits_field_func.value
    })
Dataset(new_data).to_table()
# "One liner"
print()
print('=== "One liner"')
print()
ND = Dataset([
    {
        'hostname': dataset.hostname.value,
        'A_record': dataset.A_record.value,
        'IP Digits': dataset.A_record.func(lambda ip: list(map(int, ip.split('.')))).value,
        # 'New IP': dataset.A_record.func(move_up, 2).value
        'New IP': dataset.A_record.func(lambda ip: str(ipaddress.IPv4Address(ip) + 512)).value,
        'CNAME_record': dataset.CNAME_record.value,
        'TXT_record': dataset.TXT_record.value,
    }
    for _ in dataset
])

ND.to_table()
