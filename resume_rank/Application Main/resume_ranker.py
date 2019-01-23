#TODO Experience

import string
from collections import Counter, OrderedDict

import json
import tempfile
import pickle
import shutil

import re
import math  # Using for calcuate_cosine_similarity_score()

# TO calculate cosine similarity
import cosine_similarity_calculator as csc


"""

    prepare_data_for_ranking(cvs_keywords_frequency, keyword_to_search):

"""
# Prepare data for ranking


def prepare_data_for_ranking(cvs_keywords_frequency, keyword_to_search):

    # Keywords to search from Job Specification
    # Convert to list
    # Remove whitespace
    must_have_keywords_uncleaned = keyword_to_search['must_have_keywords'].split(
        ',')
    must_have_keywords = [
        item.strip() for item in must_have_keywords_uncleaned]  # Strip whitespace

    optional_keywords_uncleaned = keyword_to_search['optional_keywords'].split(
        ',')
    optional_keywords = [item.strip()
                         for item in optional_keywords_uncleaned]  # Strip whitespace

    education_degree_keywords_uncleaned = keyword_to_search['education_degree_keywords'].split(
        ',')
    education_degree_keywords = [
        item.strip() for item in education_degree_keywords_uncleaned]  # Strip whitespace

    education_field_keywords_uncleaned = keyword_to_search['education_field_keywords'].split(
        ',')
    education_field_keywords = [
        item.strip() for item in education_field_keywords_uncleaned]  # Strip whitespace

    # For labeling highest education level
    phd_list = ["phd", "p hd"]

    masters_list = ["masters", "master", "master s",
                    "m sc", "msc", "m tech", "mtech", "mca", "m c a"]

    bachelors_list = ["b sc", "bsc", "b tech", "btech",
                      "bca", "b c a",
                      "bachelors", "bachelor"]

    # Resume data
    cvs_keywords_frequency = cvs_keywords_frequency

    ###################################
    # SORTING EXTRACTED DATA
    ###################################
    #TODO Check continue statements
    all_cvs_combined = {}
    for resume_name, keywords in cvs_keywords_frequency.items():
        must_have_count = {}
        optional_count = {}
        combined_dict = {}
        combined_dict['education_degree'] = 'degree not found'
        field_study = 'edu major not found'

        #TODO Eperiement
        education_degree_list = []

        if len(keywords) == 0:
            continue
        else:
            for word, count in keywords.items():  # TODO Verify skill using count
                if word in must_have_keywords:
                    must_have_count[word] = count
                    continue
                if word in optional_keywords:
                    optional_count[word] = count
                    continue
                #EDUCATION RELATED - Degree
                if word in bachelors_list:
                    education_degree_list.append('bachelors')
                if word in masters_list:
                    education_degree_list.append('masters')
                if word in phd_list:
                    education_degree_list.append('phd')
                # EDUCATION RELATED - Field of study
                if word in education_field_keywords:
                    field_study = word
                if word == 'years_of_experience':
                    combined_dict['years_of_experience'] = count

            combined_dict['must_have_keywords'] = must_have_count
            combined_dict['optional_keywords'] = optional_count
            combined_dict['education_field_study'] = field_study

            education_degree_list_sorted = sorted(education_degree_list, reverse=True)
            if len(education_degree_list_sorted) > 0:
                combined_dict['education_degree'] = education_degree_list_sorted[0]
            else:
                combined_dict['education_degree'] = 'degree not found'


            all_cvs_combined[resume_name] = combined_dict

    # Get cosine similarity scores
    cvs_must_have_cos_sim_score, cvs_optional_cos_sim_score = csc.get_cosine_similarity_score(
        keyword_to_search, all_cvs_combined)

    # Get percentage match scores
    csv_percentage_match_scores = percentage_match_ranker(must_have_keywords, optional_keywords, all_cvs_combined)

    return (cvs_must_have_cos_sim_score, cvs_optional_cos_sim_score,  csv_percentage_match_scores, all_cvs_combined)


def percentage_match_ranker(must_have_keywords, optional_keywords, all_cvs_combined):

    must_have_keywords = must_have_keywords  # List
    must_have_keywords_len = len(must_have_keywords)

    optional_keywords = optional_keywords  # List
    optional_keywords_len = len(optional_keywords)

    all_cvs_combined = all_cvs_combined  # TODO Do not need

    cvs_percentage_match = {}
    for candidate_name, candidate_data in all_cvs_combined.items():
        must_have_list = []
        optional_list = []
        for keywords_domain, keywords in candidate_data.items():
            if keywords_domain == 'must_have_keywords':
                for keyword, keyword_frequency in keywords.items():
                    must_have_list.append(keyword)
            if keywords_domain == 'optional_keywords':
                for keyword, keyword_frequency in keywords.items():
                    optional_list.append(keyword)

        match_percentage_must_have = len(must_have_list) / must_have_keywords_len
        match_percentage_must_have = round(match_percentage_must_have, 2)
        match_percentage_must_have = str(match_percentage_must_have * 100) + ' %'

        match_percentage_optional = len(optional_list) / optional_keywords_len
        match_percentage_optional = round(match_percentage_optional, 2)
        match_percentage_optional = str(match_percentage_optional * 100) + ' %'


        cvs_percentage_match[candidate_name] = {'Percentage match must have': match_percentage_must_have,
                                                'Percentage match optional': match_percentage_optional}

    return(cvs_percentage_match)

