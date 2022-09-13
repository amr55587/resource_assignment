"""
This module reads one effort sizing sheet and parses it to extract the roles needed and their durations 
Output in the form of 

{('STC', 'P1_RHU_BDM'): {'start_date': Timestamp('2022-01-01 00:00:00'), 
                        'end_date': Timestamp('2022-02-11 00:00:00'), 'skillset': 'BDM'}, 
('STC', 'SC2_RHU_DRM'): {'start_date': Timestamp('2022-01-01 00:00:00'), 
                        'end_date': Timestamp('2022-02-11 00:00:00'), 'skillset': 'DRM'}, 
('STC', 'L1_RHU_AI Lead'): {'start_date': Timestamp('2022-01-07 00:00:00'), 
                        'end_date': Timestamp('2022-01-19 00:00:00'), 'skillset': 'AI Lead'}

"""


import pandas as pd
import numpy as np

import utils as utils
import datetime

project_name="STC"
project_start_date="1 JAN 2022"
path="data/STC_effort_sizing.xlsx"


def main(project_name,project_start_date,path):

    def parse_the_required_roles(path):
        df_roles=pd.read_excel(path,skiprows=lambda x : x > 4 ,header=None)
        df_roles=df_roles.transpose()
        df_roles.dropna(axis=0,how='all',inplace=True)
        df_roles.dropna(axis=1,how='all',inplace=True)


        df_roles.columns=['Seniority Level','origin','Role','resource_name']
        df_roles['sen_origin_role']=df_roles['Seniority Level'] + '_' + df_roles['origin'] + '_' +df_roles['Role']
        df_roles=df_roles[2:].dropna(subset='sen_origin_role')
        role_names=list(df_roles['sen_origin_role'].values)
        return df_roles,role_names

    def retreive_resource_pipeline(path,df_roles,role_names):
        df_tasks=pd.read_excel(path,skiprows=7,header=None)
        df_tasks.dropna(axis=0,how='all',inplace=True)
        df_tasks.dropna(axis=1,how='all',inplace=True)

        df_tasks=df_tasks.loc[:,:len(df_roles)+2]
        df_tasks.columns=['Phase_id','Phase_or_task_name','phase_or_task_duration'] + role_names
        end_index=df_tasks[df_tasks['Phase_or_task_name']=="TOTALS"].index[0]
        df_tasks=df_tasks[:end_index-1]
        df_tasks['slot_type']=df_tasks['Phase_or_task_name'].map(type)
        df_tasks_only=df_tasks[df_tasks['slot_type']==str]
        max_phase_id=df_tasks_only['Phase_id'].max()
        df_tasks_only=df_tasks_only.fillna(0)
        phase_name_id=dict(df_tasks_only[df_tasks_only['Phase_id']!=0.0][['Phase_id','Phase_or_task_name']].values)
        current_phase_id=1
        current_phase_name=phase_name_id[current_phase_id]
        list_phase_id=[]
        list_phase_name=[]
        for i in range(len(df_tasks_only)):
            if df_tasks_only['Phase_id'][i] <= current_phase_id:
                list_phase_id.append(current_phase_id)
                list_phase_name.append(current_phase_name)
            else :
                current_phase_id=current_phase_id+1
                current_phase_name=phase_name_id[current_phase_id]
                list_phase_id.append(current_phase_id)
                list_phase_name.append(current_phase_name)
        df_tasks_only['correct_phase_id']=list_phase_id
        df_tasks_only['correct_phase_name']=list_phase_name
        def is_assignment(x):
            if x ==0.0:
                return "task"
            else :
                return "Phase"
        df_tasks_only['task_nature']=df_tasks_only['Phase_id'].map(is_assignment)
        df_tasks_only['critical_path']=df_tasks_only[role_names].max(axis=1)
        df_phase_agg=df_tasks_only[df_tasks_only['task_nature']=="task"].groupby(['correct_phase_id','correct_phase_name']).agg(
        sum_activites=('critical_path',sum),max_activies=('critical_path',max)).reset_index()
        df_phase_agg['Phase_dependancy']=['S','P','P','S']
        def phase_duration(sum,max,dependancy):
            if dependancy=="S":
                return sum
            elif dependancy=="P":
                return max 
        df_phase_agg['duration']=df_phase_agg[["sum_activites","max_activies","Phase_dependancy"]].apply(lambda x:phase_duration(*x),axis=1)


        list_start_date=[]
        list_end_date=[]
        for i in range(len(df_phase_agg)):
            duration=datetime.timedelta(days=df_phase_agg['duration'][i])
            if i==0:
                list_start_date.append(utils.str_to_date(project_start_date))
            else :
                list_start_date.append(list_end_date[i-1])

            list_end_date.append(list_start_date[i] + duration)
        df_phase_agg['phase_start_date']=list_start_date
        df_phase_agg['phase_end_date']=list_end_date

        # print(df_phase_agg)


        dict_phase_start_end={}
        for i in range(len(df_phase_agg)):
            dict_phase_start_end[df_phase_agg['correct_phase_id'][i]]={'start_date':df_phase_agg['phase_start_date'][i] ,
            'end_date':df_phase_agg['phase_end_date'][i]}
        
        # print(dict_phase_start_end)


        df_1=df_tasks_only[df_tasks_only['task_nature']=="Phase"][["Phase_id"]+role_names ].set_index("Phase_id").applymap(lambda x :x>0)
        # print(df_1)
        # print("\n")
        dict_pipline_assignemnt={}
        def some_func(df_1):
            for role in role_names:
                list_x=list(df_1[role].where(lambda x :x==True).dropna().index)
                start_date=dict_phase_start_end[min(list_x)]['start_date']
                end_date=dict_phase_start_end[max(list_x)]['end_date']
                dict_pipline_assignemnt[(project_name,f'{project_name}_{role}')]={'start_date':start_date.strftime('%d %b %Y'),'end_date':end_date.strftime('%d %b %Y'),'skillset':role.split('_')[2]}
            return dict_pipline_assignemnt
        dict_pipline_assignemnt=some_func(df_1)
        # print(dict_pipline_assignemnt)
        return dict_pipline_assignemnt
    df_roles,role_names=parse_the_required_roles(path)
    # print(role_names)
    return retreive_resource_pipeline(path,df_roles,role_names)
if __name__ == "__main__":
    dict_x=main(project_name,project_start_date,path)
    # print("The final output is",dict_x)



