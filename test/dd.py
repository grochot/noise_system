import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import sys
import json 
import tempfile
import random
from time import sleep
from pymeasure.log import console_log
from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Procedure, Results
from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter, unique_filename

class RandomProcedure(Procedure):
    
    DATA_COLUMNS = ['Iteration', 'Random Number', 'dd']
    DATA_COLUMNS2 = []
    iterations = IntegerParameter('Loop Iterations')
    delay = FloatParameter('Delay Time', units='s', default=0.2)
    seed = Parameter('Random Seed', default='12345')
   
   
    @staticmethod
    def generate_columns():
        START = 0
        try:
            with open("json_data.json", "r") as file:
                num_iterations = json.load(file)
                file.close()
        except FileNotFoundError:
            num_iterations1 = {'iterations': 0}
            with open('json_data.json', 'w') as json_file:
                json.dump(num_iterations1, json_file)
                json_file.close()
            with open("json_data.json", "r") as file:
                num_iterations = json.load(file)
                file.close()
        DATA_COLUMNS2 = []
        DATA_COLUMNS2 = ['Iteration', 'Random Number', 'dd']
        for i in range(int(num_iterations['iterations'])):
            print(i)
            DATA_COLUMNS2.append('Iteration'+str(i))
            DATA_COLUMNS2.append('Random Number'+str(i))
            DATA_COLUMNS2.append('dd'+str(i))
        START = START + 1
        return DATA_COLUMNS2

    @staticmethod
    def delete_columns():
        DATA_COLUMNS2 = []


    def startup(self):
        log.info("Setting the seed of the random number generator")
        random.seed(self.seed)
        self.num_iterations = {'iterations': self.iterations}
        with open('json_data.json', 'w') as json_file:
            json.dump(self.num_iterations, json_file)
       
        

    def execute(self):
        log.info("Starting the loop of %d iterations" % self.iterations)
        for i in range(self.iterations):

            data = {
                'Iteration': i,
                'Random Number': random.random(),
                'dd': 'dd'
            }
            data2= {
                'Iteration2': 4,
                'Random Number2': random.random(),
                'dd2': 'tt'
            }
            self.emit('results', data)
            self.emit('results', data2)
            log.debug("Emitting results: %s" % data)
            self.emit('progress', 100 * i / self.iterations)
            sleep(self.delay)
            if self.should_stop():
                log.warning("Caught the stop flag in the procedure")
                break
        RandomProcedure.delete_columns()


class MainWindow(ManagedWindow):

     def __init__(self):
         super().__init__(
             procedure_class=RandomProcedure,
             inputs=['iterations', 'delay', 'seed'],
             displays=['iterations', 'delay', 'seed'],
             x_axis='Iteration',
             y_axis='Random Number',
             directory_input=True,                                # Added line, enables directory widget
         )
         self.setWindowTitle('GUI Example')
         self.directory = r'C:/Path/to/default/directory'         # Added line, sets default directory for GUI load

     def queue(self):
         directory = self.directory                               # Added line
         filename = unique_filename(directory)                    # Modified line

         procedure = self.make_procedure()
         results = Results(procedure, filename)
         experiment = self.new_experiment(results)

         self.manager.queue(experiment)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())