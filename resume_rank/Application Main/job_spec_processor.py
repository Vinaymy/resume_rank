# Converts Microsoft docx documents to txt documents
import docx2txt

import string
import re

# For Keywrods Frequency Coutns
from collections import Counter

from nltk.util import ngrams
from nltk.tokenize import word_tokenize

# Keywords Repository
# Python file with multiple lists of segredated keywords
import keywords as keywords_file


"""
    
    ngrams_creator()
    
    Inputs:
        1. ngrams_text_source - String
        2. num_grams - Number of N-grams to be generated
            - Bigrams
            - Trigrams

"""


def ngrams_creator(ngrams_text_source, num_grams):
    # Returns a list of n-grams strings
    n_grams = ngrams(word_tokenize(ngrams_text_source), num_grams)
    n_grams = [' '.join(grams) for grams in n_grams]
    return n_grams


"""

    job_spec_cleaner():
    
    Inputs
        1. Text data from Job Spec File (String) 

    Outputs
        1. job_spec_sentences
            1. List
            2. Cleaned sentences in job spec file
"""


def job_spec_cleaner(job_spec_text):

    # To store cleaned sentences
    job_spec_sentences = []

    # Controller for removing punctuation
    remove_punctuation = True

    # Creating translator for translate function
    # Used to replace punctuation with empty space
    if remove_punctuation == True:
        punctuation_to_remove = "!$%&\'()*,-./:;<=>?[\\]^_`{|}~•"
        punctuation_translator = str.maketrans(
            punctuation_to_remove, ' '*len(punctuation_to_remove))
    else:
        pass

    # Convert Job Spec File to individual lines
    # Clean them up
    for line in job_spec_text.splitlines():
        if line != "":
            line = line.replace('\t', '')  # Replace Tabs with empty string
            line = line.strip()  # Remove extra whitespace
            line = line.lower()  # Convert text to lowercase
            line = line.split(' ')  # Convert string to list
            # Remove empty list elements
            line = [word for word in line if word]
            if len(line) > 1:
                line_str = ' '.join(line)
                if remove_punctuation == True:
                    # Swap punctuation with single empty space
                    line_str = line_str.translate(punctuation_translator)
                    job_spec_sentences.append(line_str)
                else:
                    job_spec_sentences.append(line_str)
        else:
            continue

    return job_spec_sentences


"""

    find_keywords()
    
    Searchs for:
        1. Technical Keywords
        2. Education degree
        3. Education field of study
    
    Inputs
        1. Cleaned sentences from Job Spec File (List)
        
    Output
        1. matched_keywords (List)
        2. List of all keywords found

"""


def find_keywords(job_spec_sentences):

    # List of keywords found
    matched_keywords = []

    # Controllers for searching N-grams
    search_unigrams = True
    search_ngrams = True

    keywords_to_search = keywords_file.database_keywords + \
        keywords_file.education_degree + keywords_file.education_field_study \
        + keywords_file.machine_learning_keywords + keywords_file.programming_keywords

    # Removing duplicates
    keywords_to_search = list(set(keywords_to_search))

    # Match Unigrams
    if search_unigrams == True:
        text_to_search = ' '.join(job_spec_sentences)
        text_to_search = text_to_search.split(' ')
        # Removing empty strings
        text_to_search = [word for word in text_to_search if word]
        for word in text_to_search:
            if word in keywords_to_search:
                matched_keywords.append(word)
            else:
                continue

    # Match Bigrams and Trigrams
    if search_ngrams == True:
        text_to_search = ' '.join(text_to_search)
        text_bigrams = ngrams_creator(text_to_search, 2)
        text_trigrams = ngrams_creator(text_to_search, 3)
        text_combined_ngrams = text_bigrams + text_trigrams
        for word in text_combined_ngrams:
            if word in keywords_to_search:
                matched_keywords.append(word)
            else:
                continue

    return matched_keywords


"""

    sort_keywords()
    
    Sorting extracted keywords
        1. Required technical skills
        2. Optional technical skills
        3. Education Degree
        4. Education Major/Field
        
    Input
        1. job_spec_keywords_found - Extracted keywords list
        2. job_spec_sentences - Cleaned Sentences
        
    Output
        1. data_for_auto_job_spec_form - Dictionary of sorted keywords
            1. required_keywords
            2. optional_keywords
            3. other_keywords
            4. education_degree_keywords
            5. education_field_keywords

"""


def sort_keywords(job_spec_keywords_found, job_spec_sentences):

    # Selectors are used to find out if a sentence has:
    # Optional Keywords
    # Required Keywords
    # Education Keywords
    required_keywords_selectors = keywords_file.required_keywords_selectors
    optional_words_selectors = keywords_file.optional_keywords_selectors

    required_keywords_sentences = []
    optional_keywords_sentences = []
    education_related_sentences = []

    for sentence in job_spec_sentences:
        individual_sentence_unigrams = sentence.split(' ')
        individual_sentence_bigrams = ngrams_creator(sentence, 2)
        individual_sentence_trigrams = ngrams_creator(sentence, 3)
        individual_sentence = individual_sentence_unigrams + \
            individual_sentence_bigrams + individual_sentence_trigrams

        for word in individual_sentence:
            if word in required_keywords_selectors:
                required_keywords_sentences.append(sentence)
                continue
            elif word in optional_words_selectors:
                optional_keywords_sentences.append(sentence)
                continue
            elif word in keywords_file.education_degree or word in keywords_file.education_field_study:
                education_related_sentences.append(sentence)
                continue
            else:
                continue

    # Check for matched keywords in segregated sentences
    required_keywords_sentences_merged = ' '.join(required_keywords_sentences)
    required_keywords_sentences_unigrams = required_keywords_sentences_merged.split()
    required_keywords_sentences_bigrams = ngrams_creator(
        required_keywords_sentences_merged, 2)
    required_keywords_sentences_trigrams = ngrams_creator(
        required_keywords_sentences_merged, 3)
    required_keywords_sentences_ngrams = required_keywords_sentences_unigrams + \
        required_keywords_sentences_bigrams + required_keywords_sentences_trigrams

    optional_keywords_sentences_merged = ' '.join(optional_keywords_sentences)
    optional_keywords_unigrams = optional_keywords_sentences_merged.split()
    optional_keywords_bigrams = ngrams_creator(
        optional_keywords_sentences_merged, 2)
    optional_keywords_trigrams = ngrams_creator(
        optional_keywords_sentences_merged, 3)
    optinal_keywords_sentences_ngrams = optional_keywords_unigrams + \
        optional_keywords_bigrams + optional_keywords_trigrams

    sorted_required_keywords = []
    sorted_optional_keywords = []
    sorted_other_keywords = []

    # Sorting Technical skills keywords
    for word in job_spec_keywords_found:
        if word in required_keywords_sentences_ngrams:
            sorted_required_keywords.append(word)
            continue
        elif word in optinal_keywords_sentences_ngrams:
            sorted_optional_keywords.append(word)
            continue
        else:
            sorted_other_keywords.append(word)

    # education_related_sentences_merged = ' '.join(education_related_sentences)
    # education_related_sentences_unigrams = education_related_sentences_merged.split()
    # education_related_sentences_bigrams = ngrams_creator(education_related_sentences_merged, 2)
    # education_related_sentences_trigrams = ngrams_creator(education_related_sentences_merged, 3)
    # education_related_sentences_ngrams = education_related_sentences_unigrams + education_related_sentences_bigrams + education_related_sentences_trigrams

    # Sorting education related keywords
    sorted_education_degree_keywords = []
    sorted_education_field_keywords = []

    for word in job_spec_keywords_found:
        if word in keywords_file.education_phd:
            sorted_education_degree_keywords = sorted_education_degree_keywords + \
                keywords_file.education_phd
        if word in keywords_file.education_masters:
            sorted_education_degree_keywords = sorted_education_degree_keywords + \
                keywords_file.education_masters
        if word in keywords_file.education_bachelors:
            sorted_education_degree_keywords = sorted_education_degree_keywords + \
                keywords_file.education_bachelors
        if word in keywords_file.education_freshers:
            sorted_education_degree_keywords = sorted_education_degree_keywords + \
                keywords_file.education_freshers
        if word in keywords_file.education_field_study:
            sorted_education_field_keywords.append(word)

    sorted_required_keywords = list(set(sorted_required_keywords))
    sorted_optional_keywords = list(set(sorted_optional_keywords))
    sorted_other_keywords = list(set(sorted_other_keywords))
    sorted_education_degree_keywords = list(
        set(sorted_education_degree_keywords))
    sorted_education_field_keywords = list(
        set(sorted_education_field_keywords))

    data_for_auto_job_spec_form = {
        "required_keywords": sorted_required_keywords,
        "optional_keywords": sorted_optional_keywords,
        "other_keywords": sorted_other_keywords,
        "education_degree_keywords": sorted_education_degree_keywords,
        "education_field_keywords": sorted_education_field_keywords,
    }

    return data_for_auto_job_spec_form


"""

    get_years_of_experience()
    
    Looking for the minimum years of experience requirement
    
    1. Input
        1. Job Specification sentences (List)
    
    2. Output
        1. exp_min_nos_years (Integer)

"""


def get_years_of_experience(job_spec_sentences):
    # If experience not found
    # Then we show it as 0
    exp_min_nos_years = 0

    # List of possible 'Years of experience sentences'
    # Trying to get the overall one
    possible_experience_sentences = []

    # Extracting sentences that might be experience related
    for sentence in job_spec_sentences:
        # Controllers
        word_year_years_found = False
        word_experience_found = False

        # Tokenize sentences
        tokenized_sentence = sentence.split()

        # For each word in tokenized sentence
        for word in tokenized_sentence:
            if word == 'year' or word == 'years':
                word_year_years_found = True
            elif word == 'experience':
                word_experience_found = True
            else:
                continue  # Carry on with the next word

        # If both controllers set to True
        # Add the sentence to possible_experience_sentences
        if word_year_years_found == True and word_experience_found == True:
            possible_experience_sentences.append(sentence)
        else:
            continue  # Carry on with the next sentence

        # Check if list is empty
        if len(possible_experience_sentences) == 0:
            exp_min_nos_years = 0
        else:
            # Get the first item in the list
            # Usually, the first mention of experience is the overall one
            experience_sentence = possible_experience_sentences[0]
            extracted_years_raw = re.search(
                r'\d{1,2}\W?(to|\W)?.?\d{1,2}.?(year|years)', experience_sentence).group()  # Returns a list
            # At present, only looking for digits. Ignoring eg: 'two years of experice'
            if len(extracted_years_raw) == 0:
                    exp_min_nos_years = 0
            else:
                years_regex_str = extracted_years_raw[0]
                years_lstripped = years_regex_str.lstrip()
                years_splitted = years_lstripped.split(' ')
                # For weirdos like 4.2 or 2.8
                years_first_number = years_splitted[0]
                years_final_list = re.findall(r'\d{1,2}', years_first_number)
                exp_min_nos_years = int(years_final_list[0])

    return exp_min_nos_years


def get_job_spec_data(job_spec_content):

    # Get data cleaned
    # Get list of sentences
    job_spec_sentences = job_spec_cleaner(job_spec_content)

    # Find all keywords
    job_spec_keywords_found = find_keywords(job_spec_sentences)

    # Sort keywords
    data_for_auto_job_spec_form = sort_keywords(
        job_spec_keywords_found, job_spec_sentences)

    # Find years of experience
    min_years_experience = get_years_of_experience(job_spec_sentences)

    # Add years of experience to dictionary
    data_for_auto_job_spec_form['experience_min_nos_years'] = min_years_experience

    return data_for_auto_job_spec_form
