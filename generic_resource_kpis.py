#import parse_ongoing_resources as parse_res
from datetime import datetime
# from datetime import Range

import utils
from collections import namedtuple


def compute_utilization(start_period,end_period,dict_resources):
    # def number_of_days_bet_2_dates(date1,date2):
    #     if type(date1) is str:
    #         date1=utils.str_to_date(date1)
    #     if type(date2) is str:
    #         date2=utils.str_to_date(date2)
    #     return (date2-date1).days 

    def compute_intersection(t1_start,t1_end,t2_start,t2_end):
        """Given two tasks start and end  , decide if they have overlap(y=1) or no (y=0)
        then compute overlap days
        """
        if (t1_start >=t2_end) or (t1_end <=t2_start):
            # print("No intersection")
            return 0
        
        else:
            Range = namedtuple('Range', ['start', 'end'])
            r1 = Range(start=t1_start, end=t1_end)
            r2 = Range(start=t2_start, end=t2_end)
            latest_start = max(r1.start, r2.start)
            earliest_end = min(r1.end, r2.end)
            delta = (earliest_end - latest_start).days + 1
            overlap = max(0, delta)
            return overlap    


            # if t2_end>=t1_end: # task 2 is more recent
            #     if 
            #     over_lap_days=(t1_end- t2_start).days
            # else :
            #     over_lap_days=(t2_end- t1_start).days

            # # print("overlap")
            # return over_lap_days



    if start_period is None :
        start_period=datetime.today()

    if type(start_period) is str:
            start_period=utils.str_to_date(start_period)
    if type(end_period) is str:
        end_period=utils.str_to_date(end_period)

    # def compute_utilization(resource):

    #     def compute_intersection(project):
    #         project_start_date=1
    #         project_end_date=1

    #         utils.time_overlap
    resource_utilization_dict={}
    for resource in dict_resources.keys():
        all_projects_dictionary=dict_resources[resource]['current_load']
        list_proj_utiliztion=[]
        for project_id in all_projects_dictionary.keys():
            project_dictionary=all_projects_dictionary[project_id]
            project_name=project_dictionary['project']
            if project_name=='idle':
                project_utilization=0
            else :
                start_proj_date=utils.str_to_date(project_dictionary['start_date'])
                end_proj_date=utils.str_to_date(project_dictionary['end_date'])
                overlap_days=compute_intersection(start_proj_date,end_proj_date,start_period,end_period)
                project_utilization= (100 * overlap_days) / ((end_period-start_period).days)
            list_proj_utiliztion.append(project_utilization)
        max_utilization=int(max(list_proj_utiliztion))
        resource_utilization_dict[resource]=max_utilization
    return resource_utilization_dict



#     num_resources=len(dict_resources.keys())
#     def compute_bench():
#         bench_count=0
#         bench_list=[]
#         for resource in dict_resources.keys():
#             if dict_resources[resource].get('num_ongoing_projects') ==0:
#                 bench_count=  bench_count + 1 
#                 bench_list.append(resource)



#     def number_of_days_from_today_till_year_end():
#         date_diff=datetime(datetime.today().year, 12, 31) - datetime.today()
#         return date_diff.days

#     def number_of_days_from_start_till_year_end():
#         date_diff=datetime(start_period.year, 12, 31) - start_period
#         return date_diff.days

#     year_end=datetime(datetime.today().year, 12, 31)

#     def number_of_days_bet_2_dates(date1,date2):
#         if type(date1) is str:
#             date1=utils.str_to_date(date1)
#         if type(date2) is str:
#             date2=utils.str_to_date(date2)
#         return (date2-date1).days 

#     #Computes utiliztion of a given project considering the year end
#     def proj_utiliztion(project_start,project_end):        
#         delta_project_year_end=number_of_days_bet_2_dates(project_end,year_end)
#         delta_today_project=number_of_days_bet_2_dates(datetime.today(),project_end)
#         # print(delta)

#         if delta_project_year_end <=0:
#             utilization=100 
#         else :
#             utilization=100 * delta_today_project / number_of_days_till_year_end()
#         return utilization 

#     active_resources=[ resource for resource in list(dict_resources.keys()) if resource not in bench_list]
#     resource_utilization_dict={}
#     for resource in active_resources:
#         projects_dictionary=dict_resources[resource]['current_load']
#         list_proj_utiliztion=[]
#         for ongoing_proj in projects_dictionary.keys():
#             project_dict=projects_dictionary[ongoing_proj]
#             project_utiliztion=proj_utiliztion(project_dict['start_date'],project_dict['end_date'])
#             list_proj_utiliztion.append(project_utiliztion)
#         max_utilization=int(max(list_proj_utiliztion))
#         resource_utilization_dict[resource]=max_utilization
    
#     return num_resources,bench_count,bench_list,resource_utilization_dict


# if __name__ == "__main__":
#     dict_resources=parse_res.main("data")
#     num_resources,bench_count,bench_list,resource_utilization_dict=main(dict_resources)


    # print(f"You have {num_resources} Resources")
    # print(f"Currently there are {bench_count} on bench ")
    # print(f"The people on bench are {bench_list}")
    # print("The resources utilization are ",resource_utilization_dict)