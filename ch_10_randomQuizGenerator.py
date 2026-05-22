
import random
import os
from datetime import date

# The quiz data. Keys are states and values are their capitals.
capitals = {'Alabama': 'Montgomery', 'Alaska': 'Juneau', 'Arizona':
'Phoenix', 'Arkansas': 'Little Rock', 'California': 'Sacramento', 'Colorado':
'Denver', 'Connecticut': 'Hartford', 'Delaware': 'Dover', 'Florida':
'Tallahassee', 'Georgia': 'Atlanta', 'Hawaii': 'Honolulu', 'Idaho': 'Boise',
'Illinois': 'Springfield', 'Indiana': 'Indianapolis', 'Iowa': 'Des Moines',
'Kansas': 'Topeka', 'Kentucky': 'Frankfort', 'Louisiana': 'Baton Rouge',
'Maine': 'Augusta', 'Maryland': 'Annapolis', 'Massachusetts': 'Boston',
'Michigan': 'Lansing', 'Minnesota': 'Saint Paul', 'Mississippi': 'Jackson',
'Missouri': 'Jefferson City', 'Montana': 'Helena', 'Nebraska': 'Lincoln',
'Nevada': 'Carson City', 'New Hampshire': 'Concord', 'New Jersey': 'Trenton',
'New Mexico': 'Santa Fe', 'New York': 'Albany', 'North Carolina': 'Raleigh',
'North Dakota': 'Bismarck', 'Ohio': 'Columbus', 'Oklahoma': 'Oklahoma City',
'Oregon': 'Salem', 'Pennsylvania': 'Harrisburg', 'Rhode Island': 'Providence',
'South Carolina': 'Columbia', 'South Dakota': 'Pierre', 'Tennessee':
'Nashville', 'Texas': 'Austin', 'Utah': 'Salt Lake City', 'Vermont':
'Montpelier', 'Virginia': 'Richmond', 'Washington': 'Olympia', 'West Virginia': 'Charleston',
'Wisconsin': 'Madison', 'Wyoming': 'Cheyenne'}

# Generate 35 quiz files.
for quiz_num in range(35):
    # Create output directory named `quizes_YYYY-MM-DD` and files inside it.
    out_dir = f"quizes_{date.today().isoformat()}"
    os.makedirs(out_dir, exist_ok=True)
    quiz_file = open(os.path.join(out_dir, f'capital_quiz_{quiz_num + 1}.txt'), 'w')
    answer_file = open(os.path.join(out_dir, f'capital_quiz_answers_{quiz_num + 1}.txt'), 'w')

    # TODO: Write out the header for the quiz.
    quiz_file.write('Name:\n\nDate:\n\nPeriod:\n\n')
    quiz_file.write(f'State Capitals Quiz (Form {quiz_num + 1})'.center(50) + '\n\n')
    quiz_file.write('Instructions: For each state, write the letter of the correct capital.\n\n')
    quiz_file.write('\n\n')
    # TODO: Shuffle the order of the states.
    states = list(capitals.keys())
    random.shuffle(states)

    # TODO: Loop through all 50 states, making a question for each.
    for question_num in range(50):
        # Get the correct answer.
        correct_answer = capitals[states[question_num]]
        # Get the wrong answers.
        wrong_answers = list(capitals.values())
        del wrong_answers[wrong_answers.index(correct_answer)]
        wrong_answers = random.sample(wrong_answers, 3)
        # Combine the correct answer with the wrong answers and shuffle them.
        answer_options = wrong_answers + [correct_answer]
        random.shuffle(answer_options)

        # TODO: Write the question and answer options to the quiz file.
        quiz_file.write(f'{question_num + 1}. What is the capital of {states[question_num]}?\n')
        for i, option in enumerate(answer_options):
            quiz_file.write(f'    {chr(65 + i)}. {option}\n')
        quiz_file.write('\n')

        # TODO: Write the answer key to a file.
        answer_file.write(f'{question_num + 1}. {chr(65 + answer_options.index(correct_answer))}\n')

    quiz_file.close()
    answer_file.close()
    
        
