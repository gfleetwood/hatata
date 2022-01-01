import streamlit as st
import xml.etree.ElementTree as ET
import requests
from os import environ

# https://leetcode.com/problems/different-ways-to-add-parentheses/

def funcHelper(base, combinations):
    if len(base) == 1:
        combinations.add(base[0])
    for i in range(1, len(base), 2):
        sub = '('+''.join(base[i-1:i+2])+')'
        funcHelper(base[:i-1] + [sub] + base[i+2:], combinations)

def compute_combinations(a):
    
    operator_positions = [
        i 
        for i,c in enumerate(a)
        if c in "*+-"
    ]
    
    base = []
    prev = 0
    
    for p in operator_positions:
        base.append(a[prev:p])
        base.append(a[p])
        prev = p + 1
        
    base.append(a[prev:])

    combinations = set()
    funcHelper(base, combinations)
    payload = {str(eval(x)): x for x in combinations}
    
    return(payload)

def read_soln_steps(q):
    
    q = requests.utils.quote(q)
    r = requests.get("http://api.wolframalpha.com/v2/query?appid={}&input=solve+{}&podstate=Result__Step-by-step+solution&format=plaintext".format(app_id, q))

    ans = [
        elem
        for elem in ET.ElementTree(ET.fromstring(r.text)).getroot().iter()
        if elem.tag == "subpod" and elem.attrib['title'] == 'Possible intermediate steps'
    ]

    payload = [child.text for child in ans[0]][0]

    return(payload)

app_id = environ["WOLFRAM_ID"]

st.title("HATATA")
st.write("Your automated Math tutor for PEMDAS")

q = st.text_input('Question', "2*3-4*5")
supplied_ans = st.text_input("Enter Your Answer")

answers = compute_combinations(q)
answer = [x for x in answers.items() if x[0] == str(eval(q))]
soln_steps = read_soln_steps(q)

st.write("Note: Parentheses will be added to questions to stress the correct order of evaluation.")

if supplied_ans != "" and supplied_ans not in list(answers.keys()):
    st.write("You solved the question in a way we didn't think of, so we don't know how to help with your answer. It isn't right though. Try again.")

elif supplied_ans != "" and supplied_ans != answer[0][0]:
    st.write("Your answer is incorrect. You answered {} but the answer is {}.\n".format(supplied_ans, answer[0][0]))
    supplied_soln_steps = read_soln_steps(answers[supplied_ans])
    col1, col2 = st.columns(2)

    col1.write("This is the question you solved: \n\n")
    col1.text(answers[supplied_ans])
    col1.write("These were your steps to solve the problem: \n\n")
    col1.text(supplied_soln_steps)

    col2.write("This is the question you were asked: \n\n")
    col2.text(answer[0][1])
    col2.write("And these are the correct steps to solve the problem: \n\n")
    col2.text(soln_steps)

elif supplied_ans != "" and supplied_ans == answer[0][0]:
    st.write("Your answer is correct! \n\n")
    st.write("This is the question you were asked: \n\n")
    st.text(answer[0][1])
    st.write("Here are the steps you took: \n\n")
    st.text(soln_steps)
