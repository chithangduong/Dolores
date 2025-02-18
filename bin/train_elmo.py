
import argparse
import pickle
import numpy as np

from bilm.training import train, load_options_latest_checkpoint, load_vocab
from bilm.data import BidirectionalLMDataset
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "1"


class MYDataset(object):
    def __init__(self, paths_repre_by_IDs):
        self.paths_repre_by_IDs = paths_repre_by_IDs
    def iter_batches(self, batch_size, num_steps):
        i = 0
        while i <= self.paths_repre_by_IDs.shape[0]:
            if (i + batch_size) > self.paths_repre_by_IDs.shape[0]:
                i = 0
            token_ids = np.zeros([batch_size, num_steps], np.int32)
            next_token_id = np.zeros([batch_size, num_steps], np.int32)
            token_ids_reverse = np.zeros([batch_size, num_steps], np.int32)
            next_token_id_reverse = np.zeros([batch_size, num_steps], np.int32)
            
            token_ids = self.paths_repre_by_IDs[i:i+batch_size,0:-1]    # [batch_size, num_steps] (model.token_ids)
            next_token_id[:,0:-1] = self.paths_repre_by_IDs[i:i+batch_size,2:]
            next_token_id[:,-1:] = np.full((batch_size,1), 14778)
            
            token_ids_reverse = np.flip(self.paths_repre_by_IDs[i:i+batch_size,1:],1)
            next_token_id_reverse[:,0:-1] = np.flip(self.paths_repre_by_IDs[i:i+batch_size,:-2],1)
            next_token_id_reverse[:,-1:] = np.full((batch_size,1), 14778)
            i += batch_size
            X = {'token_ids': token_ids,
                 'next_token_id': next_token_id,
                 'token_ids_reverse': token_ids_reverse,
                 'next_token_id_reverse': next_token_id_reverse}
            yield X

def main(args):
    file_input_20180713 = open("/u01/why/ucsb/node2vec/ID_together_walk_X_ids.txt",'rb')
    context_ids_large = pickle.load(file_input_20180713)
    #context_ids_large = context_ids_large[0:10,:]
    print(context_ids_large.shape)    # 145050,81
    # load the vocab
    #vocab = load_vocab(args.vocab_file, 50)

    # define the options
    batch_size = 256  # batch size for each GPU
    n_gpus = 1

    # number of tokens in training data
    n_train_tokens = context_ids_large.shape[0] * context_ids_large.shape[1]
    # 237+14541+1
    n_tokens_vocab = 14779
    

    options = {
     'bidirectional': True,
     'learning_rate': 0.01,
#     'char_cnn': {'activation': 'relu',
#      'embedding': {'dim': 16},
#      'filters': [[1, 32],
#       [2, 32],
#       [3, 64],
#       [4, 128],
#       [5, 256],
#       [6, 512],
#       [7, 1024]],
#      'max_characters_per_token': 50,
#      'n_characters': 261,
#      'n_highway': 2},
    
     'dropout': 0.1,
    
     'lstm': {
      'cell_clip': 3,
      'dim': 512,
      'n_layers': 4,
      'proj_clip': 3,
      'projection_dim': 32,
      'use_skip_connections': True},
    
     'all_clip_norm_val': 10.0,
    
     'n_epochs': 200,
     'n_train_tokens': n_train_tokens,
     'batch_size': batch_size,
     'n_tokens_vocab': n_tokens_vocab,
     'unroll_steps': 40,
     'n_negative_samples_batch': 8192,
    }

    #prefix = args.train_prefix
    #data = BidirectionalLMDataset(prefix, vocab, test=False,
    #                                  shuffle_on_load=True)
    data = MYDataset(context_ids_large)
    #data_gen = data.iter_batches(batch_size * n_gpus, 81)
    #for batch_no, batch in enumerate(data_gen, start = 1):
    #    X = batch
    #    print(batch_no, batch)
    
    save_dir = args.save_dir
    tf_save_dir = save_dir
    tf_log_dir = save_dir
    train(options, data, n_gpus, tf_save_dir, tf_log_dir)
          #, restart_ckpt_file = "/u01/why/ucsb/KG-embedding/20180804_lr0.03_dim32_layer_2/model7500.ckpt-7500")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--save_dir', help='Location of checkpoint files')
    #parser.add_argument('--vocab_file', help='Vocabulary file')
    #parser.add_argument('--train_prefix', help='Prefix for train files')

    args = parser.parse_args()
    main(args)
    #main()

