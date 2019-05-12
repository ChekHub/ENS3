from flask import Flask, render_template, request, Response, jsonify
import os
import io
import matplotlib as pltb
import json
import zlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

font = { 'family':'Times New Roman', 'weight':'bold','size': 20}
pltb.rc('font',**font)


## server code

app = Flask(__name__)

poll_data = {
   'question' : 'Selecciona tu respuesta:',
   'fields'   : ['A', 'B', 'C', 'D'],
   'fname'    : 'data//poll_initial.csv'
}

@app.route('/')
def root():
    return render_template('buttontest_radio.html', data=poll_data)

@app.route('/poll')
def poll():
    vote = request.args.get('field')
    filename = poll_data['fname']
    out = open(filename, 'a')
    out.write( vote + '\n' )
    out.close()

    return render_template('thankyou.html')


@app.route('/questions',methods=['POST'])
def loadquest():
    data = request.json
    fs = np.array(data['questions'])
    fs = [str(d0) for d0 in fs]
    f0 = data['filename']
    f0 = str(f0)
    poll_data['fields'] = fs
    poll_data['fname'] =  f0

    return jsonify(message = "Successfully loaded questions")

@app.route('/iplot',methods=['POST'])
def sendiplot():
    votes = {}
    percent = {}

    for f in poll_data['fields']:
        votes[f] = 0
        percent[f] = 0


    filename = poll_data['fname']
    f  = open(filename, 'r')
    for line in f:
        vote = line.rstrip("\n")
        votes[vote] += 1
    f.close()

    return jsonify(values= votes.values(), fname = poll_data['fname'], fields = votes.keys() )



@app.route('/plot.png')
def plot_png():
    votes = {}
    filename = poll_data['fname']

    for f in poll_data['fields']:
        votes[f] = 0

    f  = open(filename, 'r')
    for line in f:
        vote = line.rstrip("\n")
        votes[vote] += 1
    f.close()

    fig = create_figure(votes)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure(votes):
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    bar_width = 0.35
    opacity = 0.75

    x0 = [str(r1) for r1 in votes.keys()]
    y0 = votes.values()
    data0 = np.array([x0,y0]).T
    data0 = data0[data0[:,0].argsort()]


    xs = np.arange(len(data0[:,0]))
    ys = 100*np.array(data0[:,1].astype(float))/np.sum(data0[:,1].astype(float))

    #fig.patch.set_visible(False)
    #axis.xaxis.label.set_color('white')
    #axis.yaxis.label.set_color('white')
    #axis.spines['top'].set_color('white')
    #axis.spines['bottom'].set_color('white')
    #axis.spines['left'].set_color('white')
    #axis.spines['right'].set_color('white')

    #axis.tick_params(axis='x',colors = 'white')
    #axis.tick_params(axis='y',colors = 'white')

    axis.bar(xs, ys, bar_width, alpha=opacity, color='#0DFF92',label='resultados')
    axis.set_xlabel('Seleccion')
    axis.set_ylabel('Votos[%]')
    axis.set_title('Resultados, Total de votos :' + str(np.sum(y0)))
    axis.yaxis.grid(True, linestyle='--', which='major', color='black', alpha=.55)
    axis.set_xticks(xs + 0.5*bar_width)
    axis.set_axis_bgcolor('white')
    axis.set_xticklabels(data0[:,0])
    axis.legend()

    return fig

@app.route('/results')
def show_results():
    votes = {}
    percent = {}

    for f in poll_data['fields']:
        votes[f] = 0
        percent[f] = 0


    filename = poll_data['fname']
    f  = open(filename, 'r')
    for line in f:
        vote = line.rstrip("\n")
        votes[vote] += 1
    f.close()

    votestotal = sum(votes.values())

    for f0 in poll_data['fields']:
        percent[f0] = np.round(100.0*votes[f0]/votestotal,1)

    poll_data['totalVotes'] = votestotal
    poll_data['answers'] = votes
    poll_data['percent'] = percent

    with open(poll_data['fname'].replace('.csv','_results.txt'),'w') as outfile2:
        json.dump(poll_data,outfile2)

    return render_template('results.html', data=poll_data, votes=votes, Ntotal=votestotal, percent = percent)

if __name__ == "__main__":
    app.run(debug=True, host = '0.0.0.0', threaded = True)
