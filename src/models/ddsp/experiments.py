from .train import do_training
from .evaluation import do_evaluation


def train_some_models():
    do_training('data/groove', 'models/ddsp/results/groove', device='cuda', ext='wav', sr=44100, hop_length=441,
                batch_size=16, num_epochs=50, samples_per_epoch=5000, reverb_len=44100)
    do_training('data/guitar', 'models/ddsp/results/guitar', device='cuda', ext='wav', sr=44100, hop_length=441,
                batch_size=16, num_epochs=50, samples_per_epoch=5000, reverb_len=44100)


def simple_experiment():
    do_training('data/IRMAS-TrainingData/sax', 'models/ddsp/results/sax_test', device='cuda', ext='wav', sr=44100, hop_length=441, batch_size=4, num_epochs=10, samples_per_epoch=100, reverb_len=44100)
    do_evaluation('models/ddsp/results/sax_test/model.pkl', 'data/IRMAS-TrainingData/pia/108__[pia][nod][cla]1386__1.wav', 'models/ddsp/results/sax_test/output/my_model_eval_output.wav')


train_some_models()
# simple_experiment()
