import parse_ongoing_resources as parse_res
from datetime import datetime

import utils

def main(dict_resources):

    num_resources=len(dict_resources.keys())

    bench_count=0
    bench_list=[]
    for resource in dict_resources.keys():
        if dict_resources[resource].get('num_ongoing_projects') ==0:
            bench_count=  bench_count + 1 
            bench_list.append(resource)



    def number_of_days_till_year_end():
        date_diff=datetime(datetime.today().year, 12, 31) - datetime.today()
        return date_diff.days

    year_end=datetime(datetime.today().year, 12, 31)

    def number_of_days_bet_2_dates(date1,date2):
        if type(date1) is str:
            date1=utils.str_to_date(date1)
        if type(date2) is str:
            date2=utils.str_to_date(date2)
        return (date2-date1).days 

    #Computes utiliztion of a given project considering the year end
    def proj_utiliztion(project_start,project_end):        
        delta_project_year_end=number_of_days_bet_2_dates(project_end,year_end)
        delta_today_project=number_of_days_bet_2_dates(datetime.today(),project_end)
        # print(delta)

        if delta_project_year_end <=0:
            utilization=100 
        else :
            utilization=100 * delta_today_project / number_of_days_till_year_end()
        return utilization 

    active_resources=[ resource for resource in list(dict_resources.keys()) if resource not in bench_list]
    resource_utilization_dict={}
    for resource in active_resources:
        projects_dictionary=dict_resources[resource]['current_load']
        list_proj_utiliztion=[]
        for ongoing_proj in projects_dictionary.keys():
            project_dict=projects_dictionary[ongoing_proj]
            project_utiliztion=proj_utiliztion(project_dict['start_date'],project_dict['end_date'])
            list_proj_utiliztion.append(project_utiliztion)
        max_utilization=int(max(list_proj_utiliztion))
        resource_utilization_dict[resource]=max_utilization
    
    return num_resources,bench_count,bench_list,resource_utilization_dict


if __name__ == "__main__":
    dict_resources=parse_res.main("data")
    num_resources,bench_count,bench_list,resource_utilization_dict=main(dict_resources)


    # print(f"You have {num_resources} Resources")
    # print(f"Currently there are {bench_count} on bench ")
    # print(f"The people on bench are {bench_list}")
    # print("The resources utilization are ",resource_utilization_dict)