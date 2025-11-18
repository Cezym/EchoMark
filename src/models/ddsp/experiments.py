from train import do_training
from evaluation import do_evaluation


# do_training('../../data/violin', 'results/violin_test', device='cuda', ext='wav', sr=44100, hop_length=441, batch_size=8, num_epochs=25, samples_per_epoch=100, reverb_len=44100)
do_evaluation('results/violin_test/model.pkl', '../../data/examples/Korg-01W-A-Guitar-C3.wav', 'results/violin_test/output/my_model_eval_output.wav')
