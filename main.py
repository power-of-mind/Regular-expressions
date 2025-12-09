import re
import csv

def format_phone(phone):
    """
    Форматирует номер телефона в соответствии с шаблоном +7(999)999-99-99 доб.9999.
    """

    digits = re.findall(r'\d+', phone)
    all_digits = ''.join(digits)

    # Обработка основного номера
    if len(all_digits) >= 11:
        # Если есть 11 цифр, предполагаем, что это +7 + 10 цифр
        main_number = '+7({}){}-{}-{}'.format(
            all_digits[1:4],
            all_digits[4:7],
            all_digits[7:9],
            all_digits[9:11]
        )
    elif len(all_digits) >= 10:
        # Если 10 цифр, добавляем +7
        main_number = '+7({}){}-{}-{}'.format(
            all_digits[0:3],
            all_digits[3:6],
            all_digits[6:8],
            all_digits[8:10]
        )
    else:
        # Если не хватает цифр, возвращаем исходный номер
        return phone

    # Проверяем наличие добавочного номера
    match_dob = re.search(r'доб\.?\s*(\d+)', phone)
    if match_dob:
        dob_number = match_dob.group(1)
        # Форматируем добавочный номер как 4 цифры
        if len(dob_number) >= 4:
            dob_formatted = 'доб.{}'.format(dob_number[-4:])
        else:
            dob_formatted = 'доб.{}'.format(dob_number)
        return '{} {}'.format(main_number, dob_formatted)
    else:
        return main_number

def parse_lastname(lastname):
    """
    Разбивает фамилию, имя и отчество человека по полям lastname, firstname и surname
    """

    formatted_names = []

    for line in lastname[1:]:
        personal_list = line.split(',')
        organization = personal_list[3]
        position = personal_list[4]
        phone = format_phone(personal_list[5])
        email = personal_list[6].strip()

        # Когда пробел содержится в поле lastname
        if ' ' in personal_list[0]:
            sublist = personal_list[0].strip().split()
            if len(sublist) > 2:
                dict_ = {
                    'lastname': sublist[0],
                    'firstname': sublist[1],
                    'surname': sublist[2],
                    'organization': organization,
                    'position': position,
                    'phone': phone,
                    'email': email
                }
            else:
                dict_ = {
                    'lastname': sublist[0],
                    'firstname': sublist[1],
                    'surname': personal_list[2],
                    'organization': organization,
                    'position': position,
                    'phone': phone,
                    'email': email
                }

            formatted_names.append(dict_)

        # Когда пробел содержится в поле firstname
        elif ' ' in personal_list[1]:
            sublist = personal_list[1].split()
            dict_ = {
                'lastname': personal_list[0],
                'firstname': sublist[0],
                'surname': sublist[1],
                'organization': organization,
                'position': position,
                'phone': phone,
                'email': email
            }

            formatted_names.append(dict_)

        # Когда фамилия, имя и отчество разбиты правильно изначально
        elif len(personal_list[1]) > 0 and len(personal_list[2]) > 0:
            dict_ = {
                'lastname': personal_list[0],
                'firstname': personal_list[1],
                'surname': personal_list[2],
                'organization': organization,
                'position': position,
                'phone': phone,
                'email': email
            }

            formatted_names.append(dict_)

    return formatted_names


def join_data(final_list):
    """
    Объединяет все дублирующиеся записи о человеке в одну
    """

    dict_group = {}

    for person in final_list:
        # Создаем ключ (фамилия + имя)
        key = (person['lastname'], person['firstname'])

        # Если ключа нет в dict_group, создаем уникальную запись
        if key not in dict_group:
            dict_group[key] = {
                'lastname': person['lastname'],
                'firstname': person['firstname'],
                'surname': [person['surname']],
                'organization': [person['organization']],
                'position': [person['position']],
                'phone': [person['phone']],
                'email': [person['email']]
            }
        # Если ключ есть, объединяем данные
        else:
            dict_group[key]['surname'].extend([person.get('surname')])
            dict_group[key]['organization'].extend([person.get('organization')])
            dict_group[key]['position'].extend([person.get('position')])
            dict_group[key]['phone'].extend([person.get('phone')])
            dict_group[key]['email'].extend([person.get('email')])

    # Создаем пустой список и заполняем значениями из словаря dict_group
    join_list = []

    for value in dict_group.values():
        value['surname'] = ''.join(set(value['surname']))
        value['organization'] = ''.join(set(value['organization']))
        value['position'] = ''.join(value['position'])
        value['phone'] = ''.join(value['phone'])
        value['email'] = ''.join(value['email'])

        join_list.append(value)

    return join_list

if __name__ == '__main__':
    with (open('phonebook_raw.csv', 'r') as f):
        data = f.readlines()

        formatted_list = parse_lastname(data)
        result = join_data(formatted_list)

    with open('phonebook_format.csv', 'w') as f:
        fieldnames = ['lastname',
                      'firstname',
                      'surname',
                      'organization',
                      'position',
                      'phone',
                      'email'
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in result:
            writer.writerow(row)