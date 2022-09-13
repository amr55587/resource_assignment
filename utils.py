import os
from pyomo.environ import *
from pyomo.opt import SolverFactory
import pandas as pd 

import warnings
warnings.filterwarnings('ignore')
from datetime import datetime
import networkx as nx 
import plotly.express as px
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots


'''
pipeline_tasks= {
    ('Project1','Task1_1') : 
        {'start_date':'1 JAN 2022','end_date':'31 JAN 2022',
         'skillset':'AI_architect','uf':0.5} ,
    
    ('Project1','Task2_1') : 
        {'start_date':'1 FEB 2022','end_date':'28 FEB 2022',
         'skillset':'BI','uf':1},
    
    ('Project2','Task1_2') : 
        {'start_date':'1 MAR 2022','end_date':'30 MAR 2022',
         'skillset':'DS','uf':0.5} ,  # --- > For Kareem
    
    ('Project2','Task2_2') : 
        {'start_date':'1 MAR 2022','end_date':'31 MAR 2022',
         'skillset':'DS','uf':1} ,
    
    ('Project2','Task3_2') : 
        {'start_date':'1 MAR 2022','end_date':'30 MAR 2022',
         'skillset':'DS','uf':0.5} ,
    ('Project3','Task1_3') : 
        {'start_date':'5 MAR 2023','end_date':'7 MAR 2023',
         'skillset':'BI','uf':1}  ,
    
     ('Project3','Task2_3') : 
        {'start_date':'1 JAN 2022','end_date':'5 JAN 2022',
         'skillset':'DS','uf':0.5} , # --- > For Kareem

}
'''

def convert_to_pd(TASKS):
    """Convert to Pandas to plot a gant chart"""
    list_tasks=[]
    list_start=[]
    list_end=[]
    list_skillset=[]
    list_type=[]
    list_projects=[]
    for (p,t) in TASKS.keys():
        list_projects.append(p)
        list_tasks.append(t)
        list_start.append(str_to_date(TASKS[(p,t)]['start_date']))
        list_end.append(str_to_date(TASKS[(p,t)]['end_date']))
        list_skillset.append(TASKS[(p,t)]['skillset'])
        list_type.append(TASKS[(p,t)].get('type',None)) 
    return pd.DataFrame({"Project":list_projects,"Task":list_tasks , "Start":list_start,"End":list_end,"Role":list_skillset,"Type":list_type})


def plot_gantt_chart(df_tasks):
    fig = px.timeline(df_tasks, x_start="Start", x_end="End", y="Task",color="Role")
    fig.update_yaxes(autorange="reversed") # otherwise tasks are listed from the bottom up
    fig.show()

def plot_assignment_gantt_chart(df_tasks):
    num_projects=len(df_tasks['Project'].unique())
    fig = make_subplots(rows=num_projects, cols=2)


    for project in df_tasks['Project'].unique():
        df_plot=df_tasks[df_tasks['Project']==project]
        fig = px.timeline(df_plot, x_start="Start", x_end="End", y="Task",color="assignment_status")
        fig.update_yaxes(autorange="reversed") # otherwise tasks are listed from the bottom up
    fig.show()



def add_pipeline_type(pipeline_tasks):
    for pipeline_task in pipeline_tasks.keys():
        pipeline_tasks[pipeline_task]['type']='pipeline'
    return pipeline_tasks



def resource_tasks(RESOURCES):
    i=0
    ongoing_tasks={}
    for resource in RESOURCES.keys():
        # print(resource)
        skillset=RESOURCES[resource]['skillset']
        for ongoing_proj in RESOURCES[resource]['current_load'].keys(): 
            
            dict_details=RESOURCES[resource]['current_load'][ongoing_proj]
    #         print(RESOURCES[resource]['current_load'][ongoing_proj])
            task_id=f"{dict_details['project']}_{i}"
            ongoing_tasks[(dict_details['project'],task_id)]={
                'start_date':dict_details['start_date'],'end_date':dict_details['end_date'],
            'skillset':skillset,'uf':dict_details['uf'],'type':'ongoing','resource_name':resource
            }       
            i=i+1
    return ongoing_tasks

def merge_ongoing_pipeline(pipeline_tasks,ongoing_tasks):
    res = {**pipeline_tasks, **ongoing_tasks}
    return res

def str_to_date(date_string):
    return datetime.strptime(date_string, '%d %b %Y')       

def retrieve_task_dict_by_id(task_id,TASKS):
    """Given a taskid in the form of (project_name,task_id) 
    returns the dictionary 
        ---- > task_start_date,task_end_date,role_required and utilizaition required
     e.g. {'start_date':'1 JAN 2022','end_date':'5 JAN 2022','skillset':'DS','uf':0.5}
    
    """
    return TASKS[task_id]


def two_task_skill_overlap(t1_id,t2_id,TASKS):
    if TASKS[t1_id]['skillset']==TASKS[t2_id]['skillset']:
        return 1
    else :
        return 0

def time_overlap(t1_start,t1_end,t2_start,t2_end):
    """Given two tasks start and end  , decide if they have overlap(y=1) or no (y=0)
    """
    if (t1_start >=t2_end) or (t1_end <=t2_start):
        # print("No intersection")
        return 0
    
    else:
        # print("overlap")
        return 1

def two_task_time_overlap(t1_id,t2_id,TASKS):
    t1_dict=retrieve_task_dict_by_id(t1_id,TASKS)
    t2_dict=retrieve_task_dict_by_id(t2_id,TASKS)

    t1_start,t1_end=str_to_date(t1_dict['start_date']),str_to_date(t1_dict['end_date'])
    t2_start,t2_end=str_to_date(t2_dict['start_date']),str_to_date(t2_dict['end_date'])

    return time_overlap(t1_start,t1_end,t2_start,t2_end)


# t1_id=('Project1','Task1_1')
# t2_id=('Project1','Task2_1')
# t3_id=('Project2','Task1_2')
# t4_id=('Project2','Task2_2')
# t5_id=('Project2','Task3_2')
# t6_id=('Project3','Task1_3')
# t7_id=('Project3','Task2_3')

# print(two_task_time_overlap(t1_id,t2_id))
# print("\n")


# list_tasks=[t1_id,t2_id,t3_id,t4_id,t5_id,t6_id,t7_id]

def get_over_lap_tasks(TASKS):
    task_keys_list=list(TASKS.keys())
    list_overlap=[]
    for i in range(len(task_keys_list)-1):
        for j in range(i+1,len(task_keys_list)):
            skill_overlap=two_task_skill_overlap(task_keys_list[i],task_keys_list[j],TASKS)
            # print(skill_overlap)
            time_overlap=two_task_time_overlap(task_keys_list[i],task_keys_list[j],TASKS)
            # print(time_overlap)
            # if skill_overlap==1 and time_overlap==1:
            if time_overlap==1:
                list_overlap.append( (task_keys_list[i],task_keys_list[j]))
    return list_overlap



def task_overlap_combination(task_tuples):
    G=nx.Graph(task_tuples).to_undirected()
    return [x for x in list(nx.enumerate_all_cliques(G)) if len(x) > 1]

def constraints_uf(all_task_overlap,TASKS):
    resource_constraints={}
    pipline_constraints=[]
    for overlap_list in all_task_overlap:
        resource_counter=0
        resource_count={}
        for overlap_task in overlap_list:
            # print(overlap_task)
            if TASKS[overlap_task]['type']=='ongoing':
                resource=TASKS[overlap_task]['resource_name']
    #             print(resource)
                resource_count[resource]=resource_count.get(resource,0) +1 
                resource_counter=resource_counter+1
    #             print(resource_count)
        # print(overlap_list)
        # print(resource_count)        
        if resource_counter ==0 :
            pipline_constraints.append(overlap_list)
        elif len(resource_count.keys()) ==1 and resource_counter<len(overlap_list):
            resource=list(resource_count.keys())[0]
            # print(resource_constraints.get(resource,[]))
            if resource_constraints.get(resource,0)==0:
                resource_constraints[resource]=[overlap_list]
            else :
                resource_constraints[resource].append(overlap_list)
    return pipline_constraints,resource_constraints

def reformulate_resource_constraints(resource_constraints,TASKS):
    new_resource_constraint={}
    new_constraint_list=[]
    for resource in resource_constraints.keys():
        constraint_list=resource_constraints[resource]
        new_constraint_list=[]
        for constraint in constraint_list:            
            dict_a={"ongoing":list(),"pipeline":list()}
            # print("Constraint is ",constraint)
            for some_task in constraint:
                # print(some_task)
                if TASKS[some_task]['type']=="ongoing":
                    # print("ong")
                    dict_a['ongoing'].append(some_task)
                elif TASKS[some_task]['type']=="pipeline":
                    # print("pip")
                    dict_a['pipeline'].append(some_task)
            new_constraint_list.append(dict_a)
        new_resource_constraint[resource]=new_constraint_list
    return new_resource_constraint



# task_overlap_tuples=get_over_lap_tasks(list_tasks)
# print(task_overlap_tuples)


# print("\n")

# task_overlap_combinations=task_overlap_combination(task_overlap_tuples)
# for x in task_overlap_combinations:
#     print(x)
#     print("\n")



