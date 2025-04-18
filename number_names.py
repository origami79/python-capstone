ones = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
teens = ['ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']
tens = ['', 'ten', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']







def num_to_words (num_str):
    num_list = list(num_str)
    while len(num_list) < 6:
        num_list.insert(0, '0')
    print('num array', num_list)
    
    word = ''
    word_started = False
    for place in range(6):
        print('current place', place)
        print('current num', num_list[place])
        if num_list[place] == '0' and not word_started:
            continue
        else:
            word_started = True
            


    return word
    

def number_name (number):
    digit_count = len(number)
    if digit_count > 6:
        print("Sorry, that number is too big. Please input a number smaller than one million.")
    else:
        print(num_to_words(number))

num = input("Please enter a number smaller than one million: ")
number_name(num)