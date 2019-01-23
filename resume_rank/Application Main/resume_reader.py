
# Reads docx files by converting them to txt
import docx2txt
import string
import re
import json

from collections import Counter, defaultdict

# For searching N-grams
from nltk.util import ngrams
from nltk.tokenize import word_tokenize

"""
    ngrams_creator()
    
    Inputs:
        1. ngrams_text_source - String
        2. num_grams - Number of N-grams to be generated
            - Bigrams
            - Trigrams
    
    Output:
        1. List of n-grams
"""


def ngrams_creator(ngrams_text_source, num_grams):
    n_grams = ngrams(word_tokenize(ngrams_text_source), num_grams)
    n_grams = [' '.join(grams) for grams in n_grams]
    return n_grams


"""
    Input - docx file
    Output - list of lines
"""


def get_lines_docx(resume_file):
    resume_content = []  # List of cleaned sentences
    text = docx2txt.process(resume_file)

    # Punctuation removal control
    # Every Non-alphanumeric character is ocnverted to an expty space
    remove_punctuation = True
    if remove_punctuation == True:
        punctuation_to_remove = "!$%&\'()*★,-./:;<=>?[\\]^_`{|}~•"
        punctuation_translator = str.maketrans(
            punctuation_to_remove, ' '*len(punctuation_to_remove))

    for line in text.splitlines():
        if line != "":
            line = line.replace('\t', '')  # Replace Tabs with empty string
            line = line.strip()  # Remove extra whitespace
            line = line.lower()  # Convert text to lowercase
            line = line.split(' ')
            line = [s for s in line if s]  # Remove empty elements
            if len(line) > 1:
                line_str = ' '.join(line)
                if remove_punctuation == True:
                    line_str = line_str.translate(punctuation_translator)
                    resume_content.append(line_str)
                else:
                    resume_content.append(line_str)
            else:
                continue
        else:
            continue
    # print(resume_content) # List of sentences (Line wise)
    return resume_content


# Read resumes from repository
def search_keywords_resumes(resumes_list, keywords_to_search):
    # Preparing keywods to search
    must_have_keywords_uncleaned = keywords_to_search['must_have_keywords'].split(
        ',')
    must_have_keywords = [
        item.strip() for item in must_have_keywords_uncleaned]  # Strip whitespace

    optional_keywords_uncleaned = keywords_to_search['optional_keywords'].split(
        ',')
    optional_keywords = [item.strip()
                         for item in optional_keywords_uncleaned]  # Strip whitespace

    education_degree_keywords_uncleaned = keywords_to_search['education_degree_keywords'].split(
        ',')
    education_degree_keywords = [
        item.strip() for item in education_degree_keywords_uncleaned]  # Strip whitespace

    education_field_keywords_uncleaned = keywords_to_search['education_field_keywords'].split(
        ',')
    education_field_keywords = [
        item.strip() for item in education_field_keywords_uncleaned]  # Strip whitespace

    experience_minimum_nos_years_uncleaned = keywords_to_search['min_exp']
    #TODO Needed when activating filtering based on number of years to search
    experience_minimum_nos_years = experience_minimum_nos_years_uncleaned.strip()

    all_keywords_cleaned = must_have_keywords + optional_keywords + \
        education_degree_keywords + education_field_keywords

    # print("All keywords: {}".format(all_keywords_cleaned))
    # print('Type All Keywords {}'.format(type(all_keywords_cleaned)))

    # Single Tokens
    search_unigrams = True
    # Bi-grams
    # Tri-grams
    search_ngrams = True

    all_cvs_keywords_frequency = {}
    # For every cv/resume
    for cv in resumes_list:
        print('\n\n Processing Resume: {}'.format(cv))

        cv_matched_keywords = []
        # For candidate name
        candidate_name = str(cv)
        candidate_name = candidate_name.split('.docx')[0]
        candidate_name = candidate_name.split('/')[1]

        # Get text data from cv
        # List of strings -------------------------------------> Call
        cv_content = get_lines_docx(cv)

        ###############################################################
        ######### EXTRACTING YEARS OF PROFESSIONAL EXPERIENCE #########
        ###############################################################

        candidate_years_professional_experience = 0
        # List of possible 'Years of experience' sentences
        # Usually, overall years of experience is the first on to be found
        # in relation to other experience.
        possible_experience_sentences = []

        # Extracting potential years of experience sentences
        for sentence in cv_content:
            # Controllers
            word_year_years_found = False
            word_experience_found = False

            # Tokenize sentence
            tokenized_sentence = sentence.split()

            # For each word in tokenized/splitted sentence
            for token in tokenized_sentence:
                if token == 'year' or token == 'years':
                    word_year_years_found = True
                elif token == 'experience':
                    word_experience_found = True
                else:
                    continue  # Go to the next word

            # if 'year'/'years' AND 'experience' keywords found
            # Add the sentence to possible experience sentences
            if word_year_years_found == True and word_experience_found == True:
                possible_experience_sentences.append(sentence)
            else:
                continue  # Go to the next sentence

            # Check if the list is empty
            if len(possible_experience_sentences) == 0:
                candidate_years_professional_experience = 0
            else:
                # Get the first sentence, High chances for overall experience
                candidate_experience_sentence = possible_experience_sentences[0]
                extracted_years_raw = re.findall(
                    r'\d? \d{1,2}\+? year|\d{1,2}\+? year', candidate_experience_sentence)  # Returns a list
                # At present, only looking for digits. Ignoring eg: 'two years of experice'
                if len(extracted_years_raw) == 0:
                    candidate_experience_sentence = 0
                else:
                    # Get the first element of the list
                    years_regex_str = extracted_years_raw[0]
                    years_lstripped = years_regex_str.lstrip()  # Remove preceding whitespace
                    year_splitted = years_lstripped.split(' ')
                    # for 3.5 or 2.1 etc types
                    year_first_number = year_splitted[0]
                    year_final_list = re.findall(r'\d{1,2}', year_first_number)
                    candidate_years_professional_experience = int(
                        year_final_list[0])

        # Match Unigrams
        # Match Bigrams
        # Match Trigrams
        for line in cv_content:
            if search_unigrams == True:
                text_data = line.split()
                text_data = [s for s in text_data if s]
                for word in text_data:
                    if word in all_keywords_cleaned:
                        cv_matched_keywords.append(word)

            if search_ngrams == True:
                text_data = ' '.join(text_data)
                text_data_bigrams = ngrams_creator(text_data, 2)
                text_data_trigrams = ngrams_creator(text_data, 3)
                text_data = text_data_bigrams + text_data_trigrams
                for word in text_data:
                    if word in all_keywords_cleaned:
                        cv_matched_keywords.append(word)

        counted_keywords = dict(Counter(cv_matched_keywords))
        counted_keywords['years_of_experience'] = candidate_years_professional_experience

        # Changed the line below with this
        all_cvs_keywords_frequency[candidate_name] = counted_keywords
        # all_cvs_keywords_frequency[candidate_name] = dict(
        #     Counter(cv_matched_keywords))

    #TODO EXPERIMENT
    cvs_json = json.dumps(all_cvs_keywords_frequency)

    return cvs_json
