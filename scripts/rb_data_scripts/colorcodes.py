## https://stackoverflow.com/questions/287871/how-to-print-colored-text-in-python
from termcolor import colored, cprint
if __name__=='__main__':
    print('attempt with termcolor: ', colored('this is red.', 'red'))
    print('done.')
