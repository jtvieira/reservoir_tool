from django.shortcuts import render
from django.http import JsonResponse
from .utils import realTimeInfo
from .utils.modelInfo import return_plots
# Create your views here.

def home(request):
    return render(request, "index.html")

def get_info(request):
    if request.method == 'GET':
        res = request.GET['res']
        rti_plot = realTimeInfo.return_plot(res)
        ml_plots = return_plots(res)
        algs = ['svr', 'kneighbors', 'neural_net', 'decision_tree', 'random_forest', 'gaussian']
        plot_dict = {'rti_plot': rti_plot}
        for i in range(len(ml_plots)):
            plot_dict[algs[i]] = ml_plots[i]

        return JsonResponse(plot_dict)