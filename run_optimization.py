# Import the libraries
from pyomo.environ import *
from pyomo.opt import SolverFactory

import warnings
warnings.filterwarnings('ignore')
import sys
import os
import copy


# import project's modules and depedencies
from parse_effort_sizing import parse_project_info_from_effort_sizing
from resources_KPIs import produce_res_kpis
from generic_resource_kpis import compute_utilization



# import utlis files
module_path = ""
# file=os.path.join(module_path,"utils.py")
sys.path.append(module_path)
import utils as utils

project_start_date_dict={"STC":"1 JAN 2023" , "TAKA":"15 MAR 2023"}
path_to_datafolder = "data"

def read_effort_directory(path=path_to_datafolder):    
    """Module that reads the directory and obtain list of pipeline projects"""
    effort_sizing_list=[file for file in os.listdir(path) if "effort_sizing" in file ]
    input_pipeline_list=[filename.split("_")[0] for filename in effort_sizing_list ]
    # print(effort_sizing_list)
    # print(input_pipeline_list)
    return input_pipeline_list

def parse_effort_sizing(path_to_datafolder,input_pipeline_list):
    list_pipeline=[]
    for project in input_pipeline_list:
        # project_name="STC"
        # project_start_date="1 JAN 2023"
        read_path=f"{path_to_datafolder}/{project}_effort_sizing.xlsx"
        project_start_date=project_start_date_dict[project]
        single_pipeline_tasks=parse_project_info_from_effort_sizing(project,project_start_date,read_path)
        list_pipeline.append(single_pipeline_tasks)

    pipeline_tasks = {}
    for d in list_pipeline:
        pipeline_tasks.update(d)
    return pipeline_tasks

def resources_KPIs_stats(RESOURCES):
    num_resources,bench_count,bench_list,resource_utilization_dict=produce_res_kpis(RESOURCES)
    overall_current_utilization=sum(resource_utilization_dict.values()) / len(resource_utilization_dict.keys())
    
    total_num_resources = f"You have {num_resources} Resources"
    res_on_bench = f"Currently there are {bench_count} on bench "
    res_bench_list = f"The people on bench are {bench_list}"
    overall_current_utilization = f"The overall utilization till year end is {overall_current_utilization}"
    res_KPIs_stats = [total_num_resources, res_on_bench, res_bench_list, overall_current_utilization]

    #print(f"You have {num_resources} Resources")
    #print(f"Currently there are {bench_count} on bench ")
    #print(f"The people on bench are {bench_list}")
    #print("The resources utilization are ",resource_utilization_dict)
    #print("The overall utilization till year end is ",overall_current_utilization)

    return res_KPIs_stats
    
def run_optimization(RESOURCES,pipeline_tasks):
    ongoing_tasks=utils.resource_tasks(RESOURCES)
    pipeline_tasks=utils.add_pipeline_type(pipeline_tasks)
    TASKS=utils.merge_ongoing_pipeline(pipeline_tasks,ongoing_tasks)

    all_tasks_overlap_tuples=utils.get_over_lap_tasks(TASKS)
    all_task_overlap=utils.task_overlap_combination(all_tasks_overlap_tuples)

    pipline_constraints,resource_constraints=utils.constraints_uf(all_task_overlap,TASKS)

    new_resource_constraint=utils.reformulate_resource_constraints(resource_constraints,TASKS)

    pipeline_project_tasks={}
    for p,t in pipeline_tasks.keys():
        list_1=pipeline_project_tasks.get(p,[])
        list_1.append(t)
        pipeline_project_tasks[p]=list_1
    # print(pipeline_project_tasks)
    # print("\n")

    pipeline_task_projects={}
    for p,t in pipeline_tasks.keys():
        list_1=pipeline_project_tasks.get(t,[])
        list_1.append(p)
        pipeline_task_projects[t]=list_1

    model = ConcreteModel()
    model.pipeline_tasks = Set(initialize = pipeline_tasks.keys(), dimen=2)
    model.pipeline_taskids_only=Set(initialize=list(map(lambda x : x[1],pipeline_tasks.keys())),dimen=1)
    model.pipeline_projects = Set(initialize = list(set([j for (j,m) in model.pipeline_tasks])))
    model.RESOURCES =  Set(initialize = RESOURCES.keys(), dimen=1)
    model.Resource_assignment=Set(initialize=model.pipeline_tasks * model.RESOURCES, dimen=3)

    model.prt_improper_var=Var(model.Resource_assignment,within=Binary, initialize=0)
    model.ra_var=Var(model.RESOURCES,within=Binary, initialize=0)
    # model.ta_var=Var(model.pipeline_taskids_only,within=Binary, initialize=0)

    #Binding Variables
    model.cons = ConstraintList()
    for resource in model.RESOURCES :
        model.cons.add(
        model.ra_var[resource] <=sum(model.prt_improper_var[p,t,resource] for p in model.pipeline_projects for t in pipeline_project_tasks[p]  )
    )

    # for task in model.pipeline_taskids_only:
    #     model.cons.add(
    #     sum(model.prt_improper_var[p,task,r] for p in pipeline_task_projects[task] for r in model.RESOURCES  ) ==
    #     model.ta_var[task] 
    #     )

    #Any given task should have one or zero assignment
    for t in model.pipeline_taskids_only:  
            model.cons.add(
                    1 >= sum(  model.prt_improper_var[p,t,r] 
                            for r in model.RESOURCES 
                            for p in pipeline_task_projects[t])
                )

    #The role required skillset must be in the resources skillset 
    for p in model.pipeline_projects:
        for t in pipeline_project_tasks[p]:
            for r in model.RESOURCES :                         
                if  pipeline_tasks[(p,t)]['skillset'] not in RESOURCES[r]['skillset']:
                    model.cons.add(
                            0== model.prt_improper_var[p,t,r]
                            )

    #For any overlap tasks the sum of utiliztion factor should be less than or equal 
    for r in model.RESOURCES:           

        # pipleine constraints (can apply to any resource of the specific skillset)       
        for pipline_constraint in pipline_constraints :        
            #if RESOURCES[r]['skillset']==TASKS[pipline_constraint[0]]['skillset'] :   
            # if TASKS[pipline_constraint[0]]['skillset'] in RESOURCES[r]['skillset']  :         
                
            
            model.cons.add(
                    RESOURCES[r]['slots'] >= sum( TASKS[proj_task].get('uf',1) * model.prt_improper_var[proj_task[0],proj_task[1],r] 
                        for proj_task in pipline_constraint )
            )
                
                
        # resource constraints (specific to this resource)  
            
        for resource_constraint in new_resource_constraint.get(r,[]) : 
            
            model.cons.add(        
                RESOURCES[r]['slots'] >= sum( TASKS[proj_task].get('uf',1) * model.prt_improper_var[proj_task[0],proj_task[1],r] 
                        for proj_task in resource_constraint['pipeline'])
                
                    + sum(TASKS[proj_task].get('uf',1) for proj_task in resource_constraint['ongoing'])
                        )
    # expr=sum(model.ra_var[r] for r in model.RESOURCES) + sum(model.ta_var[t] for t in model.pipeline_taskids_only)
    expr=          sum(model.prt_improper_var[p,t,r] for p in model.pipeline_projects
        for t in pipeline_project_tasks[p]
            for r in model.RESOURCES) + sum(model.ra_var[r] for r in model.RESOURCES)
    model.objective=Objective(expr=expr,sense=maximize)

    os.environ['NEOS_EMAIL'] = 'amr.mansour@devoteam.com'
    opt = SolverFactory('cbc')  # Select solver
    solver_manager = SolverManagerFactory('neos')  # Solve in neos server
    results = solver_manager.solve(model, opt=opt)

    def get_resource_assignment():
        resource_table = {
            p: {t: [] for t in pipeline_project_tasks[p]} 
            for p in model.pipeline_projects}
        
        
        for p in model.pipeline_projects:
            for t in pipeline_project_tasks[p]:
                for r in model.RESOURCES :
                        if model.prt_improper_var[p, t, r].value == 1:
                            resource_table[p][t].append(r)
        return resource_table

    ra_dict=get_resource_assignment()

    return model,ra_dict,pipeline_project_tasks,pipeline_tasks


def post_model(model,pipeline_project_tasks,RESOURCES, pipeline_tasks):    

    RESOURCES_future=copy.deepcopy(RESOURCES)

    i=0
    for resource in RESOURCES_future.keys():
    # RESOURCES_future[resource]['num_ongoing_and_future_projects']=RESOURCES_future[resource]['num_ongoing_projects']
    # RESOURCES_future[resource]['current_and_future_load']=RESOURCES_future[resource]['current_load']

        for p in model.pipeline_projects:
                for t in pipeline_project_tasks[p]:
                    if model.prt_improper_var[p, t, resource].value == 1:
                        i=i+1
                        start_date=pipeline_tasks[(p,t)]['start_date']
                        end_date=pipeline_tasks[(p,t)]['end_date']
                        RESOURCES_future[resource]['num_ongoing_projects']=RESOURCES_future[resource]['num_ongoing_projects']+1
                        RESOURCES_future[resource]['current_load'][f'fut_{i}']={
                                'project': (p,t), 'start_date': start_date, 'end_date':end_date,'uf':1}                    
    return RESOURCES_future

def future_utilization_metrics(RESOURCES_future,start_period="1 JAN 2023",end_period="31 DEC 2023"):
    dict_assignment_resource_util=compute_utilization(start_period,end_period,RESOURCES_future)
    print(dict_assignment_resource_util)

    overall_future_utilization=sum(dict_assignment_resource_util.values()) / len(dict_assignment_resource_util.keys())
    print("The forseen utilization is ",overall_future_utilization)

def gant_chart_and_hiring_status(ra_dict,pipeline_tasks):
    def assignment_fullfilment(project,task):
        dict_1=ra_dict[project]
        try :
            assignment=dict_1[task][0]
        except: 
            assignment="To be Hired"
        return assignment

    pd_2=utils.convert_to_pd(pipeline_tasks)
    pd_2['assignment_status']=pd_2[["Project","Task"]].apply(lambda x:assignment_fullfilment(*x),axis=1)
    hire_res_info = " and ".join (pd_2[pd_2['assignment_status']=="To be Hired"]['Role'].unique())
    return pd_2, hire_res_info

    #print("You need to hire the following : ")
    #print(" and ".join (pd_2[pd_2['assignment_status']=="To be Hired"]['Role'].unique()))
