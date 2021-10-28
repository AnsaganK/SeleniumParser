alphabet = ['а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ/ь', 'ы', 'э', 'ю', 'я',]
print(len(alphabet))
key = input('Key = ')
key = key.lower()
key_list = []
for i in key:
    if i == 'ъ' or i == 'ь':
        i = 'ъ/ь'
    if not (i in key_list):
        key_list.append(i)
        print(i)
        alphabet.remove(i)
print(key_list)
text = input('Text = ')
for i in range(5):
    print()
    for j in range(6):
        index = (i*6)+(j+1)
        if len(key_list) >= index:
            if key_list[index-1] == 'ъ/ь':
                letter = key_list[index-1]
            else:
                letter = f' {key_list[index-1]} '
        else:

            number_letter = index - len(key_list)
            letter = alphabet[number_letter-1]
            if letter != 'ъ/ь':
                letter = f' {letter} '
        print(letter, end='    ')
