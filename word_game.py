#simple word guessing game
hidden_word =input('Enter a word')
word_list = list(hidden_word)
x = len(hidden_word)
d = ['_']*x
print(".".join(d))
responses = []
while d.count('_')!=0:
    accepted_inputs=('y','n','yes','no')
    run = input("Playing (Y = 'Yes', N = 'No')?")
    if not run.lower() in accepted_inputs:
        print('Wrong input')
        continue
    if run.lower() == 'y':
        guess = input('Take a Guess')
        if guess in responses:
                print('Already guessed, try something else')
                continue
        else:
            responses.append(guess)
        for (n,m) in enumerate(hidden_word):
            if (guess == m):
                d[n]=guess
        print(".".join(d))
    else:
        break
if d.count('_')==0:
    print("Congratulations you guessed it!")  