import re
import math
from collections import Counter

##########################################TODO Cross check other code with scipy
# from scipy.spatial import distance
# x = distance.cosine([1, 0, 0], [0, 1, 0])
# print(x)


def prepare_data_for_cosine_similarity(keyword_to_search, all_cvs_combined):

    # Get data
    keyword_to_search = keyword_to_search
    cvs_keywords_with_counts = all_cvs_combined

    ######################################
    # Keywords to search - Match against #
    # Strip whitespace
    ######################################

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

    # Converting lists to strings
    # Calculating the similarity against these
    js_must_have_keywords = ' '.join(must_have_keywords)
    js_optional_keywords = ' '.join(optional_keywords)
    js_degree = ' '.join(education_degree_keywords)
    js_degree_field = ' '.join(education_field_keywords)

    # Used for return
    # Better to combine the individual variables above
    js_keywords_strings = {
        'js_must_have_keywords': js_must_have_keywords,
        'js_optional_keywords': js_optional_keywords,
        'js_degree': js_degree,
        'js_degree_field': js_degree_field
    }

    ################################
    # Keywords to match - To match #
    ################################
    # Will contains candidate names and keywords without counts

    cvs_keywords_strings = {}  # TODO Name

    for candidate_name, candidate_data in cvs_keywords_with_counts.items():
        cand_must_have_keywords = []
        cand_optional_keywords = []
        cand_education_degree_keywords = []
        cand_education_field_keywords = []
        keywords_combined_dict = {}

        for keywords_domain_name, keywords_data in candidate_data.items():

            if keywords_domain_name == 'must_have_keywords':
                for keyword, keyword_count in keywords_data.items():
                    cand_must_have_keywords.append(keyword)

            elif keywords_domain_name == 'optional_keywords':
                for keyword, keyword_count in keywords_data.items():
                    cand_optional_keywords.append(keyword)

            elif keywords_domain_name == 'education_degree':
                cand_education_degree_keywords.append(keywords_data)

            elif keywords_domain_name == 'education_field_study':
                cand_education_field_keywords.append(keywords_data)
            #TODO ADD FOR CITY NAME AND YEARS OF EXPERIENCE

            # Cadidate names with list of keywords
            # Without counts
            keywords_combined_dict['cand_must_have_keywords'] = " ".join(
                cand_must_have_keywords)
            keywords_combined_dict['cand_optional_keywords'] = " ".join(
                cand_optional_keywords)
            keywords_combined_dict['cand_education_degree_keywords'] = " ".join(
                cand_education_degree_keywords)
            keywords_combined_dict['cand_education_field_keywords'] = " ".join(
                cand_education_field_keywords)

        cvs_keywords_strings[candidate_name] = keywords_combined_dict
        
    return js_keywords_strings, cvs_keywords_strings


def get_cosine_similarity_score(keyword_to_search, all_cvs_combined):

    """

        #############################
        * Send Data to get prepared *
        #############################

        Get the data perpared for scoring
        Will get dictionaries of:
            1. keyword_to_search
                {'js_must_have_keywords': 'string of keywords', 'js_optional_keywords': 'string of keywords'....}
            2. all_cvs_combined - 
                {
                'candidate_name': {'cand_must_have_keywords': 'string of keywords', 'cand_optional_keywords': 'string of keywords'.....},
                'candidate_name': {'cand_must_have_keywords': 'string of keywords', 'cand_optional_keywords': 'string of keywords'.....}
                }

    """
    prepared_keywords_to_search, prepared_all_cvs_combined = prepare_data_for_cosine_similarity(
        keyword_to_search, all_cvs_combined)

    cvs_must_have_keywords_strings = {}
    for candidate_name, candidate_data in prepared_all_cvs_combined.items():
        for keyword_domain_name, keywords_string in candidate_data.items():
            if keyword_domain_name == 'cand_must_have_keywords':
                must_have_keywords_string = candidate_data['cand_must_have_keywords']
        cvs_must_have_keywords_strings[candidate_name] = must_have_keywords_string

    cvs_optional_keywords_strings = {}
    for candidate_name, candidate_data in prepared_all_cvs_combined.items():
        for keyword_domain_name, keywords_string in candidate_data.items():
            if keyword_domain_name == 'cand_optional_keywords':
                optional_keywords_string = candidate_data['cand_optional_keywords']
        cvs_optional_keywords_strings[candidate_name] = optional_keywords_string

    """

        ######################################################
        * Send prepared data to get cosine similarity scores *
        # Return candidate names with cosine similarity scores
        ######################################################


    """

    # Must have keywords scores
    must_have_keywords_cosine_sim_score = cosine_similarity_calculator_caller(
        prepared_keywords_to_search['js_must_have_keywords'], cvs_must_have_keywords_strings)

    # Optional keywords scores
    optional_keywords_cosine_sim_score = cosine_similarity_calculator_caller(
        prepared_keywords_to_search['js_optional_keywords'], cvs_optional_keywords_strings)

    return must_have_keywords_cosine_sim_score, optional_keywords_cosine_sim_score


# TODO Can this be integrated with the function on top of this?
def cosine_similarity_calculator_caller(js_keywords, cvs_keywords):

    # Call cosine_similarity_calculator() for every candidate
    cvs_cosine_similarity_score = {}
    for candidate_name, keywords_string in cvs_keywords.items():
        score = cosine_similarity_calculator(
            js_keywords, keywords_string)
        cvs_cosine_similarity_score[candidate_name] = score

    return cvs_cosine_similarity_score


"""

    Calculates cosine similarity score
    Inputs
        - target_string: Job spec keywords as string
        - to_match_string: Keywords domain specific string

    #TODO check accuracy of code for cosine_similarity_calculator()
"""


def cosine_similarity_calculator(target_string, to_match_string):
    WORD = re.compile(r'\S+')

    target_string = target_string
    to_match_string = to_match_string

    def get_cosine(target_vector, to_match_vector):
        intersection = set(target_vector.keys()) & set(to_match_vector.keys())
        numerator = sum([target_vector[x] * to_match_vector[x]
                         for x in intersection])

        sum1 = sum([target_vector[x]**2 for x in target_vector.keys()])
        sum2 = sum([to_match_vector[x]**2 for x in to_match_vector.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
           return 0.0
        else:
           return float(numerator) / denominator

    def text_to_vector(text):
        words = WORD.findall(text)
        return Counter(words)

    target_vector = text_to_vector(target_string)
    to_match_vector = text_to_vector(to_match_string)

    cosine = get_cosine(target_vector, to_match_vector)
    return cosine
