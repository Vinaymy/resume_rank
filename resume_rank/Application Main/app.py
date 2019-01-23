# This application is built on Flask
from flask import Flask
from flask import render_template, request, session, redirect, url_for

import json
import pandas as pd  # Used to sort the outcome of sorting
import tempfile
import pickle  # For passing data
import shutil
from collections import OrderedDict, defaultdict

# Reading docx files
# TODO Add code to convert doc to docx
import docx2txt

# Application files
import job_spec_processor as jspf
import resume_reader as r_reader  # Docx reading code
import resume_ranker as r_ranker  # Ranking / Sorting for now code


app = Flask(__name__)
app.secret_key = 'spacemonkeymafia'  # TODO Change this later, seriously.

"""

    Index page
    Has two options:
        1. Upload job spec file.
        2. Manually fill job spec form.
"""

@app.route('/')
def index_page():
    return render_template('index.html')


"""
    Redirected from index.html
    In case the user decides to fill the job spec form manually
    TODO GUI Improvements
"""

@app.route('/job_spec_form_manual')
def job_spec_form_manual():
    return render_template('job_spec_form_manual.html')


"""

    In case the user decides to upload job spec file in the
    index route

    This code gets the job spec file
    Sends the file to Job Spec Processor file

"""


@app.route('/get_job_spec_file', methods=['POST'])
def get_job_spec_file():
    job_spec_file = request.files.get('job-spec-file')

    job_spec_text = docx2txt.process(job_spec_file)

    # Send text for processing to job_spec_processor.py
    job_spec_text_processed = jspf.get_job_spec_data(job_spec_text)
    # print(job_spec_text_processed)

    session['to_job_spec_from'] = job_spec_text_processed

    return redirect(url_for('fill_data_job_spec_form'))


# Send data to job spec form for verification and changes
@app.route('/job_spec_form_autofill')
def fill_data_job_spec_form():
    job_spec_text_processed = session.get('to_job_spec_from', None)
    return render_template('job_spec_form_autofill.html', **job_spec_text_processed)


# Gets data from autofill/manual form
@app.route('/final_js_form_data', methods=['POST'])
def yolo():
    from_form_must_keywords = request.form.get('form-must-have-keywords') # Required Keywords
    from_form_optional_keywords = request.form.get('form-optional-keywords') # Optional Keywords 
    from_form_min_exp = request.form.get('form-minimum-experience') # Minimum Experience
    from_form_edu_degree_keywords = request.form.get('form-education-degree') # Education Degree
    from_form_edu_field_keywords = request.form.get(
        'form-education-field-study') # Education Major

    # Combine above to Dictionary
    job_spec_text_to_search = {
        "must_have_keywords": from_form_must_keywords,
        "optional_keywords": from_form_optional_keywords,
        "min_exp": from_form_min_exp,
        "education_degree_keywords": from_form_edu_degree_keywords,
        "education_field_keywords": from_form_edu_field_keywords
    }

    # Save data in session for passing it between routes
    session['keywords_to_search'] = job_spec_text_to_search
    return redirect(url_for('resume_repository_form'))


"""

    #########################################
    ########### RESUME REPOSITORY ###########
    #########################################

"""

# Shows the resume repository form
# User can upload multiple files
# TODO Add functionality to convert doc to docx
@app.route('/resume-repository')
def resume_repository_form():
    return render_template('resume_repo_form.html')

# Get data from resume_repo_form.html
@app.route('/get-resume-repository', methods=['POST'])
def get_resumes():
     # Upload resumes from folder
    # jd_form_resumes_list = request.form.get('form-resumes-list')
    all_resumes_list = []
    for f in request.files.getlist('form-resumes-list'):
        all_resumes_list.append(f)

    # Get data from session
    # These are the that are to be searched in the resume
    keywords_to_search = session.get('keywords_to_search', None)

    # Gets JSON #TODO CLEAN
    # Also has years_of_experience
    cvs_keywords_frequency = r_reader.search_keywords_resumes(
        all_resumes_list, keywords_to_search)

    # Convert JSON to dict
    cvs_keywords_frequency = json.loads(cvs_keywords_frequency)

    # Session has a max limit of 4096 something bytes
    # Hence, creating a temporary file for the Pickle object of the dictionary
    # The other side reads the pickle object
    session['tempdir'] = tempfile.mkdtemp()
    outfile = open(session['tempdir'] + '/cvs_keywords_counts', 'wb')
    pickle.dump(cvs_keywords_frequency, outfile)
    outfile.close()

    return redirect(url_for('rank_resumes'))


@app.route('/rank-resumes')
def rank_resumes():
    # Gets JSON
    keywords_to_search = session.get('keywords_to_search', None)

    infile = open(session['tempdir'] + '/cvs_keywords_counts', 'rb')
    cvs_keywords_frequency = pickle.load(infile)
    infile.close()
    shutil.rmtree(session['tempdir'])
    session.pop('tempdir', None)

    cvs_cos_sim_must_have_score, cvs_cos_sim_optional_score, percentage_match, keywords_frequency = r_ranker.prepare_data_for_ranking(
        cvs_keywords_frequency, keywords_to_search)

    # print('\n ########## {} ############ \n'.format('KEYWORDS TO SERACH FROM RESUMES'))
    # print('\n {}'.format(keywords_to_search))
    # print('\n ############################################################# \n')

    # print('\n ########## {} ############ \n'.format('EXTRACTED KEYWORDS FROM RESUMES'))
    # print('\n {}'.format(keywords_frequency))
    # print('\n ############################################################# \n')



    
    #TODO Adding weights metrics
    """
        As per discussion on 20/12/2018
        Required Keywords - 0.5
        Years of experience - 0.3
        Optional Keyword - 0.1
        Education Degree - 0.1

        As per discussion on 24/12/2018
        Required Keywords - 0.3
        Years of experience - 0.5
        Optional Keyword - 0.1
        Education Degree - 0.1

        Approach:
        Divide the weights above by count of Job Specification Keywords (For Required Keywords and Optional
    
    """

    # Get count for must have keywords
    # Get count for optional keywords
    for jd_keywords_identifier, jd_keywords in keywords_to_search.items():
        if jd_keywords_identifier == 'must_have_keywords':
            required_keywords_list = jd_keywords.split(',')
            # Length stored here
            jd_required_keywords_count = len(required_keywords_list)
        elif jd_keywords_identifier == 'optional_keywords':
            optional_keywords_list = jd_keywords.split(',')
            # Length stored here
            jd_optional_keywords_count = len(optional_keywords_list)
        else:
            continue


    # To store the final candidate data
    outer_dict = {}
    for candidate_name_keywords_frequency, candidate_data_keywords_frequency in keywords_frequency.items():
        inner_dict = OrderedDict()
        for legend_idetifier, legends in candidate_data_keywords_frequency.items():
            if legend_idetifier == 'education_degree':
                inner_dict['Education Degree'] = legends
                score_education_degree = 0.1
                # inner_dict['Education Degree Score'] = score_education_degree # -------------------------------------------------------- EDUCATION DEGREE SCORE
                continue
            elif legend_idetifier == 'education_field_study':
                inner_dict['Education Major'] = legends
                continue
            elif legend_idetifier == 'must_have_keywords':
                inner_dict['Must Have Keywords Frequencies'] = legends
                # Calculating count of Must Have Keywords
                candidate_required_keywords_total_count = 0
                for keyword_name, keyword_count in legends.items():
                    candidate_required_keywords_total_count = candidate_required_keywords_total_count + keyword_count
                    score_must_have_keywords = (0.3/jd_required_keywords_count) * candidate_required_keywords_total_count
                    # inner_dict['Must Have Keywords Score'] = score_must_have_keywords #----  REQUIRED KEYWORDS SCORE
                continue
            elif legend_idetifier == 'optional_keywords':
                inner_dict['Optional keywords Frequencies'] = legends
                # Calculating count of Optional Keywords
                candidate_optional_keywords_total_count = 0
                for keyword_name, keyword_count in legends.items():
                    candidate_optional_keywords_total_count = candidate_optional_keywords_total_count + keyword_count
                    score_optional_keywords = (0.1/jd_optional_keywords_count) * candidate_optional_keywords_total_count
                    # inner_dict['Optional Keywords Score'] = score_optional_keywords #----- OPTIONAL KEYWORDS SCORE
                continue
            elif legend_idetifier == 'years_of_experience':
                inner_dict['Years of Experience'] = legends
                score_years_of_experience = int(legends) * 0.5
                # inner_dict['Years of Experience Score'] = score_years_of_experience

        for candidate_name_percentage_match, candidate_data_percentage_match in percentage_match.items():
            if candidate_name_percentage_match == candidate_name_keywords_frequency:
                for legend_idetifier, legends_x in candidate_data_percentage_match.items():
                    if legend_idetifier == 'Percentage match must have':
                        inner_dict['Percentage Match Must Have'] = legends_x
                    else:
                        inner_dict['Percentage Match Optional'] = legends_x

        for candidate_name_cosine_must, candidate_data_cosine_must in cvs_cos_sim_must_have_score.items():
            if candidate_name_cosine_must == candidate_name_keywords_frequency:
                inner_dict['Cosine Similarity Must Have Keywords'] = candidate_data_cosine_must

        for candidate_name_cosine_optional, candidate_data_cosine_optional in cvs_cos_sim_optional_score.items():
            if candidate_name_cosine_optional == candidate_name_keywords_frequency:
                inner_dict['Cosine Similarity Optional Keywords'] = candidate_data_cosine_optional

        score_total = score_must_have_keywords + score_years_of_experience + score_optional_keywords + score_education_degree
        inner_dict['Candidate Overall Score'] = score_total
        outer_dict[candidate_name_keywords_frequency] = inner_dict

    print(outer_dict)
    # Converting final dictionary to pandas dataframe
    # Transpose it
    # Write to csv as backup #TODO developemnt, remove in production
    output_df = pd.DataFrame(outer_dict)
    output_df = output_df.T
    # output_df = output_df.sort_values(by=['Years of Experience' ,'Cosine Similarity Must Have Keywords', 'Cosine Similarity Optional Keywords'], ascending = False)
    output_df = output_df.sort_values(by=['Candidate Overall Score'], ascending = False)

    df_template = output_df.drop(columns=[
                                 'Cosine Similarity Must Have Keywords', 'Cosine Similarity Optional Keywords'], axis=1)
    df_template['Percentage Required'] = df_template['Percentage Match Must Have'].str.rstrip(
        '%').astype('float') / 100.0
    df_template['Percentage Optional'] = df_template['Percentage Match Optional'].str.rstrip(
        '%').astype('float') / 100.0
    # df_template = df_template.sort_values(
    #     by=['Years of Experience', 'Percentage Required', 'Percentage Optional'], ascending=False)
    # To stop to_html from truncating strings
    pd.set_option('display.max_colwidth', -1)
    df_template = df_template.drop(
        columns=['Percentage Required', 'Percentage Optional'], axis=1)

    # output_df.to_csv('test.csv')

    # print('Data types-------------------------------- \n {}'.format(output_df.dtypes))

    # For better output in the template
    # Copyting dictionar
    # Change names of keys
    keywords_to_search_for_template = keywords_to_search

    keywords_to_search_for_template['Education Degree'] = keywords_to_search_for_template.pop(
        'education_degree_keywords')
    keywords_to_search_for_template['Education Major'] = keywords_to_search_for_template.pop(
        'education_field_keywords')
    keywords_to_search_for_template['Minimum Experience In Years'] = keywords_to_search_for_template.pop(
        'min_exp')
    keywords_to_search_for_template['Required Skills'] = keywords_to_search_for_template.pop(
        'must_have_keywords')
    keywords_to_search_for_template['Optional Skills'] = keywords_to_search_for_template.pop(
        'optional_keywords')

    return render_template('table_output.html', results=df_template, keywords_searched=keywords_to_search_for_template)
    # return render_template('form_output.html', bozo=outer_dict)#TODO Rename BOZO / Might want to remove this
    ###############################################



# Run application
# Debug = False in production
if __name__ == "__main__":
    app.run(debug=True)
