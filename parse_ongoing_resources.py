import pandas as pd 
from datetime import datetime

ongoing_projects_path="data"

def main(ongoing_projects_path):
    path_ongoing=ongoing_projects_path + "/ongoing_projects.xlsx"
    path_resources=ongoing_projects_path + "/Resources_sheet.xlsx"

    df_resources_ongoing=pd.read_excel(path_ongoing,header=0)
    df_resources_sheet=pd.read_excel(path_resources,header=0)


    def map_seniortiy_slots(seniority):
        if seniority[0]=="P":
            return 3
        elif seniority[0]=="L":
            return 3
        elif seniority[0]=="S":
            return 2
        else :
            return 1

    dict_resources={}
    for i in range(len(df_resources_sheet)):
        resource_name=df_resources_sheet['Resource Name'][i]
        skillset=list(df_resources_sheet['Skill Set'][i].split(','))
        # if len(skillset)==1:
        #     skillset=skillset[0]
        seniority=df_resources_sheet['Seniority'][i]
        hire_date=df_resources_ongoing['Hire date'][i]
        # datetime.strptime(date_string, '%d %b %Y') 

        slots=map_seniortiy_slots(seniority)
        dict_resources[resource_name]={'skillset':skillset,'seniority':seniority,'slots':slots,'hire_date':hire_date}

    for i in range(len(df_resources_ongoing)):
        resource_name=df_resources_ongoing['Resource Name'][i]
        # ongoing_proj=df_resources_ongoing['Resource Name'][i]
        start,end=df_resources_ongoing['Start Assignment'][i],df_resources_ongoing['End Assignment'][i]
        project_name=df_resources_ongoing['Ongoing Project'][i]
        proj_index=dict_resources[resource_name].get('num_ongoing_projects',0) +1
        dict_resources[resource_name]['num_ongoing_projects']=proj_index
        dict_resources[resource_name]['current_load']=dict_resources[resource_name].get('current_load',{})
        dict_resources[resource_name]['current_load'][f'ong_{i}']= {
            'project': project_name , 'start_date': start.strftime('%d %b %Y'), 'end_date':end.strftime('%d %b %Y'),'uf':1}

    for i in range(len(df_resources_sheet)):
        resource_name=df_resources_sheet['Resource Name'][i]
        if dict_resources[resource_name].get('num_ongoing_projects') is None:
            dict_resources[resource_name]['num_ongoing_projects']=0
            dict_resources[resource_name]['current_load']=dict_resources[resource_name].get('current_load',{})
            dict_resources[resource_name]['current_load'][f'ong_{i}']= {
            'project': 'idle' , 'start_date': "01 JAN 1900", 'end_date':"02 JAN 1900",'uf':0}


    return dict_resources
if __name__ == "__main__":
    dict_ongoing_resources=main(ongoing_projects_path)
    print("The final output is",dict_ongoing_resources)

        
