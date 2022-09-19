# import the required libraries
import pandas as pd
import json
import plotly
import plotly.express as px
from pickletools import optimize
from run_optimization import (read_effort_directory, parse_effort_sizing, resources_KPIs_stats,
                              run_optimization, post_model, future_utilization_metrics, 
                              gant_chart_and_hiring_status, path_to_datafolder)
from parse_ongoing_resources import parse_ongoing_resources_info
import utils



# List the upcomming projects.
pipeline_project_list=read_effort_directory(path_to_datafolder)

# extract the pipeline of the upcomming projects.
pipeline_tasks= parse_effort_sizing(path_to_datafolder,pipeline_project_list)

# Extract resources and their ongoing projects 
RESOURCES = parse_ongoing_resources_info(path_to_datafolder)

# Resourcses KPIs Statisitcs 
res_KPIs_stats = resources_KPIs_stats(RESOURCES)   ### ---- > Here must be show


# ==========================================================================================================
'''
                                                Flask application
'''
# ==========================================================================================================
from flask import Flask, render_template, request, url_for, redirect, request

app = Flask(__name__)


@app.route('/', methods = ["POST", "GET"])
def home():

    if request.method == "POST":
        sel_pipeline = request.form["selected_value"]
        return redirect(url_for("optimize", selected_pipeline = sel_pipeline))

    else:
        pipeline_tasks_list = list(pipeline_tasks.keys())
        for key, value in enumerate(pipeline_tasks_list):
            pipeline_tasks_list[key] = str(value)
        return render_template('home.html', pipeline=pipeline_tasks_list, res_KPIs_stats=res_KPIs_stats)



@app.route("/<selected_pipeline>")
def optimize(selected_pipeline):
        
    target_pipeline = list(eval(selected_pipeline))
    selected_pipeline_tasks = {key: pipeline_tasks[key] for key in pipeline_tasks.keys() if key in target_pipeline}
    model,ra_dict,pipeline_project_tasks = run_optimization(RESOURCES,selected_pipeline_tasks)
    RESOURCES_future= post_model(model,pipeline_project_tasks,RESOURCES, pipeline_tasks = selected_pipeline_tasks)
    future_utilization_metrics(RESOURCES_future)

    pd_2, hire_res_info = gant_chart_and_hiring_status(ra_dict,pipeline_tasks)
    
    fig = utils.plot_assignment_gantt_chart(pd_2)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('dashboard.html', graphJSON=graphJSON, hire_res_info = hire_res_info)

    

if __name__ == "__main__":
    app.run(host="127.0.0.1" ,port=8080 ,debug=True)




selected_pipeline_tasks = pipeline_tasks

