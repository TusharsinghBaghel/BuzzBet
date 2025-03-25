import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from birdwatch.models import UserLatentProfile, NewsPostLatentProfile, TrainingRun
from news.models import newsPost
from accounts.models import Profile
from birdwatch.models import PostInteraction, UserLatentProfile, NewsPostLatentProfile, TrainingRun
from birdwatch.biasedMatrixfactorization import BiasedMatrixFactorization

# Create your views here.

def train_model():
    users = list(Profile.objects.all())
    posts = list(newsPost.objects.all())
    if not users or not posts:
        print("No users or posts to train on.")
        return
    
    num_users = len(users)
    num_posts = len(posts)
    num_interactions = PostInteraction.objects.count()
    latentfactors = max(5, int(num_interactions ** 0.5))  # latent factor_size = max(5, sqrt(num_interactions))
    # took latent factor size dynamically based on number of interactions

    # Create mappings from object ID to index
    user_index = {user.id: idx for idx, user in enumerate(users)}
    post_index = {post.id: idx for idx, post in enumerate(posts)}

    training_data = []
    for interaction in PostInteraction.objects.all():
        uid = interaction.user.id
        pid = interaction.post.id
        if uid in user_index and pid in post_index:
            rating = interaction.validity
            training_data.append((user_index[uid], post_index[pid], rating))

    if not training_data:
        print("No training data available.")
        return
    
    # Convert training data to tensors
    user_indices = torch.LongTensor([d[0] for d in training_data])
    post_indices = torch.LongTensor([d[1] for d in training_data])
    ratings = torch.FloatTensor([d[2] for d in training_data])

    # Initialize the model of BiasedMatrixFactorization class
    model = BiasedMatrixFactorization(num_users, num_posts, num_factors=latentfactors, use_global_intercept=True)
    
    learning_rate = 0.005
    num_epochs = 1000
    lambda_i = 0.05 # Regularization parameter for intercepts is 5 times that of factors
    lambda_f = 0.01
    optimizer = optim.Adam(model.parameters(), lr=learning_rate) #adaptive learning rate
    mse_loss = nn.MSELoss() # Mean Squared Error loss

    #Training loop using gradient descent
    for epoch in range(num_epochs):
        model.train()
        optimizer.zero_grad()
        predictions = model(user_indices, post_indices)
        loss = mse_loss(predictions, ratings)
        reg_loss = (
            lambda_f * (model.user_factors.weight.norm(2)**2 + model.post_factors.weight.norm(2)**2)
            + lambda_i * (model.user_intercepts.weight.norm(2)**2 + model.post_intercepts.weight.norm(2)**2)
        ) # L2 regularization

        if model.global_intercept is not None:
            reg_loss += lambda_i * model.global_intercept.norm(2)**2

        total_loss = loss + reg_loss
        total_loss.backward()
        optimizer.step()
        print(f"Epoch {epoch+1}/{num_epochs}, Loss: {total_loss.item(): .4f}")


    for user in users:
        idx = user_index[user.id]
        latent_profile, _ = UserLatentProfile.objects.get_or_create(user=user)
        latent_profile.latent_factors = model.user_factors.weight.data[idx].numpy().tolist()
        latent_profile.intercept = model.user_intercepts.weight.data[idx].item()
        latent_profile.save()

    for post in posts:
        idx = post_index[post.id]
        latent_profile, _ = NewsPostLatentProfile.objects.get_or_create(post=post)
        latent_profile.latent_factors = model.post_factors.weight.data[idx].numpy().tolist()
        latent_profile.intercept = model.post_intercepts.weight.data[idx].item()
        latent_profile.save()


    # Save a TrainingRun entry to record global bias and hyperparameters
    global_bias = model.global_intercept.item() if model.global_intercept is not None else 0.0
    training_run = TrainingRun.objects.create(
        global_bias=global_bias,
        hyperparameters={
            'lambda_i': lambda_i,
            'lambda_f': lambda_f,
            'latent_dim': latentfactors,
            'epochs': num_epochs,
            'learning_rate': learning_rate
        }
    )
    
    print(f"Training complete. Global bias: {global_bias}")
    update_birdwatch_validity()
    return training_run


def update_birdwatch_validity():
    THRESHOLDF = 0.5 #for f_n
    THRESHOLDI = 0.4 #for b_n
    for post in newsPost.objects.all():
        try:
            latent_profile = NewsPostLatentProfile.objects.get(post=post)
        except NewsPostLatentProfile.DoesNotExist:
            print(f"No latent profile found for post {post.id}")
            continue

        intercept = latent_profile.intercept
        latent_vector = np.array(latent_profile.latent_factors)
        norm_f = np.linalg.norm(latent_vector)

        num_ratings = PostInteraction.objects.filter(post=post).count()
        if num_ratings < 5:
            post.birdwatch_validity = 0.5
        elif norm_f < THRESHOLDF and intercept > THRESHOLDI:
            post.birdwatch_validity = 1.0
        elif norm_f < THRESHOLDF and intercept < THRESHOLDI:
            post.birdwatch_validity = 0.0
        else:
            post.birdwatch_validity = 0.5
        
        post.save()
        print(f"Updated post {post.id} ({post.headline}) with birdwatch_validity: {post.birdwatch_validity}")

    print("Birdwatch validity update complete.")

