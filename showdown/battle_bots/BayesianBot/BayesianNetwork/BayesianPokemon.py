from pgmpy.models import BayesianModel
import matplotlib.pyplot as plt
import networkx as nx

custom_model = BayesianModel([('Pokemon HP', 'Choose'), ('Enemy HP', 'Choose'),
                              ('Pokemon Type', 'Choose'), ('Enemy Type', 'Choose'), ('Power', 'Choose'),
                              ('Category', 'Choose'), ('Weather', 'Choose')])
pos = {'Platform': [0.75, -0.5], 'Year': [1.25, -0.5],
       'Genre': [0.75, -1.], 'Developer': [1.25, -1],
       'Publisher': [1.25, -1.5],
       'Critic_Score': [1.5,  -2], 'User_Score': [1.75,  -2],
       'EU_Sales': [0.5, -2], 'NA_Sales': [0.75, -2], 'JP_Sales': [1, -2], 'Other_Sales': [1.25,  -2],
       'Global_Sales': [1, -2.5]}
fig, ax = plt.subplots(1, 1, figsize=(12, 12))
nx.draw_networkx(custom_model, pos=pos, ax=ax, node_size=5000)
ax.set_title('Custom model')
fig.savefig('custom_bn')