
import torch
import torch.nn as nn

class BiasedMatrixFactorization(nn.Module):
    def __init__(self, num_users, num_posts, num_factors, use_global_intercept=True):
        super(BiasedMatrixFactorization, self).__init__()
        self.num_users = num_users
        self.num_posts = num_posts
        self.num_factors = num_factors #num of latent factors
        self.use_global_intercept = use_global_intercept #mu
        
        # Embeddings for latent factors
        self.user_factors = nn.Embedding(num_users, num_factors)
        self.post_factors = nn.Embedding(num_posts, num_factors)
        
        # Intercepts (biases) for users and posts
        self.user_intercepts = nn.Embedding(num_users, 1) #b_i
        self.post_intercepts = nn.Embedding(num_posts, 1) #b_f
        
        # Global bias (a single scalar)
        if self.use_global_intercept:
            self.global_intercept = nn.Parameter(torch.tensor([0.0], dtype=torch.float32))
        else:
            self.global_intercept = None
        
        self.reset_parameters()
    
    def reset_parameters(self):
        nn.init.normal_(self.user_factors.weight, std=0.1)
        nn.init.normal_(self.post_factors.weight, std=0.1)
        nn.init.constant_(self.user_intercepts.weight, 0.0)
        nn.init.constant_(self.post_intercepts.weight, 0.0)
    
    def forward(self, user_indices, post_indices):
        # Lookup embeddings and intercepts
        user_factor = self.user_factors(user_indices)
        post_factor = self.post_factors(post_indices)
        user_bias = self.user_intercepts(user_indices).squeeze()
        post_bias = self.post_intercepts(post_indices).squeeze()
        dot = (user_factor * post_factor).sum(dim=1)
        if self.use_global_intercept:
            return self.global_intercept + user_bias + post_bias + dot
        else:
            return user_bias + post_bias + dot
