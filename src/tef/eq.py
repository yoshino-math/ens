def translate(lst):
    if len(lst)>=2 and lst[0]==r'\[' and lst[-1]==r'\]':
        if '&' in lst:
            lst[0]=r'\begin{align*}'
            lst[-1]=r'\end{align*}'
        elif r'\\' in lst:
            lst[0]=r'\begin{gather*}'
            lst[-1]=r'\end{gather*}'
