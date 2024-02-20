import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def make_corr_matrix(data_for_corr, sdq_subscales, facets_cols):
    

    corr_mat = data_for_corr.corr().loc[facets_cols, sdq_subscales].sort_values("tot", ascending=False)
    corr_mat.to_csv("data/output/corr_mat.csv", float_format='%.2f')

def make_scatter_plots(data, sdq_subscales, facets_cols):
    # Grouped scatter plots

    fig, axs = plt.subplots(len(facets_cols), len(sdq_subscales), figsize=(30, 100))  # 3 subplots side by side
    
    for i, facets_col in enumerate(facets_cols):
        for j, sdq_subscale in enumerate(sdq_subscales):
            axs[i, j].scatter(data[facets_col], data[sdq_subscale])
            axs[i, j].set_xlabel(facets_col)
            axs[i, j].set_ylabel(sdq_subscale)
    
    fig.subplots_adjust(hspace=0.4, wspace=0.4)
    axs = axs.flatten()

    # Set ylim
    for ax in axs:
        ax.set_xlim([0, 1.0])

    plt.tight_layout()

    #plt.tight_layout()
    plt.savefig("data/plots/scatter.png")

def plot_histograms_facets(data, facets_cols):
    # Distribution of each FACETS item
    fig, axs = plt.subplots(len(facets_cols), 1, figsize=(6, 150))  # 3 subplots side by side
    
    for i, facets_col in enumerate(facets_cols):
        counts, bins, _ = axs[i].hist(data[facets_col])
        axs[i].set_xlabel(facets_col)

        axs[i].set_xlim([0, 1])

        # Calculate mean and standard deviation
        mean = np.mean(data[facets_col])
        median = np.median(data[facets_col])
        std_dev = np.std(data[facets_col])

        # Plot lines for 1 and 2 standard deviations
        axs[i].axvline(mean, color='b', linestyle='--', label='Mean')
        axs[i].axvline(median, color='b', linestyle='-', label='Median')
        axs[i].axvline(mean - std_dev, color='y', linestyle='--', label='-1 SD')
        axs[i].axvline(mean + std_dev, color='y', linestyle='--', label='+1 SD')
        axs[i].axvline(mean - 2*std_dev, color='y', linestyle='--', label='-2 SD')
        axs[i].axvline(mean + 2*std_dev, color='y', linestyle='--', label='+2 SD')


    fig.subplots_adjust(hspace=0.4, wspace=0.4)
    axs = axs.flatten()

    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right')

    plt.tight_layout()

    #plt.tight_layout()
    plt.savefig("data/plots/facet_histograms.png")

if __name__ == "__main__":

    data = pd.read_csv("data/merged.csv", index_col=0)

    description = data.describe()
    description.to_csv("data/output/description.csv")

    data_for_corr = data.drop([
        "Entry ID", "Actor type", "Subject ID", "Hospital ID", "Group ID",
        "anonymised ID"
    ], axis=1)
    print(data_for_corr.columns)

    sdq_subscales = ["emotion", "conduct", "hyper", "peer",	"prosoc", "tot"]
    facets_cols = [x for x in data_for_corr.columns if "_" in x]
    sdq_item_cols = [x for x in data_for_corr.columns if x not in facets_cols and x not in sdq_subscales]
    
    make_corr_matrix(data_for_corr, sdq_subscales, facets_cols)
    make_scatter_plots(data, sdq_subscales, facets_cols)
    plot_histograms_facets(data_for_corr, facets_cols)

    cats = []
    for col in data.columns:
        if "_" in col:
            cat = col.split("_")[0]
            print(cat)
            cats.append(cat)
    cats = set(cats)
    print(cats)

    