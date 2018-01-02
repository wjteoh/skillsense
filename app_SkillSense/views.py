import os
from app_SkillSense import app_Isc
from flask import Blueprint, render_template, jsonify, request, url_for, redirect, Markup
import pandas as pd
import json
import csv
import math
from collections import Counter
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import plotly.plotly as py
import time
import webbrowser


# Load data from data directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # refers to application_top
DATA_DIR = os.path.join(BASE_DIR, 'data/')

# jobpost_df = pd.read_csv(DATA_DIR + '/doc_index_filter.csv', keep_default_na=False)

relation_nodes_df = pd.read_csv(DATA_DIR + '/node_DomainFunctionTopic.csv', keep_default_na=False)
relation_links_df = pd.read_csv(DATA_DIR + '/edge_DomainFunctionTopic.csv', keep_default_na=False)
label_dict = dict(zip(relation_nodes_df.id, relation_nodes_df.label))
label_id_dict = dict(zip(relation_nodes_df.label, relation_nodes_df.id))
query_DomOnly = 'nodeType == "{}"'.format('domain')
query_FcnOnly = 'nodeType == "{}"'.format('function')
domain_df = relation_nodes_df.query(query_DomOnly)
function_df = relation_nodes_df.query(query_FcnOnly)
domain_list = sorted(domain_df.label.tolist())
function_list = sorted(function_df.label.tolist())
domain_id_list = sorted(domain_df.id.tolist())
function_id_list = sorted(function_df.id.tolist())

# label_id_dict = dict(zip(relation_nodes_df.label, relation_nodes_df.id))
chord_nodes_df = pd.read_csv(DATA_DIR + '/node_TopicSkill.csv', keep_default_na=False)
chord_links_df = pd.read_csv(DATA_DIR + '/edge_TopicTopic.csv', keep_default_na=False)
ch_label_dict = dict(zip(chord_nodes_df.id, chord_nodes_df.label))
ch_label_id_dict = dict(zip(chord_nodes_df.label, chord_nodes_df.id))
query_TopicOnly = 'nodeType == "{}"'.format('Topic')
query_SkillOnly = 'nodeType == "{}"'.format('Skill')
skillgroup_df = chord_nodes_df.query(query_TopicOnly)
skills_df = chord_nodes_df.query(query_SkillOnly)
skillgroup_list = sorted(skillgroup_df.label.tolist())
skillgroup_id_list = sorted(skillgroup_df.id.tolist())
skills_list = sorted(skills_df.label.tolist())
skills_id_list = sorted(skills_df.id.tolist())

# for comparing resulst of Skills assigned to Skill Groups after IDF
ch_topicskills_links_df = pd.read_csv(DATA_DIR + '/edge_TopicSkill.csv', keep_default_na=False)
ch_topicskills_linksIDF_df = pd.read_csv(DATA_DIR + '/edge_TopicSkillIDF.csv', keep_default_na=False)
sg_s_optm_df = pd.read_csv(DATA_DIR + '/edge_TopicSkillOneRepSkill_46_20171221-1021.csv', keep_default_na=False)

# temporarily unused, Collapsible Tree based representation
# json_url = DATA_DIR + '//funccategory_data_cosine_set4.json'
# s2s_data = json.load(open(json_url))

category_nodes_df = pd.read_csv(DATA_DIR + '/node_word2vec_1.csv', keep_default_na=False)
category_links_df = pd.read_csv(DATA_DIR + '/edge_word2vec_1.csv', keep_default_na=False)
cat_label_dict = dict(zip(category_nodes_df.id, category_nodes_df.title))
cat_label_id_dict = dict(zip(category_nodes_df.title, category_nodes_df.id))

dom_skill_df = pd.read_csv(DATA_DIR + '/edge_DomainSkillGroup(text).csv', keep_default_na=False) # for category - skillgroup: heatmap

# category_jobdict_df = pd.read_csv(DATA_DIR + '/jobstitle_category.csv', keep_default_na=False)
# func_stemmed_dict_df = pd.read_csv(DATA_DIR + '/0728_jobtitle_mainfunc_stemmed.csv', keep_default_na=False)
# func_dict = dict(zip(func_stemmed_dict_df.stemmed, func_stemmed_dict_df.original))

job_posting2016_df = pd.read_csv(DATA_DIR + '/job_posting2016.csv', keep_default_na=False)


@app_Isc.route('/old/')
def home_old():
    return render_template("skillsense_homepage_old.html", sg_list=skillgroup_list, skill_list=skills_list, domain_list=domain_list, function_list=function_list)


@app_Isc.route('/')
def home():
    return render_template("skillsense_homepage.html", sg_list=skillgroup_list, skill_list=skills_list, domain_list=domain_list, function_list=function_list)
    

# # temporary bar chart: popular jobtitles
# @app_Isc.route('/job/popular/')  #new url naming convention
# def popularJobsHTML():
#     return render_template("jobtitle_analysis_popularjobs_barchart.html", ac_list=title_list)


# temporary bar chart: popular jobtitles
# @app_Isc.route('/data/job/popular/') #for relationBipartite_Chord.html: skills bar chart
# def getpopularJobsDATA():
#     title_all = jobpost_df.title.tolist()
#     job_count = Counter(title_all).most_common()  # most_common takes int param for max number of words
#     job_count_df = pd.DataFrame(job_count, columns=['title', 'count'])
#     # job_count_df.to_csv(DATA_DIR + '/jobtitle_frequency(2016).csv', index=False)

#     job_count_data = list(
#         job_count_df.apply(lambda row: {"name": row['title'], "value": row['count']}, axis=1))
#     jsonSkills = json.dumps(job_count_data)
#     return jsonify(job_count_data)


# @app_Isc.route('/<rel_type>')
# def skill_analysisbPHTML_old(rel_type):
#     # return render_template("relationBipartite.html")
#     return render_template("skill_analysis.html", rel_type=rel_type)


@app_Isc.route('/searchItem/', methods=['POST', 'GET'])
def relTypeSearchForm():
    skill_group_field = ''
    if request.method == 'POST':
        searchby_tab = request.form['radio-set']
        skill_group_field = request.form['sg_field'].title()
        category_field = request.form['category_field'].title()
        role_field = request.form['role_field'].title()
        rel_type_sg = request.form['dropdown'] # for search by SKILLGROUP tab
        print "\nEnter TAB :", searchby_tab
        print "Enter Form SG :", skill_group_field
        print "Enter Form CATEGORY:", category_field
        print "Enter Form ROLE:", role_field
        print "Enter Form RELTYPE_SG:", rel_type_sg
        if searchby_tab == "category":
            rel_type = "category"
            searchitem = category_field
        elif searchby_tab == "role":
            rel_type = "role"
            searchitem = role_field
        elif searchby_tab == "skill_group":
            rel_type = rel_type_sg
            searchitem = skill_group_field
    return redirect(url_for('skill_analysisbPHTML', rel_type=rel_type, searchitem=searchitem))


# @app_Isc.route('/<rel_type>? ', defaults={'searchitem': 'null'})
@app_Isc.route('/<rel_type>')
@app_Isc.route('/<rel_type>=<path:searchitem>')
def skill_analysisbPHTML(rel_type, searchitem="null"):
    # print rel_type
    
    # if not searchitem == 'null':
    #     rel_type = request.args.get('rel_type')
    #     searchitem = request.args.get('searchitem')
    print "rel_type", rel_type 
    print "searchitem", searchitem
    
    return render_template("skill_analysis.html", rel_type=rel_type, searchitem=searchitem)


@app_Isc.route('/data/sankey/<job_part>')
def getSkill_analysisSankeyDATA(job_part):
    verbose = True;  # Disable for NON-detail printing in terminal

    if job_part == 'category':
        q = 'nodeType == "{}"'.format('domain')
        threshold = 0.01
    else:
        q = 'nodeType == "{}"'.format('function')
        threshold = 0.045

    nodes_df = relation_nodes_df.query(q)
    node_labels_list = nodes_df.id.tolist()
    type_filter = relation_links_df['source'].isin(node_labels_list)
    # weight_filter = relation_links_df['weight'] >= threshold
    # type_relation_df = relation_links_df[type_filter & weight_filter]
    type_relation_df = relation_links_df[type_filter]  # category/role
    type_relation_df.sort_values(['weight'], ascending=True, inplace=True)
    topic_size = len(type_relation_df.target.unique())
    print "topic_size", topic_size
    type_relation_df.reset_index(level=0, drop=True)
    type_relation_data = list(
            type_relation_df.apply(lambda row: [label_dict[(row['source'])], label_dict[(row['target'])], round(row['weight'], 5)],
                         axis=1))
    print "role-topic total edges", len(type_relation_data)

    type_relation_data = {"primary_size": len(type_relation_df.source.unique()), "secondary_size":topic_size, "data": type_relation_data}

    return jsonify(type_relation_data)


#for Category/Role analysis: get skills bar chart for popular job for Role/Category
@app_Isc.route('/data/popularjobs_barchart/type_category/<path:category>') 
def getCatgyPopularJobs(category):
    k = 20
    cores_category_filter = job_posting2016_df['job_category'] == category.lower()
    sel_cat_df = job_posting2016_df[cores_category_filter].copy()
    print "\nCategory BarChart: \n", category
    title_all = sel_cat_df.title.tolist()
    job_count = Counter(title_all).most_common()  # most_common takes int param for max number of words
    job_count_df = pd.DataFrame(job_count, columns=['title', 'count'])
    job_count_df.sort_values(['count'], ascending=False, inplace=True)
    top20_df = job_count_df.head(k).copy()
    job_count_data = list(
        top20_df.apply(lambda row: {"name": row['title'], "value": row['count']}, axis=1))
    # print top_skills_data
    jsonSkills = json.dumps(job_count_data)
    return jsonify(job_count_data)


# based on role
@app_Isc.route('/data/popularjobs_barchart/type_role/<role>') 
def getRolePopularJobs(role):
    k = 20
    cores_role_filter = job_posting2016_df['job_role'] == role.lower()
    sel_role_df = job_posting2016_df[cores_role_filter].copy()
    print "\nRole BarChart: ", role
    sel_role_df.drop_duplicates(['job_id'])
    title_all = sel_role_df.title.tolist()
    job_count = Counter(title_all).most_common()  # most_common takes int param for max number of words
    job_count_df = pd.DataFrame(job_count, columns=['title', 'count'])
    job_count_df.sort_values(['count'], ascending=False, inplace=True)
    top20_df = job_count_df.head(k).copy()
    job_count_data = list(
        top20_df.apply(lambda row: {"name": row['title'].title(), "value": row['count']}, axis=1))
    # print top_skills_data
    jsonSkills = json.dumps(job_count_data)
    return jsonify(job_count_data)


@app_Isc.route('/old/<rel_type>')
@app_Isc.route('/old/<rel_type>=<path:searchitem>')
def skill_analysisbPHTMLTEMP(rel_type, searchitem="null"):
  
    # if not searchitem == 'null':
    #     rel_type = request.args.get('rel_type')
    #     searchitem = request.args.get('searchitem')
    print rel_type 
    print searchitem
    
    return render_template("skill_analysis_olddesign.html", skill_list=skills_list, rel_type=rel_type, searchitem=searchitem)


# @app_Isc.route('/tempskill/<rel_type>')
# @app_Isc.route('/tempskill/<rel_type>=<path:searchitem>')
# def skill_analysisbPHTMLTEMPSKILL(rel_type, searchitem="null"):
  
#     # if not searchitem == 'null':
#     #     rel_type = request.args.get('rel_type')
#     #     searchitem = request.args.get('searchitem')
#     print rel_type 
#     print searchitem
    
#     return render_template("skill_analysis_NEW_skill.html", skill_list=skills_list, rel_type=rel_type, searchitem=searchitem)


@app_Isc.route('/skill_groupIDF/')
def getSGSkillBarChart():   
    return render_template("skill_analysis_skillIDF_barchart.html", sg_list=skillgroup_list)


@app_Isc.route('/sg_skills_popularity/boxplot/')
def getsg_skills_popularity():   
    return render_template("skill_analysis_sg_skills_popularity_boxplot.html")
    

@app_Isc.route('/data/sg_skills_popularity/boxplot/') #for relationBipartite_Chord.html: skills bar chart
def getsg_skills_popularity_BoxPlot():
    skill_count_df = pd.read_csv(DATA_DIR + '/stat_2016_skill_count.csv', keep_default_na=False)
    skill_count_dict = dict(zip(skill_count_df.skill_name, skill_count_df.count))
    sg_csv_list = []
    for skill_group_id in skillgroup_id_list:
        cores_skill_group_filter = ch_topicskills_linksIDF_df['source'] == skill_group_id
        selected_sg_df = ch_topicskills_linksIDF_df[cores_skill_group_filter].copy()
        skill_id_list = selected_sg_df.target.tolist()
        skill_list = [ch_label_dict[skill_id] for skill_id in skill_id_list]
        sg_filter = skill_count_df['skill_name'].isin(skill_list)
        sg_csv_df = skill_count_df[sg_filter]
        sg_csv_df.rename(columns={"target": "source", "source": "target"}, inplace=True)

    return jsonify(trip_temp_df)


# Diagram type: Sankey Diagram
# Output data: Job Category & Role relation to skill groups from skill input
# Output data type: JSON
# temporarily unused
@app_Isc.route('/data/<path:skill>')  # from skill analysis, input skill name
def getSkillGroup(skill):
    # k = 20
    skill_id = ch_label_id_dict[skill]
    cores_skill_filter = ch_topicskills_links_df['target'] == skill_id
    selected_sg_df = ch_topicskills_links_df[cores_skill_filter].copy()
    tempskillgp_list = selected_sg_df.source.tolist()
    skillgp_list = [label_id_dict[ch_label_dict[sg]] for sg in tempskillgp_list]
    sg_filter = relation_links_df['target'].isin(skillgp_list)
    sg_rel_df = relation_links_df[sg_filter]
    unique_id_skillgp_list = sg_rel_df.target.unique()
    unique_skillgp_list = [label_dict[sg_id] for sg_id in unique_id_skillgp_list]

    dom_filter = sg_rel_df['source'].isin(domain_id_list)
    # dom_weight_filter = sg_rel_df['weight'] >= 0.01
    func_filter = sg_rel_df['source'].isin(function_id_list)
    # func_weight_filter = sg_rel_df['weight'] >= 0.045
    # dom_rel_df = sg_rel_df[dom_filter & dom_weight_filter]
    # func_rel_df = sg_rel_df[func_filter & func_weight_filter]
    dom_rel_df = sg_rel_df[dom_filter]
    func_rel_df = sg_rel_df[func_filter]
    fn_size = len(func_rel_df.source.unique())
    print "\nfn_size", fn_size

    # selected_sg_df.sort_values(['weight'], ascending=False, inplace=True)
    dom_rel_df.sort_values(['target', 'weight'], ascending=[True,False], inplace=True)
    func_rel_df.sort_values(['target', 'weight'], ascending=[True,False], inplace=True)
    # print "Number of skills: ", selected_sg_df.shape[0]
    # top10_df = selected_sg_df.head(k).copy()
    dom_relation_data = list(
            dom_rel_df.apply(lambda row: [label_dict[(row['target'])], label_dict[(row['source'])], round(row['weight'], 5)],
                         axis=1))
    func_relation_data = list(
            func_rel_df.apply(lambda row: [label_dict[(row['target'])], label_dict[(row['source'])], round(row['weight'], 5)],
                         axis=1))
        
    type_relation_data = {"all_skill_gp": sorted(unique_skillgp_list), "dom_data": dom_relation_data, "func_data": func_relation_data}

    return jsonify(type_relation_data)


# @app_Isc.route('/data/job_list/category/<category>')
# def getCategoryJobsDATA():
#     #return

#     # category_jobdict_df['new_function'] = category_jobdict_df.apply(lambda row: func_dict[row['function']], axis=1)
#     category_jobdict_df['new_function'] = category_jobdict_df.apply(lambda row: getProperFunc(row['function']) , axis=1)

#     category_jobdict_df['title'] = category_jobdict_df['domain'] + " " + category_jobdict_df['new_function']
#     category_jobdict_df.sort_values(['title'], ascending=True, inplace=True)
#     category_jobdict_df.to_csv(DATA_DIR + '/Relational/category_jobtitle_dict2.csv', index=False)

#     return jsonify(category_jobdict_df)


@app_Isc.route('/data/skill_group/')
def getSkill_analysisChordDATA():
    verbose = True;  # Disable for NON-detail printing in terminal
    combined_df = chord_links_df.copy()
    threshold = 0.02
    # weight_filter = chord_links_df['weight'] >= threshold
    # combined_df = combined_df[weight_filter]
    skill_group_data = list(
        combined_df.apply(lambda row: [ch_label_dict[(row['source'])], ch_label_dict[(row['target'])], round(row['weight'], 5)],
                     axis=1))
    print "chord_links_df size", len(skill_group_data)

    return jsonify(skill_group_data)


@app_Isc.route('/data/skills_barchart/<skill_group_name>') #for relationBipartite_Chord.html: skills bar chart
def getChordSkillsJSON(skill_group_name):
    k = 20
    skill_group_id = ch_label_id_dict[skill_group_name]
    cores_skill_group_filter = ch_topicskills_links_df['source'] == skill_group_id
    selected_sg_df = ch_topicskills_links_df[cores_skill_group_filter].copy()
    selected_sg_df.sort_values(['weight'], ascending=False, inplace=True)
    print skill_group_name, "\nNumber of skills before IDF: \n", selected_sg_df.shape[0]
    top10_df = selected_sg_df.head(k).copy()
    top_skills_data = list(
        top10_df.apply(lambda row: {"name": ch_label_dict[(row['target'])], "value": row['weight']}, axis=1))
    # print top_skills_data
    jsonSkills = json.dumps(top_skills_data)
    return jsonify(top_skills_data)


@app_Isc.route('/data/skills_barchartIDF/<skill_group_name>') #for relationBipartite_Chord.html: skills bar chart
def getSkillsinSG(skill_group_name):
    k = 20
    skill_group_id = ch_label_id_dict[skill_group_name]
    cores_skill_group_filter = ch_topicskills_linksIDF_df['source'] == skill_group_id
    selected_sg_df = ch_topicskills_linksIDF_df[cores_skill_group_filter].copy()
    selected_sg_df.sort_values(['weight'], ascending=False, inplace=True)
    print "Number of skills after IDF: \n", selected_sg_df.shape[0]
    top10_df = selected_sg_df.head(k).copy()
    top_skills_data = list(
        top10_df.apply(lambda row: {"name": ch_label_dict[(row['target'])], "value": row['weight']}, axis=1))
    # print top_skills_data
    jsonSkills = json.dumps(top_skills_data)
    return jsonify(top_skills_data)


@app_Isc.route('/data/skills_barchartOneRep/<skill_group_name>') #for relationBipartite_Chord.html: skills bar chart
def getSkillsinSGOpt(skill_group_name):
    k = 20
    skill_group_id = ch_label_id_dict[skill_group_name]
    cores_skill_group_filter = sg_s_optm_df['source'] == skill_group_id
    selected_sg_df = sg_s_optm_df[cores_skill_group_filter].copy()
    selected_sg_df.sort_values(['weight'], ascending=False, inplace=True)
    print "Number of skills after One SKill Rep One SG: \n", selected_sg_df.shape[0]
    top10_df = selected_sg_df.head(k).copy()
    top_skills_data = list(
        top10_df.apply(lambda row: {"name": ch_label_dict[(row['target'])], "value": row['weight']}, axis=1))
    # print top_skills_data
    jsonSkills = json.dumps(top_skills_data)
    barchart_data = [int(skill_group_id), top_skills_data, selected_sg_df.shape[0]]
    return jsonify(barchart_data)


@app_Isc.route('/data/skills_barchart/summary/') # Number of skills in each skill groups: skills bar chart
def getNumberOfSkills():
    # k = 20
    # skill_group_id = ch_label_id_dict[skill_group_name]
    listofskill = []
    rid = [36,40,47,52,53,64,18,23,61,45,30,29,43,59,32,0,5,44,46] # removed qty: 4>11>2>2
    for sg_id in range(65): 
        if sg_id in rid:
            continue
        cores_skill_group_filter = sg_s_optm_df['source'] == sg_id
        selected_sg_df = sg_s_optm_df[cores_skill_group_filter].copy()
        tmp_dict = {"name": ch_label_dict[sg_id], "value": selected_sg_df.shape[0]}
        listofskill.append(tmp_dict)
    return jsonify(listofskill)


@app_Isc.route('/data/poplrjob_barchart/<function>') #for relationBipartite_Chord.html: skills bar chart
def getPopularJobsbyType(function):
    k = 20
    skill_group_id = ch_label_id_dict[skill_group_name]
    cores_skill_group_filter = ch_topicskills_links_df['source'] == skill_group_id
    selected_sg_df = ch_topicskills_links_df[cores_skill_group_filter].copy()
    selected_sg_df.sort_values(['weight'], ascending=False, inplace=True)
    print "Number of skills: ", selected_sg_df.shape[0]
    top10_df = selected_sg_df.head(k).copy()
    top_skills_data = list(
        top10_df.apply(lambda row: {"name": ch_label_dict[(row['target'])], "value": row['weight']}, axis=1))
    # print top_skills_data
    jsonSkills = json.dumps(top_skills_data)
    return jsonify(top_skills_data)


# Diagram type: Force Directed
# Output data: Related Skills based on input skill
# Output data type: JSON
# for relationBipartite_Chord.html: skills force directed
@app_Isc.route('/data/skillsnetw/<skill_name>')  
def getRelatedSkills(skill_name):
    verbose = True;  # Disable for NON-detail printing in terminal

    if skill_name.lower() not in s2s_data:
        return jsonify(json.dumps({"skill_name": "not_found"}))

    links_list = []
    for n, skill in enumerate(s2s_data[skill_name.lower()]):
        record = {"value": skill['d'], "source": 0, "target": (n+1)}
        links_list.append(record)

    nodes_list = [{"id": "skill_0", "name": skill_name.lower(), "weight": 0}]
    for n, skill in enumerate(s2s_data[skill_name.lower()]):
        nodes_list.append({"id": "skill_{}".format(n+1), "name": skill["w"], "weight": skill["d"]})

    # for i in nodes_list:
    #     print i

    json_prep = {"skill_name": skill_name.lower(), "nodes": nodes_list, "links": links_list}

    jsonData = json.dumps(json_prep)

    # return render_template("network.html", job_title=jobtitle, json_data=jsonify(data), ac_list=autocomplete_f)
    return jsonify(jsonData)


#from tianyuan, collapsible tree, skillstoskills_coltree.html
@app_Isc.route('/external/')  
def skill2skillTempHTML():
    return render_template("skillstoskills_coltree.html")


@app_Isc.route('/data/external/')
def getskill2skillTempDATA():
    # json_url = DATA_DIR + '/Relational/word2vect_skills/funccategory_data_cosine_set4.json'
    data = json.load(open(json_url))
    return jsonify(data)


@app_Isc.route('/data/external/search_list/')  #get skill search autocomplete data
def getSkill2skillSearchAutocomplete():
    return chord_nodes_df.to_csv()


@app_Isc.route('/categoryjob/')  #from tianyuan, seperate app, hierarchical
def categoryJobHTML():
    return render_template("categoryjob.html")


@app_Isc.route('/data/categoryjob/')
def getCategoryJobDATA():
    verbose = True;  # Disable for NON-detail printing in terminal

    # dom_q = 'nodeType == "{}"'.format('domain')
    # func_q = 'nodeType == "{}"'.format('function')
    # domain_nodes_df = relation_nodes_df.query(dom_q)
    # function_nodes_df = relation_nodes_df.query(func_q)
    # domain_node_labels_list = domain_nodes_df.id.tolist()
    # function_node_labels_list = function_nodes_df.id.tolist()
    # category_nodes_df.to_csv(DATA_DIR + '/Relational/word2vect_category/node_word2vec_1_new.csv', sep=",", quoting=csv.QUOTE_NONNUMERIC, index=False)
    threshold = 10
    weight_filter = category_nodes_df['weight'] > threshold
    # domain_filter = relation_links_df['source'].isin(domain_node_labels_list)
    # function_filter = relation_links_df['source'].isin(function_node_labels_list)

    cat_node_df = category_nodes_df[weight_filter]
    pd.set_option('max_rows', cat_node_df.shape[0])
    print "df, n: {}\n".format(cat_node_df.shape[0])
    pd.reset_option('max_rows')

    nodeidlist = cat_node_df.id.tolist()
    edge_source_filter = category_links_df['source'].isin(nodeidlist)
    edge_target_filter = category_links_df['target'].isin(nodeidlist)

    cat_links_df = category_links_df[edge_source_filter & edge_target_filter]
    print "cat_links_df, length: {}\n".format(cat_links_df.shape[0])

    cat_links_df.sort_values(['source', 'target'], ascending=[True,True], inplace=True)
    cat_links_df.reset_index(level=0, drop=True)

    # if verbose:
    #     # for debugging: show values
    #     pass

    dataframe = cat_links_df
    
    unique_t = pd.Index(cat_node_df['title'])

    unique_tname = unique_t.tolist()
    group_dict = {}  # to store title groups
    for title in unique_tname:
        if title not in group_dict:
            cur_title_row = cat_node_df['title'] == title
            group_df = cat_node_df[cur_title_row]
            group_dict[title] = group_df.iloc[0].weight
        else:
            pass

    # # Only take link list of 1 & 2. If only 2-hop titles present, 3 and only 3 will be taken.
    temp_links_list = list(
        dataframe.apply(lambda row: {"source": cat_label_dict[(row['source'])], "target": cat_label_dict[(row['target'])], "value": round(row['weight'], 3)},
                     axis=1))

    links_list = []
    for link in temp_links_list:
        record = {"value": link['value'], "source": unique_t.get_loc(link['source']), "target": unique_t.get_loc(link['target'])}
        links_list.append(record)

    nodes_list = []
    for title in unique_t:
        nodes_list.append({"id": int(cat_label_id_dict[title]), "name": title, "node_weight": int(group_dict.get(title))})

    json_prep = {"nodes": nodes_list, "links": links_list}

    # print json_prep

    jsonData = json.dumps(json_prep)

    return jsonify(json_prep)


# @app_Isc.route('/data/categoryjobPopularity/')
# def getCategoryJobPopularityData():
#     notfoundlist = []
#     def getProperFunc(row_func):
#         if row_func in func_dict:
#             return func_dict[row_func]
#         else:
#             if row_func not in notfoundlist:
#                 notfoundlist.append(row_func)
#             return row_func

#     # category_jobdict_df['new_function'] = category_jobdict_df.apply(lambda row: func_dict[row['function']], axis=1)
#     category_jobdict_df['new_function'] = category_jobdict_df.apply(lambda row: getProperFunc(row['function']) , axis=1)
#     notfounddata = pd.DataFrame(notfoundlist, columns=['not_found_titles'])
#     notfounddata.to_csv(DATA_DIR + '/Relational/category_jobtitle_dict2(NOTFOUND).csv', index=False)

#     category_jobdict_df['title'] = category_jobdict_df['domain'] + " " + category_jobdict_df['new_function']
#     category_jobdict_df.sort_values(['title'], ascending=True, inplace=True)
#     category_jobdict_df.to_csv(DATA_DIR + '/Relational/category_jobtitle_dict2.csv', index=False)

#     return jsonify(category_jobdict_df)


@app_Isc.route('/heatmap/')
def getJobSkill():
    return render_template("skillcategory_heatmap.html")


@app_Isc.route('/data/network/relation/bPtestDOM/')
def getBipartiteDataTESTDOM():
    q = 'nodeType == "{}"'.format('domain')

    nodes_df = relation_nodes_df.query(q)
    node_labels_list = nodes_df.id.tolist()
    type_filter = relation_links_df['source'].isin(node_labels_list)
    # weight_filter = relation_links_df['weight'] >= threshold
    # type_relation_df = relation_links_df[type_filter & weight_filter]
    type_relation_df = relation_links_df[type_filter]  # category/role
    type_relation_df.sort_values(['target', 'source'], ascending=[True,True], inplace=True)
    topic_size = len(type_relation_df.target.unique())
    print "\nskill group size: {}\n".format(topic_size)
    columns_temp = sorted(type_relation_df.source.unique().tolist())
    index_temp = sorted(type_relation_df.target.unique().tolist())
    start = 3866
    print "\ncolumns_temp: {}\n".format(columns_temp)
    print "columns_temp:\n", columns_temp
    for index in index_temp:
        sel_target_df = type_relation_df['target'] == index
        tmpdf = type_relation_df[sel_target_df].copy()
        for column in columns_temp:
            if column not in tmpdf.source.tolist():
                type_relation_df = type_relation_df.append(pd.DataFrame([[column, index, start+1, 0]], columns=['source', 'target', 'id', 'weight']))
                start += 1
            else:
                pass

    type_relation_df.sort_values(['target', 'source'], ascending=[True,True], inplace=True)

    type_relation_df.reset_index(level=0, drop=True)

    # pd.set_option('max_rows', type_relation_df.shape[0])
    # print "df, n: {}\n".format(type_relation_df.shape[0]), type_relation_df
    # pd.reset_option('max_rows')
    # type_relation_df.to_csv(DATA_DIR + '/Relational/edge_DomainSkillGroup.csv', index=False)

    temp_columns = []
    for column in columns_temp:
        temp_columns.append(["R", label_dict[column]])

    temp_index = []
    for index in index_temp:
        temp_index.append([label_dict[index]])

    data = []
    for index in index_temp:
        filterbytarget = type_relation_df["target"] == index
        tmptargetdf = type_relation_df[filterbytarget].copy()
        data_row = tmptargetdf.weight.tolist()
        data.append([round(elem, 4) for elem in data_row])

    # data = list(
    #     type_relation_df.apply(lambda row: round(row['weight'], 4),
    #                  axis=1))

    type_relation_data = {"columns": temp_columns, "index": temp_index, "data": data}
    final_data = json.dumps(type_relation_data)

    return jsonify(type_relation_data)


@app_Isc.route('/prep/data/jobskill/heatmap/')  # convert id to text
def prepJobSkillData():
    new_temp_df = list(
        dom_skill_df.apply(lambda row: [label_dict[(row['source'])], label_dict[(row['target'])], round(row['weight'], 5)],
                     axis=1))

    print "new_temp_df", new_temp_df
    new_df = pd.DataFrame(new_temp_df, columns=['source', 'target', 'weight'])
    new_df.sort_values(['target', 'source'], ascending=[True,True], inplace=True)
    # new_df.to_csv(DATA_DIR + '/Relational/edge_DomainSkillGroup(Text).csv', index=False)


    return jsonify(new_df)


@app_Isc.route('/data/heatmap/')
def getJobSkillData():
    # later need to do if dom then > if func then diff dataframe selected
    columns_temp = sorted(dom_skill_df.source.unique().tolist())
    index_temp = sorted(dom_skill_df.target.unique().tolist())
    temp_columns = []
    for column in columns_temp:
        # temp_columns.append(["R", label_dict[column]])
        temp_columns.append(["R", column])

    temp_index = []
    for index in index_temp:
        # temp_index.append([label_dict[index]])
        temp_index.append([index])

    data = []
    for index in index_temp:
        filterbytarget = dom_skill_df["target"] == index
        tmptargetdf = dom_skill_df[filterbytarget].copy()
        data_row = tmptargetdf.weight.tolist()
        data.append([round(elem, 4) for elem in data_row])

    # data = list(
    #     type_relation_df.apply(lambda row: round(row['weight'], 4),
    #                  axis=1))

    type_relation_data = {"columns": temp_columns, "index": temp_index, "data": data}
    final_data = json.dumps(type_relation_data)

    return jsonify(type_relation_data)


# @app_Isc.route('/ACCESSnSAVEcsv/')
# def saveCSV():
#     cores_skill_group_filter = ch_topicskills_links_df['target'] < 11505  #start from 11505 duplicated
#     selected_sg_df = ch_topicskills_links_df[cores_skill_group_filter].copy()
#     selected_sg_df.sort_values(['source', 'target'], ascending=[True,True], inplace=True)
#     selected_sg_df.to_csv(DATA_DIR + '/Relational/edge_TopicSkill.csv', index=False)
#     return jsonify(selected_sg_df)
#     # return render_template("landing.html")

# @app_Isc.route('/MIRRORnSavecsv/')
# def mirrorCSV():
#     tmp_df = chord_links_df.copy()
#     new_column_arrgm = ['target', 'source', 'weight']
#     tmp_df = tmp_df.reindex(columns=new_column_arrgm)
#     tmp_df.rename(columns={"target": "source", "source": "target"}, inplace=True)
#     combined_df = chord_links_df.append(tmp_df, ignore_index=True)
#     combined_df.sort_values(['source','target'], ascending=[True,True], inplace=True)
#     combined_df.reset_index(drop=True)
#     combined_df.to_csv(DATA_DIR + '/Relational/new_edge_TopicTopic.csv', index=False)
#     # pd.set_option('max_rows', combined_df.shape[0])
#     # print "combined_df\n", combined_df
#     # pd.reset_option('max_rows')
#     print "\nsum of source == 0\n", combined_df.loc[combined_df['source'] == 0, 'weight'].sum() , "\n"

#     skill_group_data = list(
#         combined_df.apply(lambda row: [ch_label_dict[(row['source'])], ch_label_dict[(row['target'])], round(row['weight'], 5)],
#                      axis=1))
#     print "chord_links_df size", len(skill_group_data)
#     rel_data = skill_group_data

#     return jsonify(rel_data)


# extract top 20 skills for respective (65)skill_groups
# @app_Isc.route('/prep/data/skills_barchart/') #for relationBipartite_Chord.html: skills bar chart
# def prepSkillGroup2SkillsJSON():
#     k = 20
#     skill_group_list = ch_topicskills_links_df.source.unique().tolist()
#     skill_dict = {}
#     for skill_group in skill_group_list:
#         cores_skill_group_filter = ch_topicskills_links_df['source'] == skill_group
#         selected_sg_df = ch_topicskills_links_df[cores_skill_group_filter].copy()
#         selected_sg_df.sort_values(['weight'], ascending=False, inplace=True)
#         print "Number of skills: ", selected_sg_df.shape[0]
#         top10_df = selected_sg_df.head(k).copy()
#         top_skills_list =  [ch_label_dict[skill_id] for skill_id in top10_df.target.tolist()]
#         skill_dict[ch_label_dict[skill_group]] = top_skills_list
#     # jsonSkills = json.dumps(top_skills_data)
#     return jsonify(skill_dict)


@app_Isc.route('/data/skill_dict/')  #for relationBipartite_Chord.html: skills force directed
def prepSkillAvail():
    skill_list = ch_topicskills_links_df.target.unique().tolist()
    skill_dict = [[skill, ch_label_dict[skill]] for skill in skill_list]
    skill_list_df = pd.DataFrame(skill_dict, columns=['id', 'skill'])
    skill_list_df.sort_values(['skill'], ascending=True, inplace=True)
    # skill_list_df.to_csv(DATA_DIR + '/Relational/skills_dict_temp.csv', index=False)
    # return render_template("network.html", job_title=jobtitle, json_data=jsonify(data), ac_list=autocomplete_f)
    return jsonify(skill_list_df)


@app_Isc.route('/data/recalcIDF/') #for relationBipartite_Chord.html: skills bar chart
def prepIDFNEWTopicSKillWeights():
    for selector_skillid in skills_id_list:
        print selector_skillid, ch_label_dict[selector_skillid]
        filter_sel_skill = ch_topicskills_links_df['target'] == selector_skillid
        nSG_sel_skill = ch_topicskills_links_df[filter_sel_skill].shape[0]
        print "num of SG for ", ch_label_dict[selector_skillid], " = ",  nSG_sel_skill
        if int(nSG_sel_skill) == 0:
            continue
        idf_sel_skill = math.log(len(skillgroup_list) / int(nSG_sel_skill))
        ch_topicskills_links_df.loc[ch_topicskills_links_df['target']==selector_skillid, ['weight']] *= idf_sel_skill
        print "* idf = ", idf_sel_skill

    ch_topicskills_links_df.sort_values(['source', 'weight'], ascending=[True,False], inplace=True)
    # ch_topicskills_links_df.to_csv(DATA_DIR + '/edge_TopicSkillIDF.csv', index=False)

    return jsonify(ch_topicskills_links_df)


# @app_Isc.route('/data/optmimize/') #for relationBipartite_Chord.html: skills bar chart
# def prepOptIDFNEWTopicSKillWeights():
#     master_list = []
#     for selector_skillid in skills_id_list:
#         filterbyskill = sg_s_optm_df['target'] == selector_skillid
#         skillrows = sg_s_optm_df[filterbyskill].copy()
#         if skillrows.shape[0] == 0:
#             continue
#         master_list.append([skillrows.iloc[0].source, skillrows.iloc[0].target, skillrows.iloc[0].weight])

#     optimized_sg_s_df = pd.DataFrame(master_list, columns=['source', 'target', 'weight'])
#     optimized_sg_s_df.sort_values(['target', 'weight'], ascending=[True,False], inplace=True)
#     optimized_sg_s_df.to_csv(DATA_DIR + '/edge_TopicSkillOptimized.csv', index=False)
#     # ch_topicskills_links_df.to_csv(DATA_DIR + '/Relational/edge_TopicSkillNEW.csv', index=False)

#     return jsonify(optimized_sg_s_df)


@app_Isc.route('/data/getNewRepSkills/') # to assign one skill to only one skill group, from each mapping to SG, take highest weight:
def prepNewRepSkills():
    master_list = []
    skills_wo_group = []
    ch_topicskills_linksIDF_df.sort_values(['target', 'weight'], ascending=[True,False], inplace=True)
    for selector_skillid in skills_id_list:
        filterbyskill = ch_topicskills_linksIDF_df['target'] == selector_skillid
        skillrows = ch_topicskills_linksIDF_df[filterbyskill].copy()
        if skillrows.shape[0] == 0:
            skills_wo_group.append([selector_skillid, ch_label_dict[selector_skillid]])
            continue
        master_list.append([skillrows.iloc[0].source, skillrows.iloc[0].target, skillrows.iloc[0].weight])
        print ch_label_dict[selector_skillid]

    skills_wo_grp_df = pd.DataFrame(skills_wo_group, columns=['id', 'skill_name'])
    
    timestr = time.strftime("%Y%m%d-%H%M")
    fname = 'dict_Skills_wo_group'+timestr+'.csv'
    # skills_wo_grp_df.to_csv(DATA_DIR + '/' + fname, index=False)

    onerep_sg_s_df = pd.DataFrame(master_list, columns=['source', 'target', 'weight'])
    onerep_sg_s_df.sort_values(['target', 'weight'], ascending=[True,False], inplace=True)
    fname2 = 'edge_TopicSkillOneRepSkill_'+ len(skillgroup_list) +'_'+timestr+'.csv'
    # onerep_sg_s_df.to_csv(DATA_DIR + '/'+ fname2, index=False)

    return jsonify(onerep_sg_s_df)


@app_Isc.route('/data/matplotlib_boxplot/boxplot/')
@app_Isc.route('/data/matplotlib_boxplot/boxplot/<k>') # box plot for skills_population
def matplotlib_boxplot(k=None):
    # set K = 5/10/20/50/100
    mpl.use('agg')
    skill_count_df = pd.read_csv(DATA_DIR + '/stat_skill_2016_count_new.csv', keep_default_na=False)
    sg_csv_list = []
    y_label_concat = []
    custom_x_label = []
    for skill_group_id in skillgroup_id_list:
        cores_skill_group_filter = ch_topicskills_linksIDF_df['source'] == skill_group_id
        selected_sg_df = ch_topicskills_linksIDF_df[cores_skill_group_filter].copy()
        # selected_sg_df.sort_values(['weight'], ascending=False, inplace=True)
        if not k == None:
            selected_sg_df = selected_sg_df.head(int(k)).copy()
        skill_id_list = selected_sg_df.target.tolist()
        skill_list = [ch_label_dict[int(skill_id)].lower() for skill_id in skill_id_list]
        sg_filter = skill_count_df['skill_name'].isin(skill_list)
        sg_csv_df = skill_count_df[sg_filter].copy()
        sg_data_temp = sg_csv_df.jobs_count.tolist()
        sg_data = np.array([int(skill_count) for skill_count in sg_data_temp])
        # sg_data = [int(skill_count) for skill_count in sg_data_temp]
        sg_csv_list.append(sg_data)
        # y_label_concat += sg_data
        custom_x_label.append(skill_group_id)

    # Create a figure instance
    fig = plt.figure(1, figsize=(22, 9))

    # Create an axes instance
    ax = fig.add_subplot(111)

    # for i in sg_csv_list:
    #     print i

    # Create the boxplot
    ## to get fill color
    bp = ax.boxplot(sg_csv_list, patch_artist=True)

    ## change outline color, fill color and linewidth of the boxes
    for box in bp['boxes']:
        # change outline color
        box.set( color='#7570b3', linewidth=2)
        # change fill color
        # box.set( facecolor = '#ffffff' )
        box.set( facecolor = '#1b9e77' )

    ## change color and linewidth of the whiskers
    for whisker in bp['whiskers']:
        whisker.set(color='#7570b3', linewidth=2)

    ## change color and linewidth of the caps
    for cap in bp['caps']:
        cap.set(color='#7570b3', linewidth=2)

    ## change color and linewidth of the medians
    for median in bp['medians']:
        # median.set(color='#ff0000', linewidth=2)
        median.set(color='#b2df8a', linewidth=2)

    ## change the style of fliers and their fill
    for flier in bp['fliers']:
        flier.set(marker='o', color='#e7298a', alpha=0.5)

    ## Custom x-axis labels
    ax.set_xticklabels(custom_x_label)
    ## Custom y-axis labels
    # ax.set_yticklabels(np.arange(min(y_label_concat), max(y_label_concat)+1, 500.0))

    if not k == None:
        title = 'Popularity Ditribution of Skills for each Skill Group (top ' + k + ' skills in each SG selected)'
    else:
        title = 'Popularity Ditribution of Skills for each Skill Group'
    ax.set_title(title)
    ax.set_xlabel('skill_group(id)')
    ax.set_ylabel('skill_population(no.)')

    ## Remove top axes and right axes ticks
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    if not k == None:
        filename = 'figBoxplot_popularity_distibution-skills(top' + k + 'SGskills).png'
    else:
        filename = 'figBoxplot_popularity_distibution-skills.png'
    # Save the figure
    fig.savefig(filename, bbox_inches='tight')

    return jsonify(fig)


@app_Isc.route('/data/matplotlib_barchart/barchart/') # to show number os skills in each skill group
def matplotlib_barchart():
    objects = []
    performance = []
    for skill_group_id in skillgroup_id_list:
        cores_skill_group_filter = ch_topicskills_linksIDF_df['source'] == skill_group_id
        selected_sg_df = ch_topicskills_linksIDF_df[cores_skill_group_filter].copy()
        performance.append(selected_sg_df.shape[0])
        objects.append(skill_group_id)

    # objects = ('Python', 'C++', 'Java', 'Perl', 'Scala', 'Lisp')
    y_pos = np.arange(len(objects))
    # Get current size
    fig_size = plt.rcParams["figure.figsize"]
     
    # Prints: [8.0, 6.0]
    print "Current size:", fig_size
     
    # Set figure width to 12 and height to 9
    # fig_size[0] = 19
    # fig_size[1] = 7
    fig_size[0] = 23
    fig_size[1] = 5
    plt.rcParams["figure.figsize"] = fig_size
     
    plt.bar(y_pos, performance, align='center', alpha=0.5)
    plt.xticks(y_pos, objects)
    plt.ylabel('Number of Associated Skills')
    plt.title('Number of Associated Skills for 50 Skill Groups')
    plt.savefig('fig_numofskills-50skillgp')
    return jsonify(plt)


@app_Isc.route('/prepNewRepSkillsVerbose/') # to assign one skill to only one skill group, from each mapping to SG, take highest weight:
def prepNewRepSkillsVerbose():
    sg_s_optm_df = pd.read_csv(DATA_DIR + '/edge_TopicSkillOneRepSkill_46_20171221-1021.csv', keep_default_na=False)
    skill_count_df = pd.read_csv(DATA_DIR + '/stat_skill_2016_count_new.csv', keep_default_na=False)
    skill_count_dict = dict(zip(skill_count_df.skill_name, skill_count_df.jobs_count))
    master_list = []
    for skill_group_id in skillgroup_id_list:
        cores_skill_group_filter = sg_s_optm_df['source'] == skill_group_id
        selected_sg_df = sg_s_optm_df[cores_skill_group_filter].copy()
        if selected_sg_df.shape[0] == 0:
            continue
        print skill_group_id
        for sg_row in range(selected_sg_df.shape[0]):
            master_list.append([selected_sg_df.iloc[sg_row].source, ch_label_dict[selected_sg_df.iloc[sg_row].target], selected_sg_df.iloc[sg_row].weight, skill_count_dict[ch_label_dict[selected_sg_df.iloc[sg_row].target].lower()]])

    onerep_sg_s_df = pd.DataFrame(master_list, columns=['skill_group', 'skill', 'weight', 'num_of_jobposts'])
    onerep_sg_s_df.sort_values(['skill_group', 'weight'], ascending=[True,False], inplace=True)
    fname2 = 'edge_TopicSkillOneRepSkill_'+ str(len(skillgroup_list)) +'_combined_'+  time.strftime("%Y%m%d-%H%M")+'.csv'
    onerep_sg_s_df.to_csv(DATA_DIR + '/'+ fname2, index=False)

    return jsonify(onerep_sg_s_df)


# to check for presence of a pair of skills occurence in job posting .csv file
@app_Isc.route('/checkWordPresenceCSVColv2/<path:str1>/<path:str2>') # to assign one skill to only one skill group, from each mapping to SG, take highest weight:
def checkWordPresenceCSVColv2(str1, str2):
    post_dict_df = pd.read_csv(DATA_DIR + '/dict_jobid2url_mapping.csv', keep_default_na=False)
    df = pd.read_csv(DATA_DIR + '/job_posting2016_with_skills_dict.csv', keep_default_na=False)
    # str1 = "cleaning"
    # str2 = "housekeeping"
    # df_new = df[df['occur_skills'].str.contains("numeracy")==True]
    df_new = df[(df['occur_skills'].str.contains(str1)) & (df['occur_skills'].str.contains(str2))]
    print "\n", df_new, "\n\n"
    # print "\n", row_found, "\n\n"
    job_id_list = df_new.job_id.tolist()[:int(10)]
    for j in job_id_list:
        query = post_dict_df['job_id'] ==  j
        row = post_dict_df[query]
        url_str = 'https://www.myskillsfuture.sg/content/portal/en/jobsbank/job-landing/job_directory/job-details.html?jobId=JOB-'+ row.iloc[0].post_id.split('&')[0]
        webbrowser.open(url_str)
    return jsonify(df_new[['job_id','job_title']])
    # return jsonify(df_new.shape[0])


# to check for presence of a skill occurence in job posting .csv file
# OPEN webpage
@app_Isc.route('/checkWordPresenceCSVColv3/<path:str1>')
@app_Isc.route('/checkWordPresenceCSVColv3/<path:str1>/<displaynum>') # to assign one skill to only one skill group, from each mapping to SG, take highest weight:
def checkWordPresenceCSVColv3(str1,displaynum=20):
    # import mapping_dict
    post_dict_df = pd.read_csv(DATA_DIR + '/dict_jobid2url_mapping.csv', keep_default_na=False)
    # import post_dict
    df = pd.read_csv(DATA_DIR + '/job_posting2016_with_skills_dict.csv', keep_default_na=False)
    df_new = df[df['occur_skills'].str.contains(str1+",")]
    print "\n", df_new[['job_id','job_title']], "\n\n"
    # print "\n", row_found, "\n\n"
    job_id_list = df_new.job_id.tolist()[:int(displaynum)]
    for j in job_id_list:
        query = post_dict_df['job_id'] ==  j
        row = post_dict_df[query]
        # wjob_id = 
        url_str = 'https://www.myskillsfuture.sg/content/portal/en/jobsbank/job-landing/job_directory/job-details.html?jobId=JOB-'+ row.iloc[0].post_id.split('&')[0]
        webbrowser.open(url_str)
    return jsonify(df_new[['job_id','job_title']])






