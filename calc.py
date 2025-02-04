import functools
from . import neucbot
import matplotlib.pyplot as plt
import io
import base64

from flask import ( # type: ignore
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from UI.db import get_db # type: ignore

bp = Blueprint('calc', __name__, url_prefix='/')

@bp.route('/', methods=('GET', 'POST'))
def calc():
    if request.method == 'POST':
        alphas = request.form.get('alpha_chain')
        mat = request.form.get('material')
        slow_calc = request.form.get('a_energy_calculation')

        if not alphas:
            flash('Input text is required')
            return redirect(url_for('calc.calc'))
        
        #Process the alphas
        alpha_list = neucbot.loadChainAlphaList(alphas)
        #alpha_list = neucbot.loadAlphaList(alphas)
        mat_comp = neucbot.readTargetMaterial(mat)

        if(slow_calc == "True"):
            xsects, nspec, pspec, aspec, max_alpha, a_n_list = neucbot.run_alpha_energy_loss(alpha_list, mat_comp, .01)
            fig, ax = plt.subplots()
            ax.plot(sorted(pspec.keys()),[pspec[k] for k in sorted(pspec.keys())],marker="o", linestyle="-", color="b")
            ax.set_title("Neutron Emission Probability Spectrum")
            ax.set_xlabel("Neutron Energy")
            ax.set_ylabel("Probabilities")

            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            ngraph = base64.b64encode(buf.getvalue()).decode()

            graph_list = {}
            tuf = {}
            for e in a_n_list:

                fig, nx = plt.subplots()
                nx.plot(sorted(a_n_list[e].keys()),[a_n_list[e][k] for k in sorted(a_n_list[e].keys())],marker="o", linestyle="-", color="b")
                title = "(a,n) Probabilities for " + str(e) + " En"
                nx.set_title(title)
                nx.set_xlabel("deltaEa")
                nx.set_ylabel("Probabilities")

                tuf[e] = io.BytesIO()
                plt.savefig(tuf[e], format="png")
                tuf[e].seek(0)
                #a_n_graph = base64.b64encode(tuf[e].getvalue()).decode()
                graph_list[e] = base64.b64encode(tuf[e].getvalue()).decode()

            return render_template('calc/calc.html', xsect = xsects,nspec = nspec, probspec = pspec, aspec = aspec, max_alpha = max_alpha, ngraph=ngraph, graph_list = graph_list)

        else:
            xsects, nspec = neucbot.run_alpha(alpha_list, mat_comp, .01)
            return render_template('calc/calc.html', xsect = xsects,nspec = nspec)
            
        print(f"User input: {alpha_list}")
        
    else:
        return render_template('calc/calc.html')
