import numpy as np
import torch
import os
import tqdm
from torch.utils.data import DataLoader
import time
import matplotlib.pyplot as plt
from scipy.io import wavfile

from dataset import InstrumentDataset
from model import DDSPDecoder
from utils import mss_loss, plot_stft_comparison
from synthesis import synthesize_additive


def do_training(dataset_path, output_path, device='cuda', ext='wav', sr=44100, hop_length=441,
                batch_size=16, num_epochs=100, samples_per_epoch=5000, reverb_len=44100):
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    data = InstrumentDataset(device, dataset_path, ext, sr, hop_length, samples_per_epoch=samples_per_epoch)

    ## Step 2: Create model with a test batch
    model = DDSPDecoder(mlp_depth=3, n_units=512, n_harmonics=50, n_bands=65,
                        hop_length=hop_length, sr=sr, reverb_len=reverb_len, data=data)
    model = model.to(device)

    ## Step 3: Setup the loss function
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    # Start at learning rate of 0.001, rate decay of 0.98 factor every 10,000 steps
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=int(10000/len(data)), gamma=0.98)

    # and we use this to update the parameters
    train_losses = []

    plt.figure(figsize=(12, 12))
    for epoch in range(num_epochs):
        tic = time.time()
        loader = DataLoader(data, batch_size=batch_size, shuffle=True)

        train_loss = 0
        for batch_num, (X, F, FConf, L) in tqdm.tqdm(enumerate(loader)): # Go through each mini batch
            # Move inputs/outputs to GPU
            X = X.to(device)
            F = F.to(device)
            FConf = FConf.to(device)
            L = L.to(device)
            # Reset the optimizer's gradients
            optimizer.zero_grad()
            # Run the model on all inputs
            A, C, P, reverb = model(F, FConf, L)
            # Run the synthesizer
            Y = synthesize_additive(A, C, F, P, hop_length, sr, reverb)
            # Compute the loss function comparing X to Y
            loss = mss_loss(X, Y)
            # Compute the gradients of the loss function with respect
            # to all of the parameters of the model
            loss.backward()
            # Update the parameters based on the gradient and
            # the optimization scheme
            optimizer.step()
            train_loss += loss.item()
        train_loss = train_loss/len(loader)
        train_losses.append(train_loss)
        scheduler.step()

        # Synthesize training data example
        x = X[0, :, 0].detach().cpu().numpy().flatten()
        y = Y[0, :, 0].detach().cpu().numpy().flatten()
        d = np.array([x, y])
        d = np.array(d*32768, dtype=np.int16)
        wavfile.write(f"{output_path}/Epoch{epoch}.wav", sr, d.T)

        plt.clf()
        plot_stft_comparison(F, L, X, Y, reverb, torch.tensor(train_losses))
        plt.tight_layout()
        plt.savefig(f"{output_path}/Epoch{epoch}.png", bbox_inches='tight')
        state = model.state_dict()
        state["loudness_mu"] = model.loudness_mu
        state["loudness_std"] = model.loudness_std
        torch.save(state, f"{output_path}/model.pkl")

        print("Epoch {}, loss {:.3f}, elapsed time {:.3f}".format(epoch, train_loss, time.time()-tic))