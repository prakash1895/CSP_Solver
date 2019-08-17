import numpy as np 
import matplotlib.pyplot as plt
import matplotlib

def plot_nqueens(cm, n, title="N-Queens"):
    classes = range(n)
    fig = plt.figure(figsize=(15,15))
    cm = cm[::-1, :]
    ax = fig.add_subplot(1, 1, 1)
    ax.matshow(cm, extent=[0, n, 0, n])
    
    ax.set(xticks=np.arange(cm.shape[1]),
           yticks=np.arange(cm.shape[0]),
           xticklabels=classes, yticklabels=classes,
           title=title)

    ax.title.set_size(40)
    ax.yaxis.label.set_size(40)
    ax.xaxis.label.set_size(40)
    ax.grid(linewidth=2)

    # apply offset transform to all x ticklabels.
    dx = 7.5/n ; dy = 0.0
    offset = matplotlib.transforms.ScaledTranslation(dx, dy, fig.dpi_scale_trans)
    for label in ax.xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)

    dx = 0.0 ; dy = -7.5/n
    offset = matplotlib.transforms.ScaledTranslation(dx, dy, fig.dpi_scale_trans)
    for label in ax.yaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)
    fig.tight_layout()
    plt.gca().invert_yaxis()
    # plt.savefig(title+".png")
    plt.show()
